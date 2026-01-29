from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal, AsyncGenerator
import asyncio
import json
import os
import httpx
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Local LLM Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama connection settings (loaded from env or defaults)
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost")
OLLAMA_PORT = int(os.environ.get("OLLAMA_PORT", "11434"))
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    images: Optional[List[str]] = None  # Base64 encoded images for vision models

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    stream: bool = True
    session_id: Optional[str] = "default"
    # Options override
    temperature: Optional[float] = None
    num_ctx: Optional[int] = None  # Context window
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    system: Optional[str] = None
    seed: Optional[int] = None
    num_predict: Optional[int] = None
    repeat_penalty: Optional[float] = None
    format: Optional[str] = None  # "json" or None

class ModelInfo(BaseModel):
    name: str
    model: str
    size: int  # bytes
    parameter_size: Optional[str] = None
    quantization_level: Optional[str] = None
    format: Optional[str] = None
    family: Optional[str] = None
    families: Optional[List[str]] = None
    modified_at: Optional[str] = None
    digest: Optional[str] = None

class PullRequest(BaseModel):
    model: str
    insecure: bool = False

class GenerateRequest(BaseModel):
    model: str
    prompt: str
    system: Optional[str] = None
    stream: bool = True
    options: Optional[Dict] = None

# In-memory session storage for chat history
session_histories: Dict[str, List[Dict]] = {}

@app.get("/health")
async def health_check():
    """Check if Ollama is accessible"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags", timeout=5.0)
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "ollama_url": OLLAMA_URL,
                    "bridge_status": "running"
                }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "message": "Ollama is not running or not accessible"
        }

@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List all available models from Ollama"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            if response.status_code != 200:
                raise HTTPException(502, f"Ollama error: {response.text}")
            
            data = response.json()
            models = []
            for model in data.get("models", []):
                models.append(ModelInfo(
                    name=model.get("name"),
                    model=model.get("model"),
                    size=model.get("size"),
                    parameter_size=model.get("details", {}).get("parameter_size"),
                    quantization_level=model.get("details", {}).get("quantization_level"),
                    format=model.get("details", {}).get("format"),
                    family=model.get("details", {}).get("family"),
                    families=model.get("details", {}).get("families"),
                    modified_at=model.get("modified_at"),
                    digest=model.get("digest")
                ))
            return models
    except httpx.ConnectError:
        raise HTTPException(503, "Cannot connect to Ollama. Is it running?")

@app.get("/models/detailed")
async def list_models_detailed():
    """
    Returns all available models with loaded status, VRAM usage, and expiration info.
    Shows which models are actively running in GPU/CPU memory.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Get all available models (downloaded)
            tags_resp = await client.get(f"{OLLAMA_URL}/api/tags")
            available = tags_resp.json().get("models", [])
            
            # Get currently running/loaded models with their resource usage
            ps_resp = await client.get(f"{OLLAMA_URL}/api/ps")
            running = ps_resp.json().get("models", [])
            
            # Index running models by name for quick lookup
            running_map = {
                m["name"]: {
                    "digest": m.get("digest"),
                    "details": m.get("details", {}),
                    "size": m.get("size"),  # Size in bytes (VRAM usage)
                    "size_vram": m.get("size_vram"),  # GPU VRAM specifically
                    "expires_at": m.get("expires_at"),  # When Ollama will unload it
                }
                for m in running
            }
            
            detailed_models = []
            for model in available:
                name = model["name"]
                is_loaded = name in running_map
                
                model_data = {
                    "name": name,
                    "model": model.get("model"),
                    "size": model.get("size"),  # Total file size
                    "parameter_size": model.get("details", {}).get("parameter_size"),
                    "quantization_level": model.get("details", {}).get("quantization_level"),
                    "format": model.get("details", {}).get("format"),
                    "family": model.get("details", {}).get("family"),
                    "loaded": is_loaded,
                    "loaded_at": None,
                    "expires_at": None,
                    "vram_usage": None,  # Human readable
                    "keep_loaded": False,
                }
                
                if is_loaded:
                    running_info = running_map[name]
                    model_data["loaded_at"] = running_info.get("details", {}).get("loaded_at")
                    model_data["expires_at"] = running_info.get("expires_at")
                    
                    # Calculate VRAM usage
                    if running_info.get("size_vram"):
                        vram_mb = running_info["size_vram"] / (1024 * 1024)
                        model_data["vram_usage"] = f"{vram_mb:.0f} MB"
                        model_data["vram_bytes"] = running_info["size_vram"]
                    elif running_info.get("size"):
                        size_mb = running_info["size"] / (1024 * 1024)
                        model_data["vram_usage"] = f"{size_mb:.0f} MB (estimated)"
                        
                    # Check if this model matches current keep_alive settings
                    # Note: Ollama doesn't expose this directly, we infer from expires_at
                    if model_data["expires_at"]:
                        # Parse expires_at to check if it's far in future (keep_loaded)
                        pass
                
                detailed_models.append(model_data)
            
            # Sort: loaded models first, then by name
            detailed_models.sort(key=lambda x: (not x["loaded"], x["name"]))
            return detailed_models
            
    except httpx.ConnectError:
        raise HTTPException(503, "Ollama not accessible")
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(500, str(e))

