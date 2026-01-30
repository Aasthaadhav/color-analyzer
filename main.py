from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# from helpers.profile_builder import build_profile
from helpers.season_analyzer import analyze_color_season
import os
from dotenv import load_dotenv
from openai import OpenAI
import colorsys
from typing import Dict, Any
from helpers.colora import nearest_color  # we will create this module below
from helpers.color_analysis import analyze_color
load_dotenv()  
app = FastAPI()



# -------------------------
# Request Body Model
# -------------------------

class ColorSet(BaseModel):
    match: Dict[str, Any]
    analysis: Dict[str, Any]

class SeasonRequest(BaseModel):
    skin: ColorSet
    eyes: ColorSet
    hair: ColorSet


# -------------------------
# API Endpoint
# -------------------------

@app.post("/analyze-color-season")
async def analyze_color_season_api(data: SeasonRequest):
    try:
        # Convert Pydantic model → pure dict
        traits = {
            "skin": data.skin.dict(),
            "eyes": data.eyes.dict(),
            "hair": data.hair.dict()
        }

        # Call OpenAI-based analyzer
        season_result = await analyze_color_season(traits)

        return {
            "status": "success",
            "traits_received": traits,
            "season_analysis": season_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/color")
def get_color_details(hex_code: str):
    closest = nearest_color(hex_code)
    analysis = analyze_color(closest["closest_hex"])

    return {
        "match": closest,
        "analysis": analysis
    }