from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import uvicorn
import re
import nest_asyncio

nest_asyncio.apply()

app = FastAPI()

print(" BERT Modeli Hazırlanıyor...")
classifier = pipeline("sentiment-analysis", model="savasy/bert-base-turkish-sentiment-cased")

class AnalysisRequest(BaseModel):
    text: str

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    try:
        raw_text = request.text
        clean_text = re.sub(r"http\S+|@\S+", "", raw_text)[:500].strip()
        
        if not clean_text or len(clean_text) < 2:
            return {"text": raw_text, "sentiment": "SKIPPED", "confidence": 0}

        #Analiz kısmı
        prediction = classifier(clean_text)[0]
        label = prediction['label'].lower()
        score = prediction['score']

        #Eşleştirme kısmı
        if score < 0.70:
            final_sentiment = "NEUTRAL"
        else:
            final_sentiment = "POSITIVE" if "pos" in label else "NEGATIVE"

        return {
            "text": clean_text,
            "sentiment": final_sentiment,
            "confidence": round(score, 4),
            "status": "success"
        }
    except Exception as e:
        #Hata mesajı gödnerme kısmı
        print(f"HATA OLUŞTU: {str(e)}")
        return {"text": request.text, "sentiment": "ERROR", "error_msg": str(e), "status": "failed"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)