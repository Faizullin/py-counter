import datetime,time,sys,json,re,os
import requests,subprocess
import config
INFO=config.PATHS['info']
IMG_PATH=config.PATHS['img']
del config;
from .esp import Esp
import pyautogui


print(INFO,__file__)
# from functions.config import config

aiy=None;
esp=Esp()

def change_name():

	newname=aiy.listenTime()

	if not newname:
		return -1
	elif len(newname)>15:return aiy.say("слишком длинное имя")
	elif len(newname)<4:return aiy.say("слишком короткое имя")
	else:
		with open(INFO,'r', encoding='utf-8') as f:
			info=json.loads(f.read());
		info['aiy']['name'] = newname;
		with open(INFO,'w', encoding='utf-8') as f:
			f.write(json.dumps(info,ensure_ascii=False))
		aiy.name=newname;
		return aiy.say("теперь меня зовут "+newname);
	return -1

def start_light():
	global esp;
	if not esp.check_state():
		return aiy.say('Нет подключения с модулем');
	if not esp.setDiod(1):
		return aiy.say("свет уже включен");
	return aiy.say("Включил");

def stop_light():
	global esp;
	if not esp.check_state():
		return aiy.say('Нет подключения с модулем');
	if esp.setDiod(0):
		return aiy.say("свет уже выключен");
	return aiy.say("Выключил");

def get_esp_data():
	global esp;
	data = esp.getData();
	if data==-1:
		return aiy.say('Нет подключения с модулем');
	res=f'Температура {data["t"]} Влажность {data["h"]} Уровень газа {data["g"]}';
	return aiy.say(res);

def do_reload():
	aiy.say('Перезапускаюсь');
	PATH = os.path.realpath(__file__)
	os.system('py scripts/reload.py --filename=assistant.py');
	do_bye()

	return aiy.say('Перезапускаюсь');

def do_sleep():
	return aiy.say('Засыпаю. нажмите на клавишу R для пробуждения');

def get_temp(done=None):
	try:
		res = subprocess.getoutput('sudo vcgencmd measure_temp');
		res="Температура "+str(re.search(r'\d+', res).group())+" градусов";
	except Exception as err:
		print("ERROR:",err);
		res = 'Произошла ошибка';
	return aiy.say(res);

def get_data(done=None):
	text = ''
	try:
		res = requests.get(config.PATH['urls']['esp']+"readData",timeout = 3)
		data = res.json();
		text += f'Температура {data["t"]} Влажность {data["h"]} Уровень газа {data["g"]}'
	except:
		text += "\nОшибка запроса"

	return aiy.say(text);

def get_time():
	now=datetime.datetime.now()
	return aiy.say(f'Сейчас {now.hour} : {now.minute}');

def do_screenshot(done=None):
	
	date_string = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
	pyautogui.screenshot(IMG_PATH+"image"+date_string+".jpg")
	return aiy.say("Выполнила");
def do_bye(done=None):
	aiy.say("Досвидание");
	while aiy.say_wait:
		time.sleep(0.1)
	sys.exit()
def make_func(func_obj):
	return eval(func_obj['func']+"()")
