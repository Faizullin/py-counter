import os,webbrowser,config,socket
this_host=socket.gethostbyname(socket.gethostname())
os.system("py -3.8 main.py --telegram=1  --esp_update=1 --fire_predict=1");#

#webbrowser.open_new("http://"+this_host+":5000")
