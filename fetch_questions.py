import os
import json
import google.generativeai as genai
from datetime import datetime, timezone

# --- Initialize Gemini client ---
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# --- Load old questions (if available) ---
exclusions = []
if os.path.exists("questions.json"):
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            old_data = json.load(f)
            exclusions = [q["question"] for q in old_data.get("questions", [])]
    except Exception as e:
        print(f"⚠️ Could not load old questions: {e}")

# --- Build prompt ---
prompt = f"""
Generate 5 multiple-choice questions about chip design, digital IC design, and computer architecture. 
- Each question should have exactly 5 answer choices.
- Provide the correct answer clearly marked.
- Make sure questions vary in difficulty (easy to advanced).
- Most questions should be conceptual (not coding challenges).
- Correct answer can be any option between the 5 options provided.
- Do NOT repeat or closely paraphrase any of these previous questions:
{json.dumps(exclusions, indent=2)}

Format the output strictly as JSON in this structure:

{{
  "questions": [
    {{
      "question": "What does CMOS stand for?",
      "options": [
        "Complementary Metal-Oxide-Semiconductor",
        "Central Memory Operation System",
        "Current Mode Output Source",
        "Charged Metal Oxide Semiconductor",
        "Capacitor Mode Operating Signal"
      ],
      "correct": 0
    }}
  ]
}}
"""

# --- Call Gemini ---
response = genai.GenerativeModel("gemini-2.5-flash").generate_content(prompt)

content = response.text.strip()

# --- Clean Markdown fences if model wrapped in ```json ... ``` ---
if content.startswith("```"):
    first_newline = content.find("\n")
    if first_newline != -1:
        content = content[first_newline:].strip()
    else:
        content = content[3:].strip()
if content.endswith("```"):
    content = content[:-3].strip()

# --- Parse JSON ---
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    print("\n--- MODEL OUTPUT ---")
    print(content)
    print("--------------------\n")
    raise ValueError(f"Gemini returned invalid JSON. Error: {e}") from e

# --- Save to file ---
with open("questions.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Saved new questions.json at", datetime.now(timezone.utc).isoformat())
