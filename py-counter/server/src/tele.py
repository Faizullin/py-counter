import telebot
class TeleBot(telebot.TeleBot):
	def __init__(self,config):
		telebot.TeleBot.__init__(self,config.TELEGRAM_TOKEN)
		del config
	def send(self,message,text):
		#user_markup = telebot.types.ReplyKeyboardMarkup(True, False); user_markup.row('Помощь')
		self.send_message(message.chat.id,text.lower().capitalize())
