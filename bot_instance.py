import telebot
import config

bot = telebot.TeleBot(config.API_TOKEN, parse_mode='HTML')
