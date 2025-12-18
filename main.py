from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import re
import uvicorn

app = FastAPI()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15"
}

@app.get("/")
def get_barcode(barcode: str):
    pattern = r"\s*-\s*Штрих-код.*"
    try:
        url = f"https://barcode-list.ru/barcode/RU/barcode-{barcode}/Поиск.htm"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.title.string if soup.title else ""

        if title and re.search(pattern, title):
            product_name = re.sub(pattern, "", title).strip()
        else:
            product_name = "Нет данных"
        return {"product_name": product_name}
    except:
        return {"product_name": "Ошибка запроса"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
