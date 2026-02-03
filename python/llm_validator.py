"""
Phase 4: LLM Validation Layer.

Integrates with Ollama/LLM for:
- Extraction consistency validation
- Unstructured notes extraction (MD&A, commitments)
- Segment reporting extraction
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Check for Ollama availability
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class LLMValidationResult:
    """Result of LLM validation check."""
    is_valid: bool
    confidence: float
    issues: List[str]
    suggestions: List[str]
    raw_response: str

@dataclass
class ExtractedNarrative:
    """Extracted information from narrative text."""
    section_type: str  # 'mda', 'commitments', 'contingencies', 'segment'
    content: str
    key_points: List[str]
    metrics_mentioned: Dict[str, Any]

# =============================================================================
# LLM Integration
# =============================================================================

class OllamaClient:
    """Client for Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
    
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response from Ollama."""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                },
                timeout=60
            )
            
            if response.ok:
                return response.json().get('response', '')
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            return response.ok
        except:
            return False

# =============================================================================
# Extraction Validator (Phase 4.1)
# =============================================================================

class LLMExtractionValidator:
    """
    Uses LLM to validate consistency of extracted financial data.
    """
    
    VALIDATION_SYSTEM_PROMPT = """You are Benjamin Graham's student and Warren Buffet's student with the utmost knowledge of finance. 
Your expert job is to check if extracted financial data is consistent and reasonable.
Look for:
1. Mathematical consistency (totals should match sum of components)
2. Sign conventions (assets positive, expenses positive in P&L)
3. Reasonable magnitudes (no obvious data entry errors)
4. Missing critical items (every balance sheet needs assets, liabilities, equity)

Respond in JSON format:
{
  "is_valid": true/false,
  "confidence": 0.0-1.0,
  "issues": ["list of issues found"],
  "suggestions": ["list of suggestions"]
}"""
    
    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or OllamaClient()
    
    def validate_extraction(
        self,
        metrics: Dict[str, float],
        statement_type: str = "balance_sheet"
    ) -> LLMValidationResult:
        """
        Validate extracted metrics using LLM.
        """
        # Format metrics for LLM
        metrics_text = "\n".join([
            f"- {key}: {value:,.2f}"
            for key, value in sorted(metrics.items())
        ])
        
        prompt = f"""Validate this extracted {statement_type} data:

{metrics_text}

Check for:
1. Are totals consistent with components?
2. Are there obvious sign errors?
3. Are any critical items missing?
4. Do the magnitudes seem reasonable?

Respond in JSON format."""
        
        response = self.client.generate(prompt, self.VALIDATION_SYSTEM_PROMPT)
        
        # Parse response
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return LLMValidationResult(
                    is_valid=result.get('is_valid', True),
                    confidence=result.get('confidence', 0.5),
                    issues=result.get('issues', []),
                    suggestions=result.get('suggestions', []),
                    raw_response=response
                )
        except json.JSONDecodeError:
            pass
        
        # Fallback: Simple heuristic validation
        return self._fallback_validation(metrics)
    
    def _fallback_validation(self, metrics: Dict[str, float]) -> LLMValidationResult:
        """Fallback validation when LLM is unavailable."""
        issues = []
        
        # Check balance sheet equation
        assets = metrics.get('total_assets', 0)
        liab = metrics.get('total_liabilities', 0)
        equity = metrics.get('total_equity', 0)
        
        if assets and (liab or equity):
            if abs(assets - (liab + equity)) > abs(assets) * 0.05:
                issues.append("Balance sheet equation mismatch > 5%")
        
        # Check for critical items
        if not assets and not liab:
            issues.append("Missing critical balance sheet items")
        
        return LLMValidationResult(
            is_valid=len(issues) == 0,
            confidence=0.7,
            issues=issues,
            suggestions=["Manual review recommended"],
            raw_response="Fallback validation (LLM unavailable)"
        )

# =============================================================================
# Narrative Extractor (Phase 4.2)
# =============================================================================

class NarrativeExtractor:
    """
    Extracts structured information from unstructured narrative text.
    Targets: MD&A, Commitments, Contingencies, Segment Reporting.
    """
    
    MDA_SYSTEM_PROMPT = """You are Benjamin Graham's student and Warren Buffet's student with the utmost knowledge of finance, extracting key information from Management Discussion & Analysis (MD&A).
Extract:
1. Key business highlights
2. Revenue drivers mentioned
3. Cost/margin commentary
4. Future outlook/guidance
5. Any specific metrics or targets mentioned

Respond in JSON format:
{
  "key_points": ["point1", "point2"],
  "revenue_drivers": ["driver1"],
  "outlook": "summary",
  "metrics_mentioned": {"metric_name": "value"}
}"""
    
    COMMITMENT_SYSTEM_PROMPT = """You are extracting commitment and contingency information from financial statements.
Extract:
1. Capital commitments
2. Operating lease commitments
3. Purchase obligations
4. Contingent liabilities
5. Guarantees

Respond in JSON format:
{
  "capital_commitments": "amount or description",
  "lease_commitments": "amount or description",
  "contingent_liabilities": ["list"],
  "total_commitments": "amount if stated"
}"""
    
    SEGMENT_SYSTEM_PROMPT = """You are extracting segment reporting information.
Extract for each segment:
1. Segment name
2. Revenue
3. Operating profit/EBIT
4. Assets (if provided)

Respond in JSON format:
{
  "segments": [
    {"name": "Segment A", "revenue": 1000, "operating_profit": 100},
    {"name": "Segment B", "revenue": 2000, "operating_profit": 200}
  ]
}"""
    
    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or OllamaClient()
    
    def extract_mda(self, text: str) -> ExtractedNarrative:
        """Extract key information from MD&A section."""
        prompt = f"""Extract key information from this MD&A text:

{text[:4000]}

Focus on business highlights, drivers, and forward-looking statements."""
        
        response = self.client.generate(prompt, self.MDA_SYSTEM_PROMPT)
        return self._parse_narrative_response(response, 'mda', text)
    
    def extract_commitments(self, text: str) -> ExtractedNarrative:
        """Extract commitments and contingencies."""
        prompt = f"""Extract commitments and contingencies from:

{text[:4000]}

List all financial commitments and potential liabilities."""
        
        response = self.client.generate(prompt, self.COMMITMENT_SYSTEM_PROMPT)
        return self._parse_narrative_response(response, 'commitments', text)
    
    def extract_segments(self, text: str) -> ExtractedNarrative:
        """Extract segment reporting data."""
        prompt = f"""Extract segment information from:

{text[:4000]}

Capture revenue and profit by segment."""
        
        response = self.client.generate(prompt, self.SEGMENT_SYSTEM_PROMPT)
        return self._parse_narrative_response(response, 'segment', text)
    
    def _parse_narrative_response(
        self,
        response: str,
        section_type: str,
        original_text: str
    ) -> ExtractedNarrative:
        """Parse LLM response into ExtractedNarrative."""
        key_points = []
        metrics = {}
        
        try:
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                key_points = data.get('key_points', [])
                metrics = data.get('metrics_mentioned', {})
        except:
            pass
        
        return ExtractedNarrative(
            section_type=section_type,
            content=original_text[:1000],
            key_points=key_points,
            metrics_mentioned=metrics
        )

# =============================================================================
# Unified LLM Validator Interface
# =============================================================================

class LLMValidator:
    """
    Unified interface for LLM-based validation and extraction.
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama2"):
        self.client = OllamaClient(ollama_url, model)
        self.extraction_validator = LLMExtractionValidator(self.client)
        self.narrative_extractor = NarrativeExtractor(self.client)
    
    def is_available(self) -> bool:
        """Check if LLM service is available."""
        return self.client and self.client.is_available()
    
    def validate_metrics(
        self,
        metrics: Dict[str, float],
        statement_type: str = "balance_sheet"
    ) -> LLMValidationResult:
        """Validate extracted metrics for consistency."""
        if not self.is_available():
            # Use heuristic fallback when LLM is offline
            return self.extraction_validator._fallback_validation(metrics)
            
        return self.extraction_validator.validate_extraction(metrics, statement_type)
    
    def extract_mda(self, text: str) -> ExtractedNarrative:
        """Extract key points from MD&A."""
        return self.narrative_extractor.extract_mda(text)
    
    def extract_commitments(self, text: str) -> ExtractedNarrative:
        """Extract commitments and contingencies."""
        return self.narrative_extractor.extract_commitments(text)
    
    def extract_segments(self, text: str) -> ExtractedNarrative:
        """Extract segment reporting data."""
        return self.narrative_extractor.extract_segments(text)


if __name__ == "__main__":
    print("LLM Validator loaded")
    
    # Test availability
    validator = LLMValidator()
    print(f"Ollama available: {validator.is_available()}")
    
    # Test fallback validation
    test_metrics = {
        'total_assets': 1000000,
        'total_liabilities': 600000,
        'total_equity': 400000,
    }
    result = validator.validate_metrics(test_metrics)
    print(f"Validation result: valid={result.is_valid}, confidence={result.confidence}")
