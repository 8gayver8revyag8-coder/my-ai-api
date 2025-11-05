from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="My Cloud AI API",
    description="Мой первый AI API развернутый в облаке!",
    version="1.0.0"
)

# Разрешаем запросы отовсюду
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    max_results: int = 3

class ParseRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {
        "message": "🚀 Мой AI API работает!",
        "status": "active", 
        "version": "1.0",
        "endpoints": {
            "GET /": "Эта страница",
            "POST /search": "Поиск в интернете",
            "POST /parse": "Парсинг сайта", 
            "POST /chat": "Общение с AI",
            "GET /health": "Проверка здоровья API"
        }
    }

@app.post("/search")
async def search_web(request: SearchRequest):
    """Поиск информации в интернете через DuckDuckGo"""
    try:
        print(f"🔍 Поиск: {request.query}")
        
        search_url = "https://api.duckduckgo.com/"
        params = {
            'q': request.query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        data = response.json()
        
        # Формируем ответ
        result = {
            "query": request.query,
            "abstract": data.get('AbstractText', 'Информация не найдена'),
            "source": data.get('AbstractSource', 'DuckDuckGo'),
            "url": data.get('AbstractURL', ''),
            "related_topics": []
        }
        
        # Добавляем связанные темы
        for topic in data.get('RelatedTopics', [])[:request.max_results]:
            if 'Text' in topic:
                result["related_topics"].append(topic['Text'])
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при поиске: {str(e)}")

@app.post("/parse")
async def parse_website(request: ParseRequest):
    """Парсинг содержимого веб-страницы"""
    try:
        print(f"🌐 Парсим URL: {request.url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(request.url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Извлекаем заголовок
        title = soup.find('title')
        title_text = title.text.strip() if title else "Заголовок не найден"
        
        # Извлекаем основной текст
        paragraphs = soup.find_all('p')[:3]
        text_content = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        result = {
            "url": request.url,
            "title": title_text,
            "content_preview": text_content[:300] + "..." if len(text_content) > 300 else text_content,
            "status": "success"
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {str(e)}")

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    """Простой AI чат-бот"""
    user_message = request.message.lower().strip()
    
    print(f"💬 Чат запрос: {user_message}")
    
    # База знаний AI
    responses = {
        "привет": "Привет! Я твой AI помощник! ☁️",
        "как дела": "Отлично! Работаю в облаке!",
        "что ты умеешь": "Искать информацию, парсить сайты и общаться!",
        "погода": "Используй /search для поиска погоды",
        "новости": "Используй endpoint /search для новостей!",
    }
    
    ai_response = responses.get(user_message, f"Я получил: '{request.message}'. Используй /search для поиска информации!")
    
    return {
        "user_message": request.message,
        "ai_response": ai_response
    }

@app.get("/health")
def health_check():
    """Проверка здоровья API"""
    return {
        "status": "healthy",
        "message": "✅ Все системы работают нормально!"
    }

# ЗАПУСК СЕРВЕРА - УПРОЩЕННАЯ ВЕРСИЯ
if __name__ == "__main__":
    print("🚀 Запуск AI API сервера...")
    print("📍 Адрес: http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    print("🛑 Остановка: Ctrl+C")
    
    # Простой запуск без reload
    uvicorn.run(app, host="0.0.0.0", port=8000)