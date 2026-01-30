import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from helpers.color_analysis import analyze_color as analyze_color_util

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

def clean_hex_value(hex_str):
    """Remove any non-hex characters from the hex string."""
    if not hex_str:
        return ""
    # Remove any non-hex characters (like ^) and ensure it starts with #
    clean = ''.join(c.lower() for c in hex_str if c.lower() in '0123456789abcdef')
    return f"#{clean}" if clean else ""

async def analyze_color_season(traits: dict) -> dict:
    print("\n===== ENTERING analyze_color_season =====")
    print("Raw input traits:", json.dumps(traits, indent=2))
    
    try:
        # Clean and validate the input data
        cleaned_traits = {}
        required_traits = ['skin', 'eyes', 'hair']
        
        # Check for missing required traits
        missing_traits = [t for t in required_traits if t not in traits]
        if missing_traits:
            error_msg = f"Missing required traits: {', '.join(missing_traits)}"
            print(f"❌ {error_msg}")
            return {
                "error": "Incomplete data",
                "details": error_msg,
                "required_traits": required_traits,
                "received_traits": list(traits.keys())
            }
            
        for trait_type in required_traits:
            try:
                trait_data = traits[trait_type].copy()
                print(f"\n🔍 Processing {trait_type} trait:")
                print("Raw trait data:", json.dumps(trait_data, indent=2))
                
                # Ensure we have the required structure
                if 'match' not in trait_data:
                    trait_data['match'] = {}
                if 'analysis' not in trait_data:
                    trait_data['analysis'] = {}
                
                # Clean hex values in match
                if 'hex' in trait_data['match']:
                    original_hex = trait_data['match']['hex']
                    cleaned_hex = clean_hex_value(original_hex)
                    print(f"  - Cleaned hex: {original_hex} -> {cleaned_hex}")
                    trait_data['match']['hex'] = cleaned_hex
                
                # Clean hex values in analysis
                for key in ['input_hex', 'closest_hex']:
                    if key in trait_data['analysis']:
                        original_hex = trait_data['analysis'][key]
                        cleaned_hex = clean_hex_value(original_hex)
                        print(f"  - Cleaned {key}: {original_hex} -> {cleaned_hex}")
                        trait_data['analysis'][key] = cleaned_hex
                
                cleaned_traits[trait_type] = trait_data
                print(f"✅ Processed {trait_type} trait")
                
            except Exception as e:
                error_msg = f"Error processing {trait_type}: {str(e)}"
                print(f"❌ {error_msg}")
                return {
                    "error": f"Invalid {trait_type} data",
                    "details": error_msg,
                    "trait_data": trait_data
                }

        print("\n🔍 DEBUG: Cleaned traits for analysis:")
        print(json.dumps(cleaned_traits, indent=2))

        # Prepare traits for the prompt with validation
        prompt_traits = {}
        
        print("\n🔍 Preparing traits for analysis:")
        for trait_type in ['skin', 'eyes', 'hair']:
            try:
                trait_data = cleaned_traits[trait_type]
                analysis = trait_data.get('analysis', {})
                
                # Get the hex value for analysis
                hex_value = trait_data.get('match', {}).get('hex', '')
                if not hex_value:
                    print(f"⚠️ Missing hex value for {trait_type}")
                    continue
                
                # Perform color analysis if we don't have the required fields
                required_fields = ['hue_degree', 'lightness', 'saturation', 'temperature', 'value', 'chroma']
                if not all(k in analysis for k in required_fields):
                    print(f"🔍 Running color analysis for {trait_type} ({hex_value})")
                    try:
                        color_analysis = analyze_color_util(hex_value)
                        if color_analysis:
                            analysis.update(color_analysis)
                            print(f"✅ Color analysis results for {trait_type}:")
                            for k, v in color_analysis.items():
                                print(f"   - {k}: {v}")
                        else:
                            print(f"⚠️ No analysis results for {trait_type}")
                    except Exception as e:
                        print(f"⚠️ Error analyzing color for {trait_type}: {str(e)}")
                
                # Prepare trait data with actual or default values
                trait_info = {
                    'hex': hex_value,
                    'closest_name': analysis.get('closest_name', 'Unknown'),
                    'temperature': analysis.get('temperature', 'Neutral'),
                    'value': analysis.get('value', 'Medium'),
                    'chroma': analysis.get('chroma', 'Medium'),
                    'hue_degree': float(analysis.get('hue_degree', 0)),
                    'lightness': float(analysis.get('lightness', 0.5)),
                    'saturation': float(analysis.get('saturation', 0.5))
                }
                
                print(f"✅ Prepared {trait_type} data:", json.dumps(trait_info, indent=2))
                prompt_traits[trait_type] = trait_info
                
            except Exception as e:
                error_msg = f"Error preparing {trait_type} data: {str(e)}"
                print(f"❌ {error_msg}")
                return {
                    "error": f"Invalid {trait_type} analysis",
                    "details": error_msg,
                    "trait_data": trait_data,
                    "analysis_data": analysis
                }

        # Prepare the final prompt with validation
        try:
            traits_json = json.dumps(prompt_traits, indent=2)
            prompt = SEASON_CLASSIFICATION_PROMPT.format(traits=traits_json)
            
            print("\n🔍 Final prompt to LLM:")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
            
        except Exception as e:
            error_msg = f"Error creating prompt: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "error": "Failed to prepare analysis",
                "details": error_msg,
                "prompt_traits": prompt_traits
            }

        try:
            print("\n🔄 Sending request to OpenAI...")
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are an expert certified Personal Color Analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=350
            )
            
            print("\n✅ Received response from OpenAI")
            
            # Extract the raw content safely
            try:
                raw = response.choices[0].message.content
                print("\n🔍 Raw model output:")
                print("-" * 50)
                print(raw)
                print("-" * 50)
                
                # Try to parse the JSON response
                try:
                    # Look for JSON in the response
                    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group(0))
                        print("✅ Successfully parsed JSON response:")
                        print(json.dumps(parsed, indent=2))
                        return {
                            "status": "success",
                            "season_analysis": parsed
                        }
                except json.JSONDecodeError as je:
                    print(f"⚠️ Could not parse JSON response: {je}")
                
                # If we get here, return the raw output for fallback processing
                return {
                    "status": "partial_success",
                    "raw_output": raw
                }
                
            except (IndexError, AttributeError) as e:
                error_msg = f"Unexpected response format: {str(e)}"
                print(f"❌ {error_msg}")
                print("Full response:", response)
                return {
                    "error": "Invalid response from analysis service",
                    "details": error_msg,
                    "response": str(response)
                }
                
        except Exception as e:
            error_msg = f"Error calling OpenAI API: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "error": "Analysis service unavailable",
                "details": error_msg
            }

    except Exception as e:
        import traceback
        error_type = type(e).__name__
        error_trace = traceback.format_exc()
        
        print("\n❌ CRITICAL ERROR")
        print("-" * 50)
        print(f"Error Type: {error_type}")
        print(f"Error Message: {str(e)}")
        print("\nStack Trace:")
        print(error_trace)
        print("-" * 50)
        
        return {
            "error": "Season analysis failed due to an internal error",
            "error_type": error_type,
            "details": str(e),
            "traceback": error_trace.split('\n')
        }
