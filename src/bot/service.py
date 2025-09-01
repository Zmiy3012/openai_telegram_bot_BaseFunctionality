import base64

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes

from src.utils import load_prompt, load_image, load_personalities, load_topics, load_message
from src.openapi_client import OpenAiClient

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


#ask chatGPT and return result to bot
# user_text = '' in 'random' mode
async def gpt_response(app: OpenAiClient, mode: str, user_text: str, update: Update) -> None:
    prompt = load_prompt("gpt")
    txt = load_message("gpt")
    query = update.callback_query

    keyboard = InlineKeyboardMarkup([])
    if mode == 'random_again':
        # a new randow fact
        prompt = load_prompt("random")
        txt = load_message("random")
        keyboard = [
            [InlineKeyboardButton("Хочу ще факт", callback_data='random_again')],
            [InlineKeyboardButton("Закінчити", callback_data='finish')]
        ]
    elif mode == 'gpt':
        # ask gpt again
        keyboard = [
            [InlineKeyboardButton("Закінчити", callback_data='finish')]
        ]

    try:

        txt_response = await app.ask(user_text, prompt)

        reply_markup = InlineKeyboardMarkup(keyboard)

        caption = f"{txt}\n\n{txt_response}"

        #if update.message:
        if mode == 'gpt':
            await update.message.reply_text(
                text=txt_response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif mode == 'random_again':
            # another random fact
            if query.message.caption:
                await query.edit_message_caption(
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            elif query.message.text:
                await query.message.reply_text(
                    text=txt_response,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
    except Exception as e:
        logging.error(f"Error in random_again: {e}")
        await query.edit_message_caption("Вибачте, сталася помилка. Спробуйте пізніше.")


#async def talk_mode_reply_photo_response(app: OpenAiClient, user_text: str, update: Update) -> None:
async def talk_mode_start(user_text: str, update: Update) -> None:
    query = update.callback_query
    personalities_images = load_personalities("personalities_images")

    image_bytes = load_image(personalities_images[user_text])

    keyboard = [[InlineKeyboardButton("Закінчити", callback_data='finish')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_photo(
        photo=image_bytes,
        caption="Можете почати розмову! Напишіть ваше повідомлення.",
        reply_markup=reply_markup
    )



async def gpt_mode_response(app: OpenAiClient, user_text: str, update: Update) -> None:
    prompt = load_prompt("gpt")
    try:
        txt_response = await app.ask(user_text, prompt)
        await update.message.reply_text(txt_response)
    except Exception as e:
        logging.error(f"Error in gpt mode: {e}")
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте пізніше.")


async def talk_mode_response(app: OpenAiClient, personality: str, user_text: str, update: Update) -> None:
    prompt = load_prompt(f"talk_{personality}")

    keyboard = [[InlineKeyboardButton("Закінчити", callback_data='finish')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        txt_response = await app.ask(user_text, prompt)
        await update.message.reply_text(txt_response, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Error in talk mode: {e}")
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте пізніше.")


async def translate_mode_translate_text(
                                  app: OpenAiClient,
                                  lang: str,
                                  user_text: str,
                                  update: Update) -> None:

    prompt = load_prompt(f"translate_{lang}")

    keyboard = [[InlineKeyboardButton(text="Finish", callback_data='finish')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        txt_response = await app.ask(user_text, prompt)
        await update.message.reply_text(text=txt_response, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Error in translate mode: {e}")
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте пізніше.")






async def quiz_mode_response(app: OpenAiClient, user_text: str, topic: str, score: int, update: Update, context: ContextTypes) -> None:
    check_prompt = f"Користувач відповів: '{user_text}' на питання: '{context.user_data['quiz_question']}'. Скажи чи правильна відповідь (так/ні) та дай коротке пояснення."
    try:
        txt_response = await app.ask(user_message=check_prompt,
                                     system_prompt="Ти експерт з квізів. Перевіряй відповіді користувачів.")

        is_correct = not ("неправильн" in txt_response.lower() or "не є правильн" in txt_response.lower() or "не правильн" in txt_response.lower())

        if is_correct:
            context.user_data['score'] = score + 1

        current_score = context.user_data.get('score', 0)

        keyboard = [
            [InlineKeyboardButton("Ще питання", callback_data=f'quiz_{topic}')],
            [InlineKeyboardButton("Змінити тему", callback_data='quiz_change_topic')],
            [InlineKeyboardButton("Закінчити", callback_data='finish')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(text=f"{txt_response}\n\nВаш рахунок: {current_score}", reply_markup=reply_markup)

        del context.user_data['quiz_question']
    except Exception as e:
        logging.error(f"Error in quiz mode: {e}")
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте пізніше.")


async def quiz_start_interface(app: OpenAiClient, query: CallbackQuery, update: Update,
                               context: ContextTypes) -> None:

    topic = query.data.split('_')[1]
    context.user_data['mode'] = query.data

    if 'score' not in context.user_data:
        context.user_data['score'] = 0

    topic_prompts = load_topics("topic_prompts")

    try:
        txt_response = await app.ask(topic_prompts[topic], load_prompt("quiz"))
        context.user_data['quiz_question'] = txt_response

        caption = f"{txt_response}\n\nНапишіть вашу відповідь (A, B, C або D):"

        if query.message.caption:
            await query.edit_message_caption(
                caption=caption
            )
        else:
            await query.edit_message_text(
                text=caption
            )

    except Exception as e:
        logging.error(f"Error in quiz mode: {e}")
        await query.edit_message_caption("Вибачте, сталася помилка. Спробуйте пізніше.")

async def photo_mode_response(app: OpenAiClient, file: telegram.File, update: Update) -> None:

    photo_file_data = await file.download_as_bytearray()

    # Coding to base64
    b64_str = base64.b64encode(photo_file_data).decode("utf-8")

    response = await app.ask_photo(b64_str=b64_str)


    keyboard = [
        [
            InlineKeyboardButton(text="Закінчити", callback_data='finish')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=response,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )