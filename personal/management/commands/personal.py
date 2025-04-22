from django.conf import settings
from django.core.management.base import BaseCommand

from asgiref.sync import sync_to_async
import logging,random

from telegram import Update, ReplyKeyboardMarkup,CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    ConversationHandler,
    filters,
    CallbackQueryHandler
)
from tiktok_downloader import TTDownloader


from bot.models import TelegramClient
from ...services import identify_person_from_video
from ...handlers import verify_instruction_and_user

instructions = [
    "Посмотрите налево, затем направо.",
    "Посмотрите вверх, затем вниз.",
    ]


class Command(BaseCommand):
    help = 'Run the Telegram bot'
    

    def handle(self, *args, **kwargs):
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
            )
        logger = logging.getLogger(__name__)

        application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

        user_instructions = {}

        async def start(update: Update, context: CallbackContext):
            await update.message.reply_text(
                "Добро пожаловать! Для идентификации отправьте видео-кружочек. Сначала получите инструкцию."
            )

        async def send_instruction(update: Update, context: CallbackContext):
            user_id = update.effective_user.id
            instruction = random.choice(instructions)
            user_instructions[user_id] = instruction
            await update.message.reply_text(
                f"Ваше задание: {instruction} После выполнения отправьте видео-кружочек."
            )

        async def handle_video(update: Update, context: CallbackContext):
            user_id = update.effective_user.id
            if user_id not in user_instructions:
                await update.message.reply_text(
                    "Сначала получите инструкцию с помощью команды /instruction."
                )
                return

            instruction = user_instructions[user_id]
            del user_instructions[user_id]

            video =  update.message.video_note or update.message.video
            if video:
                processing_message = await update.message.reply_text(
                    "видео обрабатыватеся подождите..."
                )
                file_id = video.file_id
                file = await context.bot.get_file(file_id)
                save_file = await file.download_to_drive(f'/Users/macpro2019/PersonalProjects/dowloader_back/personals/user_{user_id}_video.mp4')
                result = await sync_to_async(verify_instruction_and_user)(save_file,instruction)
                if result["status"] == "success":
                    user_data = result['data']
                    user_full_name = user_data.get('name')
                    user_age = user_data.get('age')
                    user_city = user_data.get('city')
                    user_email = user_data.get('email')
                    user_phone = user_data.get('phone')
                    user_avatar_url = user_data.get('avatar_url')
                    await processing_message.edit_text(
                        f"Вы найдены:\nИмя: {user_full_name}, \nВозраст: {user_age}, \nГород: {user_city}, \nЭлектронная почта: {user_email}, \nТелефон: {user_phone}, \nАватар: {user_avatar_url}"
                    )
                elif result['status'] == "failed":
                    await processing_message.edit_text(
                        f"Инструкция не выполнена"
                    )
                elif result["status"] == "not_found":
                    await processing_message.edit_text(
                        f"Пользователь не найден"
                    )
                else:
                    await processing_message.edit_text(
                        f"Ошибка при проверке видео: {result['message']}"
                    )
            else:
                await update.message.reply_text("Пожалуйста, отправьте видео-кружочек.")


        async def error_handler(update: object, context):
            logger.error("Произошла ошибка: %s", context.error)


        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("instruction", send_instruction))
        application.add_handler(MessageHandler(filters.VIDEO | filters.VIDEO_NOTE, handle_video))

        application.add_error_handler(error_handler)
        logger.info("Бот запущен...")

        application.run_polling()