# core/ai_utils.py
#Handles API selection, loading keys, and LLM initialization.
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_llm_client(api_choice="Gemini"):
    """Initialize and return LLM client based on user choice."""
    if api_choice == "Gemini":
        if not GEMINI_API_KEY:
            raise ValueError("❌ Missing Gemini API Key in .env")
        genai.configure(api_key=GEMINI_API_KEY)
        return genai, "Gemini"
    else:
        raise ValueError("Invalid API choice. Use 'Gemini'.")

print("\n🔑 Gemini key loaded:", bool(os.getenv("GEMINI_API_KEY")))
print(os.getenv("GEMINI_API_KEY"))

# Visuals instruction for LLM prompts
def get_visuals_instruction() -> str:
    """
    Return LLM instructions for optionally including text-based visuals.
    Safe to append to any mode's prompt; the model decides based on content relevance.
    """
    return """
**Optional: Include Visuals if Helpful**
- Only add visuals if they genuinely aid understanding (comparisons, processes, hierarchies).
- Choose ONE of:
  1. **Markdown Table**: For comparisons, feature lists, step summaries. Keep it compact (max 5-6 rows).
     Example: | Concept | Definition | Use Case |
  2. **Numbered/Bulleted Flow**: For step-by-step processes, state transitions. Number each step (1→2→3...).
     Example: 1. Input data → 2. Process → 3. Output
  3. **Mermaid Diagram (text)**: For hierarchies, flowcharts, relationships. Wrap in triple backticks with "mermaid" label.
     Example:
     ```mermaid
     flowchart TD
       A[Start] --> B[Decision]
       B -->|Yes| C[Action 1]
       B -->|No| D[Action 2]
     ```
- Keep all visuals **small, text-only, and exam-friendly**. Avoid unnecessary detail.
- Visuals should enhance clarity, not clutter the response.
"""