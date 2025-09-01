import logging

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from src.config import TG_BOT_API_KEY

from src.bot.handlers import start_handler, gpt_interface_handler, random_fact_handler, talk_with_personality_handler, \
    quiz_game_handler, text_messages_handler, query_callback_handler, translate_text_handler, photo_start_handler, \
    photo_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



app = ApplicationBuilder().token(TG_BOT_API_KEY).build()

app.add_handler(CommandHandler("start", start_handler))
app.add_handler(CommandHandler("random", random_fact_handler))
app.add_handler(CommandHandler("gpt", gpt_interface_handler))
app.add_handler(CommandHandler("talk", talk_with_personality_handler))
app.add_handler(CommandHandler("quiz", quiz_game_handler))
app.add_handler(CommandHandler("translate", translate_text_handler))


app.add_handler(CommandHandler('photo', photo_start_handler, filters=filters.COMMAND))

photo_filter = filters.PHOTO | filters.Document.IMAGE
app.add_handler(MessageHandler(callback = photo_handler, filters=photo_filter))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_messages_handler))
app.add_handler(CallbackQueryHandler(query_callback_handler))

app.run_polling()