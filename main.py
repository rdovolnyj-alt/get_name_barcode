from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import re
import uvicorn
import os

app = FastAPI()

# 1. РАЗРЕШАЕМ CORS (необходимо для работы FlutterFlow в браузере)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Актуальный User-Agent на 2025 год
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@app.get("/")
def get_barcode(barcode: str = Query(..., description="Штрих-код товара")):
    pattern = r"\s*-\s*Штрих-код.*"
    try:
        url = f"https://barcode-list.ru/barcode/RU/barcode-{barcode}/Поиск.htm"
        
        # 2. ТАЙМАУТ И ПРОВЕРКА СТАТУСА
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 403:
            return {"product_name": "Ошибка: Сайт заблокировал доступ (403 Forbidden)"}
        if response.status_code != 200:
            return {"product_name": f"Ошибка сайта: код {response.status_code}"}

        # 3. ИСПОЛЬЗУЕМ html.parser (он встроен в Python и не требует lxml)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else ""

        if title and re.search(pattern, title):
            product_name = re.sub(pattern, "", title).strip()
            # Проверка на пустой результат парсинга
            if not product_name or product_name == "Поиск":
                product_name = "Товар не найден"
        else:
            product_name = "Нет данных в базе"
            
        return {"product_name": product_name}

    except Exception as e:
        # Показываем реальную причину ошибки для отладки
        return {"product_name": f"Ошибка сервера: {str(e)}"}

if __name__ == "__main__":
    # Берем порт из переменной окружения Render или используем 10000 по умолчанию
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