@app.post("/models/pull")
async def pull_model(request: PullRequest, background_tasks: BackgroundTasks):
    """Pull a new model from Ollama library"""
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/pull",
                json={
                    "name": request.model,
                    "insecure": request.insecure,
                    "stream": False  # We handle streaming separately if needed
                }
            )
            return {"status": "pulling", "model": request.model}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.delete("/models/{model_name}")
async def delete_model(model_name: str):
    """Delete a model"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{OLLAMA_URL}/api/delete",
                json={"name": model_name}
            )
            if response.status_code == 200:
                return {"status": "deleted", "model": model_name}
            else:
                raise HTTPException(400, response.text)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    """Non-streaming chat completion"""
    try:
        # Build options from request or defaults
        options = {
            "temperature": request.temperature or 0.7,
            "num_ctx": request.num_ctx or 4096,
        }
        
        if request.top_p is not None:
            options["top_p"] = request.top_p
        if request.top_k is not None:
            options["top_k"] = request.top_k
        if request.seed is not None:
            options["seed"] = request.seed
        if request.num_predict is not None:
            options["num_predict"] = request.num_predict
        if request.repeat_penalty is not None:
            options["repeat_penalty"] = request.repeat_penalty

        payload = {
            "model": request.model or os.environ.get("DEFAULT_MODEL", "llama3.2"),
            "messages": [m.dict() for m in request.messages],
            "stream": False,
            "options": options,
            "keep_alive": os.environ.get("KEEP_ALIVE", "5m")
        }
        
        if request.system:
            payload["system"] = request.system
        if request.format:
            payload["format"] = request.format

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload,
                timeout=300.0
            )
            
            result = response.json()
            
            # Store in session history
            if request.session_id:
                if request.session_id not in session_histories:
                    session_histories[request.session_id] = []
                session_histories[request.session_id].extend([
                    {"role": "user", "content": request.messages[-1].content},
                    {"role": "assistant", "content": result["message"]["content"]}
                ])
            
            return {
                "message": result["message"],
                "model": result.get("model"),
                "created_at": result.get("created_at"),
                "done": result.get("done"),
                "total_duration": result.get("total_duration"),
                "load_duration": result.get("load_duration"),
                "prompt_eval_count": result.get("prompt_eval_count"),
                "eval_count": result.get("eval_count"),
                "eval_duration": result.get("eval_duration"),
            }
            
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(500, str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat completion via SSE"""
    async def generate() -> AsyncGenerator[str, None]:
        try:
            options = {
                "temperature": request.temperature or 0.7,
                "num_ctx": request.num_ctx or 4096,
            }
            
            if request.top_p is not None:
                options["top_p"] = request.top_p
            if request.top_k is not None:
                options["top_k"] = request.top_k
            if request.seed is not None:
                options["seed"] = request.seed
            if request.num_predict is not None:
                options["num_predict"] = request.num_predict

            payload = {
                "model": request.model or os.environ.get("DEFAULT_MODEL", "llama3.2"),
                "messages": [m.dict() for m in request.messages],
                "stream": True,
                "options": options,
                "keep_alive": os.environ.get("KEEP_ALIVE", "5m")
            }
            
            if request.system:
                payload["system"] = request.system
            if request.format:
                payload["format"] = request.format

            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as response:
                    full_response = ""
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    chunk = data["message"]["content"]
                                    full_response += chunk
                                    yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
                                
                                if data.get("done"):
                                    # Send final stats
                                    yield f"data: {json.dumps({
                                        'done': True,
                                        'total_duration': data.get('total_duration'),
                                        'prompt_eval_count': data.get('prompt_eval_count'),
                                        'eval_count': data.get('eval_count')
                                    })}\n\n"
                                    
                                    # Save to history
                                    if request.session_id:
                                        if request.session_id not in session_histories:
                                            session_histories[request.session_id] = []
                                        session_histories[request.session_id].extend([
                                            {"role": "user", "content": request.messages[-1].content},
                                            {"role": "assistant", "content": full_response}
                                        ])
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/generate")
async def generate(request: GenerateRequest):
    """Raw completion (non-chat)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json=request.dict(),
                timeout=300.0
            )
            return response.json()
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/sessions/{session_id}/history")
async def get_history(session_id: str):
    return session_histories.get(session_id, [])

@app.delete("/sessions/{session_id}")
async def clear_history(session_id: str):
    if session_id in session_histories:
        del session_histories[session_id]
    return {"status": "cleared"}

@app.get("/version")
async def get_version():
    """Get Ollama version"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_URL}/api/version")
            return response.json()
    except:
        return {"error": "Cannot reach Ollama"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("BRIDGE_PORT", "1245"))
    uvicorn.run(app, host="127.0.0.1", port=port)
