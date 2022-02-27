import requests
class Esp:
	def __init__(self,url='http://192.168.1.2'):
		self.url=url;
	#state=requests.get(self.url+'/led').text

	def check_state(self,timeout=2):
		try:
			res=requests.get(self.url,timeout=timeout);
			return res.status_code;
		except :
			return False;
	def tr(self,url):
		try:
			res=requests.get(url,timeout=timeout);
			return res;
		except :
			return False;

	def getData(self,timeout=2):
		res = self.tr(self.url+'/readData',timeout=timeout);
		if not res:
			return -1;
		return res.json();
			



	def setDiod(self,state):
		old_state = requests.get(self.url+'/led');
		if old_state=="1" and not state:
			requests.get(self.url+'/ledoff');
			return True;
		elif old_state=="0" and state:
			requests.get(self.url+'/ledon');
			return True;
		return False;