import logging

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


from src.utils import load_message, load_prompt, load_image, load_personalities, load_topics, load_translate_lang
from src.openapi_client import OpenAiClient
from src.bot.service import gpt_response, talk_mode_response, quiz_mode_response, quiz_start_interface, talk_mode_start, \
    translate_mode_translate_text, photo_mode_response

openai_client = OpenAiClient()

# start CommandHandler
async def start_handler(update: Update, context: ContextTypes):
    text = load_message("main")
    image_bytes = load_image("main")

    context.user_data['mode'] = None

    query = update.callback_query

    if update.message:
        await update.message.reply_photo(photo=image_bytes, caption=text, parse_mode='Markdown')
    elif query:
        await query.message.reply_photo(
            photo=image_bytes,
            caption=text,
            parse_mode='Markdown')



# random_fact CommandHandler
async def random_fact_handler(update: Update, context: ContextTypes):
    text = load_message("random")
    prompt = load_prompt("random")
    image_bytes = load_image("random")

    context.user_data['mode'] = 'random'

    keyboard = [
        [InlineKeyboardButton(text = "Хочу ще факт", callback_data='random_again')],
        [InlineKeyboardButton(text = "Закінчити", callback_data='finish')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        txt_response = await openai_client.ask(user_message="", system_prompt= prompt)

        await update.message.reply_photo(
            photo=image_bytes,
            caption=f"{text}\n\n{txt_response}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Error in random_fact: {e}")
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте пізніше.")


# gpt_interface CommandHandler
async def gpt_interface_handler(update: Update, context: ContextTypes):
    text = load_message("gpt")
    image_bytes = load_image("gpt")

    context.user_data['mode'] = 'gpt'

    await update.message.reply_photo(photo=image_bytes, caption=text, parse_mode='Markdown')



# translate_text CommandHandler # Shows buttons with languages
async def translate_text_handler(update: Update, context: ContextTypes):
    text = load_message("translate")
    image_bytes = load_image("translate")
    languages = load_translate_lang("languages")

    context.user_data['mode'] = 'translate'

    keyboard = [
        [InlineKeyboardButton(text=key, callback_data=value)]
        for key, value in languages.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_photo(
        photo=image_bytes,
        caption=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )




# talk_with_personality CommandHandler
async def talk_with_personality_handler(update: Update, context: ContextTypes):
    text = load_message("talk")
    image_bytes = load_image("talk")
    personalities = load_personalities("personalities")

    context.user_data['mode'] = 'talk_'

    keyboard = [
        [InlineKeyboardButton(text=key, callback_data=value)]
        for key, value in personalities.items()
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=image_bytes,
        caption=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# quiz_game CommandHandler
async def quiz_game_handler(update: Update, context: ContextTypes):
    text = load_message("quiz")
    image_bytes = load_image("quiz")
    topics = load_topics("topics")

    context.user_data['mode'] = 'quiz_'

    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton(text=key, callback_data=value)]
        for key, value in topics.items()
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_photo(
            photo=image_bytes,
            caption=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif query:
        #await query.delete_message()
        await query.message.reply_photo(
            photo=image_bytes,
            caption=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# text_messages MessageHandler
async def text_messages_handler(update: Update, context: ContextTypes):
    user_mode = context.user_data.get('mode', '')
    user_text = update.message.text

    if user_mode == '':
        return

    if user_mode.startswith( 'translate_'): #translate mode is selected. User pressed button, with selected lang. User entered text to translate
        lang = user_mode.split('_')[1]

        await translate_mode_translate_text(
            app=openai_client,
            lang=lang,
            user_text=user_text,
            update=update)

    elif user_mode == 'photo':
        await photo_handler(update, context)

    elif user_mode == 'gpt':
        await gpt_response(
            app = openai_client,
            mode="gpt",
            user_text = user_text,
            update = update)

    elif user_mode.startswith('talk_'):
        personality = user_mode.split('_')[1]
        await talk_mode_response(
            app = openai_client,
            personality = personality,
            user_text = user_text,
            update = update)

    elif user_mode.startswith('quiz_'):
        topic = user_mode.split('_')[1]
        score = context.user_data.get('score', 0)

        if 'quiz_question' in context.user_data:
            await quiz_mode_response(
                app = openai_client,
                user_text = user_text,
                topic = topic,
                score = score,
                update = update,
                context=context)


# query_callback CallbackQueryHandler
async def query_callback_handler(update: Update, context: ContextTypes):
    query = update.callback_query
    await query.answer()


    if query.data == 'random_again':
        await gpt_response(
            app = openai_client,
            mode="random_again",
            user_text = "",
            update = update)

    elif query.data == 'finish':
        context.user_data.clear()
        await start_handler(update, context)

    elif query.data.startswith('talk_'):
        personality = query.data.split('_')[1]
        context.user_data['mode'] = query.data

        await talk_mode_start(
            user_text= personality,
            update = update)

    elif query.data.startswith('quiz_'):

        if query.data == 'quiz_change_topic':
            await quiz_game_handler(update, context)
            return

        elif query.data.startswith('talk_'):
            #personality = query.data.split('_')[1]
            context.user_data['mode'] = query.data

        await quiz_start_interface(
            app = openai_client,
            query = query,
            update = update,
            context = context
        )


    elif query.data.startswith('translate_'):#translate mode is selected. Message with lang buttons is showing. User pressed button, with selected lang.
        lang = query.data.split('_')[1]
        context.user_data['mode'] = query.data

        txt = load_message("translate_output_" + lang)
        await query.message.reply_text(text=txt, reply_markup=None, parse_mode='MARKDOWN')



# "/photo" command CommandHandler
async def photo_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "photo"
    await update.message.reply_text(
        text="Завантажте фото через меню завантаження, чи використовуйте Ctrl+C Ctrl+V ... \n\n ChatGPT опише ваше фото")

#image and doc with image MessageHandler
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.user_data:
        await update.message.reply_text(
            text="Введіть команду \"Photo\", чи виберіть її з \"Menu\" .."
        )
        return

    if not context.user_data["mode"] == "photo":
        await update.message.reply_text(
            text="Використовуйте команду '\\photo' для роботи з фото .."
        )
        return
    photo_doc = update.message.document
    photo_file: telegram.File = None

    if not photo_doc:
        if update.message.photo:
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
        else:
            await update.message.reply_text("Фото відсутнє !")
    else:
        if photo_doc.mime_type.startswith("image/"):
            photo_file = await photo_doc.get_file()
        else:
            await update.message.reply_text("Завантажуйте саме фото !")

    await photo_mode_response(app = openai_client,file=photo_file,  update=update)

