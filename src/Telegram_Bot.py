from telebot import types

import src.report_asset as report
import src.trade as trade
from config.keys import bot


def main_keyboardmain():
    keyboardmain = types.InlineKeyboardMarkup(row_width=2)

    start_button = types.InlineKeyboardButton(text="Start Bot", callback_data="start")
    stop_button = types.InlineKeyboardButton(text="Stop Bot", callback_data="stop")
    info_button = types.InlineKeyboardButton(text="Get Portfolio", callback_data="get_portfolio")
    trade_info_button = types.InlineKeyboardButton(text="Trade Infos", callback_data="trade_infos")

    keyboardmain.add(start_button, stop_button, info_button, trade_info_button)
    return keyboardmain


def trade_info_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    BEP = types.InlineKeyboardButton(text="Get BEP", callback_data="BEP")
    add_trade = types.InlineKeyboardButton(text="Add Trade", callback_data="add_trade")
    reset = types.InlineKeyboardButton(text="Reset", callback_data="reset")
    backbutton = types.InlineKeyboardButton(text="Back", callback_data="mainmenu")

    keyboard.add(BEP, add_trade, reset, backbutton)
    return keyboard


@bot.message_handler(['start'])  # welcome message handler
def send_welcome(message):
    bot.reply_to(message, "(Welcome, I'm the tradingBot and I will assist you)")


@bot.message_handler(content_types=["text"])
def any_msg(message):
    bot.send_message(chat_id=message.chat.id, reply_markup=main_keyboardmain(),
                     text="Choose an Action\n"
                          "The TradingBot is " + trade.tradingBot_sate())


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):  # TODO: Format elifs to switch case and compare
    if call.data == "mainmenu":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=main_keyboardmain(),
                              text="Main.")


    elif call.data == "start":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=trade.starting_the_TradingBot(),
                              text="Starting the Bot\n ...")

    elif call.data == "stop":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=trade.stopping_the_TradingBot(),
                              text="Stopping the Bot")

    elif call.data == "get_portfolio":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=report.get_Portfolio_total())

    elif call.data == "trade_infos":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=trade_info_keyboard(),
                              text="Here are some trade informations")

    elif call.data == "BEP":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=trade_info_keyboard(),
                              text=report.get_BEP_of_telegrams_items())
    elif call.data == "add_tade":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=trade_info_keyboard(),
                              text=report.add_element_to_telegram_item("Buy_p", "usedCoins"))
    elif call.data == "reset":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=report.reset_telegram_items())


if __name__ == "__main__":
    bot.polling(True)

"""
import telebot
from telebot import types
token = "your token"
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=["text"])
def any_msg(message):
    keyboardmain = types.InlineKeyboardMarkup(row_width=2)
    first_button = types.InlineKeyboardButton(text="1button", callback_data="first")
    second_button = types.InlineKeyboardButton(text="2button", callback_data="second")
    keyboardmain.add(first_button, second_button)
    bot.send_message(message.chat.id, "testing kb", reply_markup=keyboardmain)

@bot.callback_query_handler(func=lambda call:True)
def callback_inline(call):
    if call.data == "mainmenu":

        keyboardmain = types.InlineKeyboardMarkup(row_width=2)
        first_button = types.InlineKeyboardButton(text="1button", callback_data="first")
        second_button = types.InlineKeyboardButton(text="2button", callback_data="second")
        keyboardmain.add(first_button, second_button)
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id, text="menu",reply_markup=keyboardmain)

    if call.data == "first":
        keyboard = types.InlineKeyboardMarkup()
        rele1 = types.InlineKeyboardButton(text="1t", callback_data="1")
        rele2 = types.InlineKeyboardButton(text="2t", callback_data="2")
        rele3 = types.InlineKeyboardButton(text="3t", callback_data="3")
        backbutton = types.InlineKeyboardButton(text="back", callback_data="mainmenu")
        keyboard.add(rele1, rele2, rele3, backbutton)
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id, text="replaced text",reply_markup=keyboard)

    elif call.data == "second":
        keyboard = types.InlineKeyboardMarkup()
        rele1 = types.InlineKeyboardButton(text="another layer", callback_data="gg")
        backbutton = types.InlineKeyboardButton(text="back", callback_data="mainmenu")
        keyboard.add(rele1,backbutton)
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id, text="replaced text",reply_markup=keyboard)

    elif call.data == "1" or call.data == "2" or call.data == "3":
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="alert")
        keyboard3 = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="lastlayer", callback_data="ll")
        keyboard3.add(button)
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id, text="last layer",reply_markup=keyboard3)


if __name__ == "__main__":
    bot.polling(none_stop=True)
"""
