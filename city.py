import aiohttp
from api import CITY_URL

COUNTRIES = {
    "Россия": "RU",
    "Казахстан": "KZ",
    "США": "US",
    "Германия": "DE",
    "Франция": "FR",
    "Италия": "IT",
    "Испания": "ES"
}
CITIES = {}

async def get_cities(country: str):
    if country in CITIES:
        return CITIES[country]  

    country_code = COUNTRIES.get(country)
    if not country_code:
        print(f"❌ Ошибка: Страна '{country}' не поддерживается.")
        return []

    params = {
        "country": country_code,
        "featureClass": "P",
        "maxRows": 1000,
        "username": "VictoriaTrix",
        "lang": "ru"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(CITY_URL, params=params) as response:
                print(f"🔍 Запрос: {response.url}")  
                if response.status != 200:
                    print(f"❌ Ошибка API: {response.status}")
                    return []

                data = await response.json()
                print(f" Данные API для {country}: {data}")  

                if "geonames" in data:
                    CITIES[country] = [city["name"] for city in data["geonames"]]
                    print(f"Найдено {len(CITIES[country])} городов.")
                    return CITIES[country]
                else:
                    print("⚠️ В ответе нет данных о городах!")
                    return []
                    
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
            return []

    return []

def get_available_countries():
    return list(COUNTRIES.keys()) 