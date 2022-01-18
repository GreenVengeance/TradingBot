import telebot
from binance.client import Client

TOKEN = "YOUR TELEBOT TOKEN"
API_Key = "YOUR BINANCE API_KEY"
SECRET_Key = "YOUR BINANCE SECRET_KEY"

bot = telebot.TeleBot(TOKEN)
client = Client(API_Key, SECRET_Key)
