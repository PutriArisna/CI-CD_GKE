# app/main.py
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

class BodyMeasurements(BaseModel):
    bust: float
    waist: float
    hips: float
    high_hip: float

body_type_to_query = {
    "hourglass": "wrap dress, v-neck top, pencil skirt, bodycon dress, tailored jumpsuit",
    "bottom hourglass": "fit and flare dress, belted pants, high-rise jeans, structured tops, empire waist dress",
    "top hourglass": "fitted tops, high-waisted jeans, flared skirts, scoop-neck tops, bodycon dresses",
    "spoon": "fit and flare dress, A-line skirt, embellished tops, structured jackets, ruffled blouses",
    "triangle": "off-shoulder top, a-line skirt, boat-neck tops, wide-leg trousers, patterned tops",
    "inverted triangle": "a-line skirt, wide-leg pants, v-necklines, peplum tops, flowy blouses",
    "rectangle": "peplum top, belted jacket, layered outfits, ruffled skirts, ruched dresses"
}

def classify_body_type(bust: float, waist: float, hips: float, high_hip: float) -> str:
    bust_hips = bust - hips
    hips_bust = hips - bust
    hips_waist = hips - waist
    bust_waist = bust - waist
    high_hip_waist = high_hip / waist if waist != 0 else 0

    if abs(bust_hips) <= 2.54 and hips_bust < 9.14 and bust_waist >= 22.86 or hips_waist >= 25.4:
        return "hourglass"
    elif hips_bust >= 9.14 and hips_bust < 25.4 and hips_waist >= 22.86 and high_hip_waist < 1.193:
        return "bottom hourglass"
    elif bust_hips > 2.54 and bust_hips < 25.4 and bust_waist >= 22.86:
        return "top hourglass"
    elif hips_bust > 5.08 and hips_waist >= 17.78 and high_hip_waist >= 1.193:
        return "spoon"
    elif hips_bust >= 9.14 and hips_waist < 22.86:
        return "triangle"
    elif bust_hips >= 9.14 and bust_waist < 22.86:
        return "inverted triangle"
    elif hips_bust < 9.14 and bust_hips < 9.14 and bust_waist < 22.86 and hips_waist < 25.4:
        return "rectangle"
    else:
        return "unknown"

def generate_fashion_recommendation(body_type: str) -> str:
    item_query = body_type_to_query.get(body_type, "fashion items")
    prompt = (
        f"You are a fashion assistant. Recommend the best clothing style for someone with a {body_type} body type. "
        f"Suggest pieces like {item_query}."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a fashion stylist."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/recommend-form", response_class=HTMLResponse)
def handle_form(request: Request,
                bust: float = Form(...),
                waist: float = Form(...),
                hips: float = Form(...),
                high_hip: float = Form(...)):
    body_type = classify_body_type(bust, waist, hips, high_hip)
    if body_type == "unknown":
        return templates.TemplateResponse("index.html", {"request": request, "error": "Could not classify body type."})
    recommendation = generate_fashion_recommendation(body_type)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "body_type": body_type,
        "recommendation": recommendation
    })

@app.post("/recommend")
def recommend_api(measurements: BodyMeasurements):
    body_type = classify_body_type(
        measurements.bust,
        measurements.waist,
        measurements.hips,
        measurements.high_hip,
    )
    if body_type == "unknown":
        raise HTTPException(status_code=400, detail="Could not classify body type")
    recommendation = generate_fashion_recommendation(body_type)
    return {"body_type": body_type, "recommendation": recommendation}