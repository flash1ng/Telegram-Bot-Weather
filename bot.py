import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Конфигурация (лучше вынести в отдельный config.py или использовать переменные окружения)
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Замените на реальный токен
WEATHER_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"  # Ключ от OpenWeatherMap

class WeatherBot:
    """
    Телеграм-бот для получения текущей погоды в любом городе мира
    Использует API OpenWeatherMap
    """
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = (
            "Привет! Я погодный бот.\n"
            "Просто напиши мне название города, и я пришлю текущую погоду.\n"
            "Например: Москва или London"
        )
        await update.message.reply_text(welcome_text)

    @staticmethod
    def _fetch_weather_data(city: str) -> dict:
        """Получение данных о погоде через API"""
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при запросе к API погоды: {e}")

    @staticmethod
    def _format_weather(weather_data: dict) -> str:
        """Форматирование данных о погоде в читаемый текст"""
        return (
            f"🌤 Погода в {weather_data['name']}:\n"
            f"🌡 Температура: {weather_data['main']['temp']}°C\n"
            f"💧 Влажность: {weather_data['main']['humidity']}%\n"
            f"🌬 Ветер: {weather_data['wind']['speed']} м/с\n"
            f"📝 {weather_data['weather'][0]['description'].capitalize()}"
        )

    async def handle_weather_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка запросов погоды"""
        city = update.message.text.strip()
        
        try:
            weather_data = self._fetch_weather_data(city)
            if weather_data.get("cod") != 200:
                await update.message.reply_text("Город не найден. Попробуйте другой.")
                return
            
            weather_report = self._format_weather(weather_data)
            await update.message.reply_text(weather_report)
            
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {str(e)}")

def main():
    """Запуск бота"""
    try:
        bot = WeatherBot()
        
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Регистрация обработчиков
        app.add_handler(CommandHandler("start", bot.start))
        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_weather_request)
        )
        
        print("Бот успешно запущен")
        app.run_polling()
        
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main()