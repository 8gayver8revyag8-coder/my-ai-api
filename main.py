from fastapi import FastAPI
from pydantic import BaseModel
import requests
import random

app = FastAPI(title="Smart AI API", version="2.0")

class ChatRequest(BaseModel):
    message: str

def get_ai_response(user_input):
    """Получаем ответ от настоящего AI через Hugging Face"""
    try:
        # Используем бесплатную AI модель от Microsoft
        API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        payload = {
            "inputs": user_input,
            "parameters": {
                "max_length": 500,
                "temperature": 0.7,
                "do_sample": True
            },
            "options": {
                "wait_for_model": True  # Ждем если модель загружается
            }
        }
        
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0]['generated_text']
            else:
                return "Извините, не получилось обработать запрос"
        else:
            return f"AI временно недоступен (код: {response.status_code})"
            
    except Exception as e:
        return f"Ошибка соединения с AI: {str(e)}"

@app.post("/smart-chat")
async def smart_chat(request: ChatRequest):
    """Умный чат с настоящим AI"""
    user_input = request.message
    
    print(f"💬 Получен запрос: {user_input}")
    
    ai_response = get_ai_response(user_input)
    
    return {
        "user_message": user_input,
        "ai_response": ai_response,
        "source": "HuggingFace AI",
        "model": "microsoft/DialoGPT-medium"
    }

@app.post("/chat")
async def simple_chat(request: ChatRequest):
    """Простой чат для обратной совместимости"""
    return await smart_chat(request)

@app.get("/")
def home():
    return {
        "message": "🚀 Умный AI API работает!",
        "version": "2.0",
        "endpoints": {
            "POST /smart-chat": "Настоящий AI через Hugging Face",
            "POST /chat": "Простой чат",
            "GET /": "Эта страница"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "Smart AI API",
        "ai_provider": "Hugging Face",
        "model": "DialoGPT-medium"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
