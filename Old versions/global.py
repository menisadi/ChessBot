import telebot

bot = telebot.TeleBot("5817401323:AAHDjTShJ5ymOhG3QwoqL4PHL_NlATACfcg")

# This variable will store all the messages received by the bot
messages = []

@bot.message_handler(commands=['store'])
def store_message(message):
  # Store the message in the list
  messages.append(message.text[7:])

@bot.message_handler(commands=['echo'])
def echo_messages(message):
  # Send all the stored messages back to the user
  for msg in messages:
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['clean'])
def clean_messages(message):
  # Clear the messages list
  messages.clear()

# Start the bot
bot.infinity_polling()