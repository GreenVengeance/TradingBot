import config.keys as keys
import telebot
from telebot import types
import src.traid as traid

bot = telebot.TeleBot(keys.TOKEN)

def createKeyboardmain():
    keyboardmain = types.InlineKeyboardMarkup(row_width=2)
    start_button = types.InlineKeyboardButton(text="Start Bot", callback_data="start")
    stop_button = types.InlineKeyboardButton(text="Stop Bot", callback_data="stop")
    info_button = types.InlineKeyboardButton(text="Get Results", callback_data="results")
    keyboardmain.add(start_button, stop_button, info_button)
    return keyboardmain

@bot.message_handler(['start'])  # welcome message handler
def send_welcome(message):
    bot.reply_to(message, "(Welcome, I'm the tradingBot and I will assist you)")


@bot.message_handler(content_types=["text"])
def any_msg(message):
    bot.send_message(chat_id=message.chat.id, reply_markup=createKeyboardmain(),
                     text="Choose an Action\n"
                          "The TraindingBot is " + traid.tradingBot_sate())


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "start":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=traid.starting_the_TradingBot(),
                              text="Starting the Bot\n ...")
    elif call.data == "stop":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=traid.stopping_the_TradingBot(),
                              text="Stopping the Bot")

    elif call.data == "results":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=traid.get_results())


if __name__ == "__main__":
    bot.polling(True)
