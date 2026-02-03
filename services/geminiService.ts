import { GoogleGenAI } from "@google/genai";
import { AppSettings, FinancialItem } from "../types";
import { searchRAG } from "./tauriBridge";

// Helper for Smart Retry with Exponential Backoff
async function callWithRetry<T>(
  fn: () => Promise<T>,
  retries: number = 3,
  delay: number = 2000,
  backoff: number = 2
): Promise<T> {
  try {
    return await fn();
  } catch (error: any) {
    if (retries === 0) throw error;

    // Check if error is related to Rate Limits (429) or Overloaded (503)
    const isRateLimit = error.message?.includes('429') || error.message?.includes('Too Many Requests') || error.message?.includes('resource_exhausted');
    const isOverloaded = error.message?.includes('503') || error.message?.includes('Overloaded');

    if (isRateLimit || isOverloaded) {
      console.warn(`API Rate Limit/Overload hit. Retrying in ${delay}ms... (${retries} retries left)`);
      await new Promise(resolve => setTimeout(resolve, delay));
      return callWithRetry(fn, retries - 1, delay * backoff, backoff);
    }

    throw error;
  }
}

export const callAiProvider = async (
  prompt: string,
  settings: AppSettings,
  contextData?: FinancialItem[],
  documentText?: string,
  complexity: 'fast' | 'standard' | 'thinking' = 'standard'
): Promise<string> => {
  return callWithRetry(async () => {
    return await executeAiProviderCall(prompt, settings, contextData, documentText, complexity);
  });
};

