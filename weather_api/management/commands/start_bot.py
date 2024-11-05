from django.core.management.base import BaseCommand
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, Updater, ApplicationBuilder, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from asgiref.sync import sync_to_async
from django.conf import settings

from weather_api.services import WeatherService, CityNotFound

class Command(BaseCommand):
    help = 'Starts the Telegram bot'

    def handle(self, *args, **kwargs):
        #app = ApplicationBuilder().token('8085169735:AAGSnCb8V61iCPw-t9tZh-aCnicyZTix7C0').build()
        app = ApplicationBuilder().token(settings.TG_BOT_TOKEN).build()

        async def start(update: Update, context: CallbackContext):
            await update.message.reply_text("Введите название города:")

        async def weather_handler(update: Update, context: CallbackContext) -> None:
            city_name = update.message.text
            try:
                get_weather = sync_to_async(WeatherService.get_weather)
                weather = await get_weather(city_name, kind='tg')
                text = "Погода в {}: {}°C, {} мм рт/с, {} м/с".format(city_name, weather['temp'], weather['pressure'], weather['wind_speed'])
                await update.message.reply_text(text=text)
            except CityNotFound:
                await update.message.reply_text("Город не найден")

        start_handler = CommandHandler('start', start)
        app.add_handler(start_handler)
        app.add_handler(MessageHandler(filters.Text(), weather_handler))
        app.run_polling()
