import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client (no need to pass API key manually if env var is set)
client = OpenAI()

SEASON_CLASSIFICATION_PROMPT = """
You are a certified Personal Color Analyst specializing in the 12-season system.
You will receive detailed color analysis data for SKIN, EYES, and HAIR.

Each contains:
- temperature (Warm / Cool / Neutral)
- value (Very Light / Light / Medium / Dark / Very Dark)
- chroma (Bright / Muted / Soft)
- saturation (0–1)
- lightness (0–1)
- hue_degree (0–360)
- closest standard color name
- and overall contrast level (auto-calculated based on skin–hair–eye difference)

Your task:
Determine the most accurate **12-season color type**:
- Spring: Light Spring, Warm Spring, Bright Spring  
- Summer: Light Summer, Cool Summer, Soft Summer  
- Autumn: Soft Autumn, Warm Autumn, Dark Autumn  
- Winter: Bright Winter, Cool Winter, Dark Winter

Rules to consider:
- Skin undertone is the foundation (Warm vs Cool vs Neutral).
- Hair + eye depth define the value (Light / Deep seasons).
- Chroma defines if the person fits Bright / Clear vs Soft / Muted.
- Contrast between features defines placement into Bright/Winter or Soft/Summer/Autumn.
- Warm + Muted + Medium/Dark → usually Autumn
- Cool + Soft + Light → usually Summer
- Cool + High Contrast → Winter
- Warm + Light/Medium contrast → Spring

OUTPUT FORMAT (STRICT JSON):
{
  "season": "Exact season name",
  "dominant_trait": "Main reason: undertone / value / chroma / contrast",
  "reasoning": "Short explanation of why this season fits"
}

Here are the person's traits:
{traits}
"""
# async def analyze_color_season(traits: dict) -> dict:
#     """
#     traits: dict containing skin, eyes, hair (each with match + analysis)
#     """

#     try:
#         # ----------- DEBUG 1: Print the traits being sent -----------
#         print("\n🔍 DEBUG: Traits received by API:")
#         print(json.dumps(traits, indent=2))

#         prompt = SEASON_CLASSIFICATION_PROMPT.format(
#             traits=json.dumps(traits, indent=2)
#         )

#         # ----------- DEBUG 2: Print the final prompt -----------
#         print("\n🔍 DEBUG: Final prompt sent to LLM:")
#         print(prompt)

#         response = client.chat.completions.create(
#             model="gpt-4.1-mini", 
#             messages=[
#                 {"role": "system", "content": "You are an expert certified Personal Color Analyst."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.2,
#             max_tokens=350
#         )

#         # ----------- DEBUG 3: Print raw model response object -----------
#         print("\n🔍 DEBUG: Raw OpenAI API response:")
#         print(response)

#         # Extract message text
#         raw_output = response.choices[0].message.content

#         # ----------- DEBUG 4: Print the exact raw output -----------
#         print("\n🔍 DEBUG: Extracted model output:")
#         print(raw_output)

#         # No JSON parsing — simply return raw text safely
#         return {
#             "season_output_raw": raw_output
#         }

#     except Exception as e:
#         # ----------- DEBUG 5: Print the full error -----------
#         print("\n❌ DEBUG: Season analysis error:", str(e))

#         return {
#             "season": "Unknown",
#             "dominant_trait": "Unknown",
#             "reasoning": f"Failed due to error: {e}"
#         }

async def analyze_color_season(traits: dict) -> dict:
    try:
        print("\n===== ENTERING FUNCTION =====")

        print("\n🔍 DEBUG: Traits received by API:")
        print(json.dumps(traits, indent=2))

        prompt = SEASON_CLASSIFICATION_PROMPT.format(
            traits=json.dumps(traits, indent=2)
        )

        print("\n🔍 DEBUG: Final prompt:")
        print(prompt)

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert certified Personal Color Analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=350
        )

        print("\n🔍 DEBUG: Raw API response object:")
        print(response)

        raw = response.choices[0].message.content
        print("\n🔍 DEBUG: RAW MODEL OUTPUT (printing exactly):")
        print(repr(raw))  # repr shows hidden characters like "\n", "\t"

        print("\n===== END OF FUNCTION (returning raw text) =====")
        return {"raw_output": raw}

    except Exception as e:
        print("\n❌ CRITICAL DEBUG: Exception occurred")
        print("Exception type:", type(e))
        print("Exception details:", e)

        return {
            "error": "Season analysis failed",
            "details": str(e)
        }
