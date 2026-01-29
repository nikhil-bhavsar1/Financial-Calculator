import { GoogleGenAI } from "@google/genai";
import { AppSettings, FinancialItem } from "../types";
import { searchRAG } from "./tauriBridge";

export const callAiProvider = async (
  prompt: string,
  settings: AppSettings,
  contextData?: FinancialItem[],
  documentText?: string,
  complexity: 'fast' | 'standard' | 'thinking' = 'standard'
): Promise<string> => {

  const { aiProvider, apiKeys, modelName, llm } = settings;

  // Safe access to LLM settings with defaults
  const llmSettings = llm || {
    selected_model: '',
    context_window: 4096,
    temperature: 0.7
  };

  // Construct context string
  let contextBlock = "";

  // 1. RAG Retrieval (Dynamic Context)
  // For 'standard' and 'thinking' modes, we prioritize searched context over full text dump if configured
  // But for now, we will ADD it to the context.
  let ragChunks: { page: number; text: string; score: number }[] = [];
  try {
    if (documentText && documentText.length > 100) {
      ragChunks = await searchRAG(prompt);
    }
  } catch (e) {
    console.warn("RAG search skipped due to error:", e);
  }

  if (ragChunks.length > 0) {
    contextBlock += "\n[RELEVANT DOCUMENT EXCERPTS (RAG SEARCH RESULTS)]\n";
    ragChunks.forEach((chunk, i) => {
      contextBlock += `\n--- Excerpt ${i + 1} (Page ${chunk.page}) ---\n${chunk.text}\n`;
    });
    contextBlock += "\n[END EXCERPTS]\n";
  }

  // 2. Add Structured Data Context
  if (contextData && contextData.length > 0) {
    const dataSummary = contextData.map(item =>
      `${item.label}: Current=${item.currentYear}, Prev=${item.previousYear}, Var=${item.variationPercent}%`
    ).join('\n');
    contextBlock += `\n[EXTRACTED METRICS SUMMARY]\n${dataSummary}\n`;
  }

  // 3. Add Full Document Text Context (Truncated based on provider limits)
  if (documentText) {
    // Provider-specific limits to stay within token/TPM limits (e.g. Groq 12k TPM)
    // 1 char ~= 0.25-0.3 tokens. 
    // Groq: 15k chars (~4-5k tokens) is safe for 12k TPM limits.
    // Gemini/OpenAI/Other: 100k chars is fine for their much larger contexts.
    const maxChars = settings.aiProvider === 'groq' ? 15000 : 100000;

    const cleanText = documentText.slice(0, maxChars);
    if (ragChunks.length === 0) {
      contextBlock += `\n[DOCUMENT TEXT SNIPPET (First ${maxChars} chars)]\n${cleanText}\n[END SNIPPET]\n`;
    } else {
      // If RAG active, maybe provide less full text or rely on RAG? 
      // User requested "NotebookLM like", which often uses FULL context.
      // We will keep full context but prioritize RAG excerpts in instruction.
      contextBlock += `\n[FULL DOCUMENT CONTENT START]\n${cleanText}\n[FULL DOCUMENT CONTENT END]\n`;
    }
  }

  // Enhanced system prompt
  let systemInstruction = "You are an expert financial analyst assistant. Use the provided [RELEVANT DOCUMENT EXCERPTS] and [FULL DOCUMENT CONTENT] to answer.";
  if (complexity === 'thinking') {
    systemInstruction += " You must think step-by-step, analyzing all angles before providing a conclusion. Be extremely thorough.";
  } else if (complexity === 'fast') {
    systemInstruction += " Be concise and direct. prioritized speed and brevity.";
  }

  systemInstruction += "\nCRITICAL: Always cite the source page number when referencing information from the document, e.g., 'Revenue grew by 10% [Page 5]'.";

  const fullPrompt = `
    ${systemInstruction}
    
    CONTEXT:
    ${contextBlock}
    
    USER REQUEST: 
    ${prompt}

    INSTRUCTIONS:
    - Answer based strictly on the provided Context.
    - If the user asks where to find something, provide specific section names or text snippets from the document.
    - CITE SOURCES using [Page X] format.
  `;

  try {
    switch (aiProvider) {
      case 'gemini':
        const geminiKey = apiKeys.gemini || process.env.API_KEY;
        if (!geminiKey) return "Please configure the Gemini API key in Settings.";

        const ai = new GoogleGenAI({
          apiKey: geminiKey,
          // Force v1 API to avoid v1beta 404 for gemini-1.5-flash
          //@ts-ignore - Some versions of the SDK might not have this in types but support it in options
          apiVersion: 'v1'
        });

        // Default to selection, fallback to standard
        let model = modelName || 'gemini-1.5-flash';

        // Complexity overrides:
        // 'thinking' always forces the thinking model regardless of base selection
        // 'fast' forces flash if no selection or if selection is a 'pro' model
        if (complexity === 'thinking') {
          model = 'gemini-2.0-flash-thinking-exp-1219';
        } else if (complexity === 'fast' && (!modelName || modelName.includes('pro'))) {
          model = 'gemini-1.5-flash';
        }

        let config: any = {};

        const response = await ai.models.generateContent({
          model: model,
          contents: fullPrompt,
          config: config
        });
        return response.text || "No response generated.";

      case 'groq':
      case 'openai':
      case 'openrouter':
      case 'opencode':
        const apiKey = apiKeys[aiProvider];
        if (!apiKey) {
          return `Please configure the API key for ${aiProvider.toUpperCase()} in Settings.`;
        }

        let baseUrl = 'https://api.openai.com/v1/chat/completions';
        let targetModel = modelName;

        if (aiProvider === 'groq') {
          baseUrl = 'https://api.groq.com/openai/v1/chat/completions';
          if (!targetModel) {
            // Groq Model Selection based on Complexity
            if (complexity === 'fast') targetModel = 'llama-3.1-8b-instant';
            else targetModel = 'llama-3.3-70b-versatile';
          }
        }

        if (aiProvider === 'openrouter') {
          baseUrl = 'https://openrouter.ai/api/v1/chat/completions';
          // OpenRouter fallback defaults
          if (!targetModel) targetModel = 'meta-llama/llama-3-70b-instruct';
        }

        if (aiProvider === 'openai') {
          if (!targetModel) {
            // OpenAI Model Selection
            if (complexity === 'fast') targetModel = 'gpt-3.5-turbo';
            else targetModel = 'gpt-4-turbo';
          }
        }

        if (aiProvider === 'opencode') {
          baseUrl = 'https://api.opencode.com/v1/chat/completions';
          if (!targetModel) targetModel = 'default-model';
        }

        const completionReq = await fetch(baseUrl, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
            ...(aiProvider === 'openrouter' && { 'HTTP-Referer': window.location.origin })
          },
          body: JSON.stringify({
            model: targetModel,
            messages: [{ role: 'user', content: fullPrompt }],
            // Add temperature control for fast/thinking modes
            temperature: complexity === 'fast' ? 0.3 : 0.7
          })
        });

        if (!completionReq.ok) {
          const err = await completionReq.json();
          throw new Error(err.error?.message || 'API Request Failed');
        }

        const data = await completionReq.json();
        return data.choices?.[0]?.message?.content || "No response content.";

      case 'local_llm':
        try {
          const { invoke } = await import('@tauri-apps/api/core');
          const result = await invoke('generate_completion', {
            prompt: fullPrompt,
            model: llmSettings.selected_model,
            context: [] // We can implement conversation history later if needed
          });
          // The rust command returns the full string or dict? Assuming string based on command name
          // If it returns { response: string }, we need to parse it. 
          // Checking backend signature: returns String.
          return result as string;
        } catch (e: any) {
          console.error("Local LLM Invoke Error:", e);
          return `Local LLM Error: ${e.message || e}`;
        }

      default:
        return "Unsupported AI Provider.";
    }
  } catch (error: any) {
    console.error("AI Service Error:", error);
    return `Error calling ${aiProvider}: ${error.message}`;
  }
};