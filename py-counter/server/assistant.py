import subprocess, sys
from fuzzywuzzy import fuzz
from vosk import Model, KaldiRecognizer
import os, json, re, threading, signal, shutil, time
from src.botname import isbotname
import src.functions as functions
from src.dop import die,tr
import pyaudio,pyttsx3
import config

PERMISSIONS={
    "SAY":True
}
oldtime=None
sluh=0
stoptime=60
print(__file__)

WORDS = config.PATHS['vosk']+'words/'


def getanswer(text):
    text=text.lower().strip()
    a=0;n=0;nn=0;
    with open(WORDS+'boltun.json','r', encoding='utf-8') as file:
        mas=json.loads(file.read());
    for i in mas['plot']:
        for i_text in i['text']:
            aa=(fuzz.token_sort_ratio(i_text, text));
            if(aa>a and aa!=a):
                a=aa
                nn=n
        n+=1
    if a>=80:
        return mas['plot'][nn]['type'],mas['plot'][nn]
    nn=0;a=0;n=0;
    with open(WORDS+'boltun.txt','r', encoding='utf-8') as file:
        mas=file.read().split('\n')
        for q in mas:
            if('u: ' in q):
                aa=(fuzz.token_sort_ratio(q.replace('u: ',''), text))
                if(aa>a and aa!=a):
                    a=aa
                    nn=n
            n=n+1
        if a>70:
            return None,mas[nn+1]
    return None,'Нет ответа'



class Assistant():
    say_wait=False
    stoptime=20
    sluh=True
    def __init__(self,rec):
        
        def getName():
            with open(config.PATHS['info'],'r', encoding='utf-8') as f:
                self.name =json.loads(f.read())['aiy']['name'];
        tr(getName,is_die=True,is_exit=True)
        #tr(getName,is_die=True,is_exit=True)
        self.rec=rec
        self.stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        print("stream")
        self.oldtime=int(time.time())
        functions.aiy=self;
        print('Чтобы активировать распознвание речи скажите фразу с именем "'+self.name+'"');
        if not PERMISSIONS["SAY"]:
            self.say = self.void_function;
    def say(self,text):
        self.say_wait=True
        engine = pyttsx3.init()
        engine.say(str(text))
        engine.runAndWait()
        self.say_wait=False
        return text;
    def void_function(self,text):
        print(text)

    def start(self):
        t1=threading.Thread(target=self.run,daemon=True)
        t1.start()
        t2=threading.Thread(target=self.tick,daemon=True)
        t2.start()
        t1.join()
        
    def run(self):
        self.stream.start_stream()
        while True:
            text = self.listen()
            print('Вы: '+text)
            ans=getanswer(text)
            if ans[0] =='f':
                print(functions.make_func(ans[1]));
            elif ans[0]=='ans':
                if ans[1]=='bye':
                    break
            else:
                self.say(ans[1])

    def listen(self):
        while True:
            if(self.say_wait):
                continue
            data = self.stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                continue
            if rec.AcceptWaveform(data):
                x=json.loads(rec.Result())["text"].lower()
                
                if len(x)>1 and (self.sluh==True or self.isName(x)):

                    self.oldtime=int(time.time());self.sluh=True;
                    return x.replace(self.name,'').strip();
    def listenTime(self,delay=10):
        l=True;
        def stopL(delay):
            time.sleep(delay)
            l=False
        self.say("слушаю")
        threading.Thread(target=stopL,args=(delay,),daemon=True).start()
        while l:
            data = self.stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                continue
            if rec.AcceptWaveform(data):
                x=json.loads(rec.Result())["text"].lower()
                if len(x)>1:
                    self.oldtime=int(time.time());self.sluh=True;
                    return x;
        return None
    
    def tick(self):
        while True:
            razn=int(time.time())-self.oldtime
            if(razn>self.stoptime and self.sluh==True):
                self.sluh=False
                print('Лилия больше вас не слушает. Окликните её по имени, чтобы продолжить беседу.')
            time.sleep(1.5)
    def isName(self,text):
        print('check namf')
        if self.name in text:
            return True
        return False
    def __del__(self):
        print("END")
            

stopf=0
stop2=0
model = None
rec = None
try:
	model = Model(config.PATHS['vosk']+'model')
	rec = KaldiRecognizer(model, 16000)
except Exception as err:
	print(err)
	print("ERROR")
	sys.exit()
p = pyaudio.PyAudio()
#stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)


# def say(mytext):
#     global sluh
#     global stop2
#     global stopf
#     global oldtime
#     stop2=0
#     stopf=1
#     mastexts=getpr(mytext)
#     for stroka in mastexts:
#         if(len(stroka)>=2):
#             synthesis_input = texttospeech.SynthesisInput(text=stroka)
#             response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
#             fname='mp3/'+re.sub('[^А-Яа-я]', '', stroka)+'.mp3'
#             if not os.path.exists(fname):
#                 with open(fname, "wb") as out:
#                     out.write(response.audio_content)
#             mixer.music.load(fname)
#             mixer.music.play()
#             while mixer.music.get_busy() and stop2!=1:
#                 time.sleep(0.1)
#             if(stop2==1):
#                 mixer.music.stop()
#                 stopf=0
#                 break
#     stopf=0
#     sluh=1
#     oldtime=int(time.time())
#     print('Сейчас Лилия слушает вас. можно не окликать ее по имени, а просто говорить вслух что-либо')
    

#mixer.stop()
#mixer.quit()  


def listencommand():
    global sluh
    global stop2
    global stopf
    print('Запущено распознавание с микрофона')
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()
    while True:
        if(stopf==0):
            data = stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                continue
            if rec.AcceptWaveform(data):
                # Получили распознанную с микрофона фразу
                x=json.loads(rec.Result())["text"].lower()
                if len(x)>1:
                    print('Вы: '+x)
                if (isbotname(x)!=None or sluh==1) and len(x)>1:
                    oldtime=int(time.time())
                    sluh=1
                    if(isbotname(x)!=None):
                        #otv=myvopros(isbotname(x))
                        print(getanswer(isbotname(x)))
                    else:
                        print(getanswer(x))
                        #otv=myvopros(x)
                    #print('Лилия: '+otv)
                    #say(otv+'.')

if __name__=='__main__':
    print("START");
    Assistant(rec).start();