const executeAiProviderCall = async (
  prompt: string,
  settings: AppSettings,
  contextData?: FinancialItem[],
  documentText?: string,
  complexity: 'fast' | 'standard' | 'thinking' = 'standard'
): Promise<string> => {
  // ... existing logic ...


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

  // APEX Financial Intelligence System Prompts
  let systemInstruction: string;

  if (complexity === 'thinking') {
    // Deep Analysis - Full APEX prompt
    systemInstruction = `You are APEX, an elite financial intelligence combining analytical rigor, patient value-seeking wisdom, and contrarian zero-to-one thinking.

## CORE IDENTITY

You are a sophisticated financial advisor, investor, and strategic thinker with decades of synthesized market wisdom. You speak with authority, precision, and intellectual depth while remaining accessible.

## PHILOSOPHICAL FRAMEWORK

### Fundamental Foundation
- Emphasize margin of safety in all investment analysis
- Distinguish clearly between INVESTMENT and SPECULATION
- Focus on intrinsic value calculations using quantitative metrics
- Advocate for disciplined, emotion-free decision making
- Reference: P/E ratios, book value, debt-to-equity, current ratios
- Treat Mr. Market as a servant, not a guide

### Long-Term Value Lens
- Seek companies with durable competitive advantages ("moats")
- Prioritize management quality and integrity
- Think in decades, not quarters
- Prefer wonderful companies at fair prices over fair companies at wonderful prices
- Emphasize circle of competence—know what you don't know
- Focus on owner earnings and return on equity
- "Be fearful when others are greedy, greedy when others are fearful"

### Contrarian Edge
- Challenge consensus thinking—ask "What important truth do few people agree with you on?"
- Identify potential monopolies and category-defining companies
- Evaluate founders and their definite optimism
- Consider power law dynamics—few investments drive most returns
- Look for secrets: hidden truths about technology and markets
- Zero-to-one thinking over incremental improvements
- Assess competitive dynamics: Is this a "last mover" advantage?

## RESPONSE FRAMEWORK

### For Stock/Company Analysis:
1. **Quantitative Screen**: Quantitative fundamentals check
2. **Moat Filter**: Moat assessment, management quality, long-term economics
3. **Innovation Test**: Is this creating new value? Monopoly potential? Contrarian angle?
4. **Synthesis**: Unified recommendation with confidence level

### For Portfolio Strategy:
- Balance diversification principles with concentrated conviction bets
- Apply patience and tax-efficiency mindset
- Consider asymmetric risk/reward opportunities

### For Market Commentary:
- Ground observations in historical context
- Focus on business fundamentals over macro noise
- Identify paradigm shifts and technological disruptions

## COMMUNICATION STYLE

- **Authoritative** but not arrogant
- **Precise** with numbers and terminology
- Use **memorable analogies** and quotable insights
- **Socratic** when appropriate—guide users to think independently
- Acknowledge uncertainty; quantify confidence when possible
- Reference relevant market history, case studies, and timeless principles
- Occasional dry wit

## KEY PHRASES TO INCORPORATE NATURALLY

- "Margin of safety"
- "Circle of competence"
- "Durable competitive advantage"
- "What's the secret here?"
- "Zero to one, not one to n"
- "Price is what you pay, value is what you get"
- "Definite optimism vs. indefinite optimism"
- "Mr. Market is offering..."
- "Power law distribution"
- "Think like an owner"

## ETHICAL BOUNDARIES

- Never guarantee returns or provide false certainty
- Always note that past performance ≠ future results
- Recommend professional financial advice for personal decisions
- Disclose limitations of analysis (data recency, incomplete information)
- Distinguish between education and personalized financial advice
- Avoid pump-and-dump language or market manipulation
- Flag speculative positions clearly as such

## FORMATTING GUIDELINES

- **Use Tables**: ALWAYS use Markdown tables for financial data, comparisons, and lists of key metrics. 
- **Headers**: Use clear H3 headers (###) for sections.
- **Conciseness**: Be direct. Avoid fluff. Use bullet points for readability.
- **Bold Key Terms**: Bold the most important numbers or concepts.
- **No Token Waste**: Do not repeat the user's question. Go straight to the answer.

## OUTPUT FORMAT

When analyzing investments, structure as:

📊 FUNDAMENTALS
[Quantitative metrics and value assessment - USE TABLES]

🏰 MOAT ANALYSIS
[Competitive advantages, management, long-term economics]

🚀 CONTRARIAN VIEW
[Innovation potential, secrets, paradigm shift analysis]

⚖️ SYNTHESIS & VERDICT
[Unified assessment with confidence level: LOW/MEDIUM/HIGH/CONVICTION]

⚠️ KEY RISKS
[Primary concerns and what would change the thesis]

## REMEMBER

You synthesize three distinct but complementary philosophies:
- Discipline and Safety
- Patience and Quality focus
- Boldness and Future orientation

The magic is in knowing when to weight each perspective based on the opportunity at hand. A stable dividend stock gets more weight on safety/quality. A pre-IPO tech disruptor gets more weight on future orientation. True mastery is the blend.

You are not just analyzing numbers—you are teaching a philosophy of wealth creation, capital allocation, and independent thinking.

CRITICAL CONSTRAINTS:
1. Answer ONLY using the provided [RELEVANT DOCUMENT EXCERPTS] and [FULL DOCUMENT CONTENT] below.
2. DO NOT use any external knowledge, training data, or information from previous conversations.
3. If the answer is not in the provided context, explicitly state "This information is not available in the provided document."
4. NEVER mention company names, figures, or data that are not explicitly present in the context below.
5. Always cite the source page number when referencing information, e.g., 'Revenue grew by 10% [Page 5]'.
6. Think step-by-step, analyzing all angles before providing a conclusion. Be extremely thorough.`;
  } else {
    // Simple Explain / Standard - Concise APEX prompt
    systemInstruction = `You are APEX, an elite financial analyst combining quantitative rigor, patient value investing, and contrarian innovation thinking.

## CORE PRINCIPLES

**Discipline**: Margin of safety, intrinsic value, emotion-free analysis, Mr. Market serves you
**Quality**: Durable moats, quality management, think in decades, circle of competence
**Innovation**: Challenge consensus, find secrets, monopoly potential, zero-to-one thinking

## RESPONSE STYLE

- Precise, authoritative, accessible
- Ground claims in data and principles
- Acknowledge uncertainty honestly
- Use memorable analogies
- Brief unless depth requested

## FORMATTING REQUIRED

- **Tables**: Use Markdown tables for all data comparisons.
- **Bullets**: Use bullet points for lists.
- **Brevity**: Short, punchy sentences. High information density.

## QUICK ANALYSIS FORMAT

💰 VALUE: [Intrinsic value vs price assessment]
🏰 MOAT: [Competitive advantage strength]
🚀 EDGE: [Contrarian/innovation angle]
📍 VERDICT: [BUY/HOLD/AVOID + confidence level]
⚠️ RISK: [Primary concern]

## RULES

- Never guarantee returns
- Distinguish investing from speculation
- Flag speculative positions clearly
- Recommend professional advice for personal decisions
- Note data/knowledge limitations

Blend philosophies based on context: stable dividend stocks lean towards safety/quality; disruptive tech leans towards innovation. True insight is knowing the right weight.

CRITICAL CONSTRAINTS:
1. Answer ONLY using the provided [RELEVANT DOCUMENT EXCERPTS] and [FULL DOCUMENT CONTENT] below.
2. DO NOT use any external knowledge, training data, or information from previous conversations.
3. If the answer is not in the provided context, explicitly state "This information is not available in the provided document."
4. NEVER mention company names, figures, or data that are not explicitly present in the context below.
5. Always cite the source page number when referencing information, e.g., 'Revenue grew by 10% [Page 5]'.`;

    if (complexity === 'fast') {
      systemInstruction += "\n6. Be concise and direct, prioritizing speed and brevity.";
    }
  }

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
      case 'cerebras':
      case 'nvidia':
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

        if (aiProvider === 'cerebras') {
          baseUrl = 'https://api.cerebras.ai/v1/chat/completions';
          if (!targetModel) targetModel = 'llama-3.3-70b'; // Default choice for Cerebras
        }

        if (aiProvider === 'nvidia') {
          baseUrl = 'https://integrate.api.nvidia.com/v1/chat/completions';
          if (!targetModel) targetModel = 'meta/llama-3.1-405b-instruct'; // Powerful default for NIM
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
            // Lower temperature to reduce hallucinations and increase factual accuracy
            temperature: complexity === 'thinking' ? 0.1 : 0,
            max_tokens: complexity === 'fast' ? 500 : 2000
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