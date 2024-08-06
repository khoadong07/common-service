from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from typing import List
import fasttext
import asyncio

app = FastAPI()

model = fasttext.load_model('lid.176.bin')

router = APIRouter(prefix="/api")

class ContentRequest(BaseModel):
    id: str
    content: str

class LanguageRequest(BaseModel):
    contents: List[ContentRequest]

class LanguageResponse(BaseModel):
    id: str
    language: str
    confidence: float

async def predict_language(content_request: ContentRequest):
    predictions = model.predict(content_request.content)
    language = predictions[0][0].replace('__label__', '')
    confidence = predictions[1][0]
    return LanguageResponse(id=content_request.id, language=language, confidence=confidence)

# Định nghĩa endpoint để dự đoán ngôn ngữ
@router.post("/predict_languages", response_model=List[LanguageResponse])
async def predict_languages(request: LanguageRequest):
    tasks = [predict_language(item) for item in request.contents]
    responses = await asyncio.gather(*tasks)
    return responses

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
