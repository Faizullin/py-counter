PERMISSIONS={
	"FIRE_PREDICT":False,
	"TELEGRAM_BOT":False,
	"ESP_UPDATE":False
};

import sys,os,argparse,socket,cv2,config,json,requests;
parser = argparse.ArgumentParser()
parser.add_argument('--telegram', default='')
parser.add_argument('--fire_predict', default='')
parser.add_argument('--esp_update', default='')
args = parser.parse_args();
if args.telegram and (args.telegram=="1" or args.telegram==1):
	PERMISSIONS["TELEGRAM_BOT"]=True
if args.fire_predict and (args.fire_predict=="1" or args.fire_predict==1):
	PERMISSIONS["FIRE_PREDICT"]=True
if args.esp_update and (args.esp_update=="1" or args.esp_update==1):
	PERMISSIONS["ESP_UPDATE"]=True
if PERMISSIONS['TELEGRAM_BOT']:
	from src.tele import TeleBot
if PERMISSIONS["FIRE_PREDICT"]:
	from src.camera import Cam
	cam=Cam(config=config)

from src.sql import Sql
from threading import Thread
from flask import Flask,jsonify,request,render_template
from fuzzywuzzy import fuzz


class RequestReader:
	state= False;
	data = {'temp':0,'gas':0,'hum':0,"count":0}
	def __init__(self,config=None,this_host=None,ser=None):
		self.ser=ser
		pathT = config.PATHS['urls']['esp'].split(".");
		pathT[2] = str(this_host.split(".")[2])
		pathT=".".join(pathT);
		self.path = pathT +"readData";
		with open(config.PATHS['buildings'],"r",   encoding='utf-8') as f:
			buildings_data = json.loads(f.read());
			self.maxCount = buildings_data[0]['limit']['3']

	def request(self):
		if not self.state:
			self.state = True;
			Thread(target=self.make_request_in_thread,args=(),daemon=True).start()
		return self.data;
	def make_request_in_thread(self):
		try:
			data = requests.get(self.path,timeout= 10);
			data=data.json()
			app.logger.info(str(data))
			for key,val in data.items():
				if key in self.data.keys():
					self.data[key] = int(val);
		except Exception as err:
			self.ser.die(err)
		finally:
			self.state = False;
class Ser:
	def __init__(self,app):
		self.app = app
	def die(self,text):
		self.app.logger.info("ERROR:"+str(text))
app=Flask(__name__);bot=None;
ser=Ser(app)
sql=Sql(config)
this_host=socket.gethostbyname(socket.gethostname())
requestReader = RequestReader(config,this_host,ser=ser)
if PERMISSIONS["TELEGRAM_BOT"]:
	bot = TeleBot(config=config)
print("START ",this_host)

def tr(func):
	try:
		func();
	except Exception as err:
		print("ERROR: "+str(err))


del args;
@app.route('/',methods=["GET","POST"])
def app_index():
	buildings_data = None;
	with open(config.PATHS['buildings'],"r",   encoding='utf-8') as f:
		buildings_data = json.loads(f.read());
	if PERMISSIONS["ESP_UPDATE"]:

		buildings_data[0]["data"]= requestReader.request();
	return render_template('htmls/index.html',data={"buildings_data":buildings_data,'urls':config.PATHS['urls']})

@app.route('/charts/')
def on_show_charts():
	db_data = sql.get_complete_data(request.args);
	if db_data==False:
		return redirect('/');
	db_data['urls'] = config.PATHS['urls'];
	db_data['maxCount'] = requestReader.maxCount;
	return render_template('htmls/charts.html',data = db_data);

if PERMISSIONS["FIRE_PREDICT"]:
	@app.route('/upload/',methods=["GET","POST"])
	def app_upload():
		global cam;
		response = {
			'res':0,
			'status':500,
			'time':0,
                        'message':None
		}
		if request.files and 'file' in request.files:
			file = request.files['file']
			if file:
				try:
					img = cam.encode(file.read());
					res,duringTime = cam.predict_fire(img);
					app.logger.info((res,duringTime))
					response['time'] = duringTime;
					response['res'] = res;
					response['status']=200;
				except Exception as err:
					response['message'] = str(err);
					app.logger.info(str(err))
					print(err)
				return response;
		response['message']='File not Found';
		return response;


