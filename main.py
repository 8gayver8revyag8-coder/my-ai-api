from fastapi import FastAPI
from pydantic import BaseModel
import requests
import random

app = FastAPI(title="Smart AI API", version="2.1")

class ChatRequest(BaseModel):
    message: str

def get_ai_response(user_input):
    """Пробуем разные бесплатные AI модели"""
    
    # Список бесплатных моделей которые точно работают
    models = [
        "microsoft/DialoGPT-small",  # Маленькая но быстрая
        "facebook/blenderbot-400M-distill",  # Альтернатива
        "microsoft/DialoGPT-large",  # Большая модель
    ]
    
    for model in models:
        try:
            API_URL = f"https://api-inference.huggingface.co/models/{model}"
            
            payload = {
                "inputs": user_input,
                "parameters": {
                    "max_length": 300,
                    "temperature": 0.7,
                    "do_sample": True
                },
                "options": {
                    "wait_for_model": False  # Не ждем если модель грузится
                }
            }
            
            response = requests.post(API_URL, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['generated_text']
                    
        except Exception as e:
            continue  # Пробуем следующую модель
    
    # Если все модели не сработали, используем DeepSeek
    try:
        return get_deepseek_response(user_input)
    except:
        return "Привет! Я твой AI помощник. Сейчас основная AI система временно недоступна, но я могу помочь с программированием! 🚀"

def get_deepseek_response(user_input):
    """Резервный вариант через DeepSeek"""
    try:
        # Альтернативный бесплатный API
        url = "https://free.churchless.tech/v1/chat/completions"
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Ты полезный AI помощник. Отвечай на русском языке."},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(url, json=data, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except:
        pass
    
    return None

@app.post("/smart-chat")
async def smart_chat(request: ChatRequest):
    """Умный чат с настоящим AI"""
    user_input = request.message
    
    print(f"💬 Запрос: {user_input}")
    
    ai_response = get_ai_response(user_input)
    
    return {
        "user_message": user_input,
        "ai_response": ai_response,
        "source": "AI Assistant",
        "type": "smart_chat"
    }

@app.post("/chat")
async def simple_chat(request: ChatRequest):
    """Простой чат для обратной совместимости"""
    return await smart_chat(request)

@app.get("/")
def home():
    return {
        "message": "🚀 Умный AI API работает!",
        "version": "2.1",
        "status": "active",
        "endpoints": {
            "POST /smart-chat": "Настоящий AI (мульти-модель)",
            "POST /chat": "Простой чат", 
            "GET /": "Эта страница"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "Smart AI API",
        "version": "2.1",
        "ai_models": "Multi-model fallback"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
