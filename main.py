from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from helpers.season_analyzer import analyze_color_season
import os
from dotenv import load_dotenv
from openai import OpenAI
import colorsys
from typing import Dict, Any
from helpers.colora import nearest_color
from helpers.color_analysis import analyze_color
from pathlib import Path

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Set up static files and templates
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")



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
    
    
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/color")
async def get_color_details(hex_code: str):
    closest = nearest_color(hex_code)
    return closest
    analysis = analyze_color(closest["closest_hex"])

    return {
        "match": closest,
        "analysis": analysis
    }