@app.route('/bye/',methods=['POST','GET'])
def app_shutdown_server():
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()
	if PERMISSIONS["TELEGRAM_BOT"]:
		bot.stop_polling()
	return "До свидание"

@app.route('/reload/',methods=['POST','GET'])
def app_reload():
	if os.path.exists("scripts/reload.py"):
		requests.get('http://'+this_host+':5000/bye')
		pid = os.getpid()
		Thread(target = os.system,args=(f"py scripts/reload.py --mypid={pid} --delay=2",),daemon=True).start()
		return "Перезапуск"
	return "error"

def getanswer(text):
	text=text.lower().strip()
	a=0;n=0;nn=0;
	with open(config.PATHS['vosk']+'words/boltun.json','r', encoding='utf-8') as file:
		mas=json.loads(file.read());
	for i in mas['plot']:
		for i_text in i['text']:
			aa=(fuzz.token_sort_ratio(i_text, text));
			if(aa>a and aa!=a):
				a=aa
				n=nn
		nn+=1
	if a>=80:
		return mas['plot'][n]
	nn=0;a=0;n=0;
	with open(config.PATHS['vosk']+'words/boltun.txt','r', encoding='utf-8') as file:
		mas=file.read().split('\n')
		for q in mas:
			if('u: ' in q):
				aa=(fuzz.token_sort_ratio(q.replace('u: ',''), text))
				if(aa>a and aa!=a):
					a=aa
					n=nn
			nn+=1;
	if a>70:
		return {'text':mas[n+1],'type':'a'};
	return None

if PERMISSIONS["TELEGRAM_BOT"]:
	@bot.message_handler(content_types=['text']) 
	def bot_get_messages(message):
		mas = getanswer(message.text)

		if mas is None:
			return bot.send(message,'Непоняла')
		if mas['type']=='f':
			if mas['func']=='do_bye':
				bot.stop_polling()
				requests.get('http://'+this_host+':5000/bye')
				return bot.send(message, 'Пока')
			elif mas['func']=='get_data':
				text = ''
				try:
					app.logger.info("Request to ESP")
					res = requests.get(config.PATHS['urls']['esp']+"readData",timeout = 10)
					app.logger.info(str(res))
					data = res.json();
					app.logger.info(str(data))
					text += f'Температура {data["temp"]} Влажность {data["hum"]} Уровень газа {data["gas"]} Количество людей {data["count"]}'
				except Exception as err:
					text += "\nОшибка запроса"
					print(err)
				return bot.send(message, text)
		elif mas['type']=='a':
			return bot.send(message, mas['text'])


if(PERMISSIONS["TELEGRAM_BOT"] and PERMISSIONS["FIRE_PREDICT"]):
	@bot.message_handler(content_types=['photo'])
	def bot_get_photo(message):
		global cam,ser;
		file_info = bot.get_file(message.photo[0].file_id)
		try:
			file_info = cam.encode(bot.download_file(file_info.file_path));
			res,duringTime = cam.predict_fire(file_info);
		except Exception as err:
			ser.die(err);
			return bot.send(message,"ERROR: "+str(err));
		text = 'Ничего не найдено'
		if res==1:
			text = '🔥 Опасность возникновения огня 🔥'
		elif res==2:
			text = '🔥🔥🔥 Замечен пожар 🔥🔥🔥'
		bot.send(message,text)

if __name__=='__main__':
	if PERMISSIONS["TELEGRAM_BOT"]:
		Thread(target=bot.polling,args=(),daemon=True).start()
	app.run(host=this_host, port=5000, debug=True,use_reloader=False)#,,
	

		
