import re, os,json,time
from fuzzywuzzy import fuzz

def getanswer(text):
    try:
        text=text.lower().strip()       
        a=0
        n=0
        nn=0
        t1=time.time()
        with open('boltun.json','r', encoding='utf-8') as file:
            mas=json.loads(file.read())
            print(mas)
        for i in mas['plot']
            for i_text in i['text']:
                aa=(fuzz.token_sort_ratio(i_text, text));
                if(aa>a and aa!=a):
                    a=aa
                    nn=n
            n+=1;
        s=mas['plot'][nn]
        # with open('boltun.txt','r', encoding='utf-8') as file:
        #     mas=file.read().split('\n')
        
        # for q in mas:
        #     if('u: ' in q):
        #         aa=(fuzz.token_sort_ratio(q.replace('u: ',''), text))
        #         if(aa>a and aa!=a):
        #             a=aa
        #             nn=n
        #     n=n+1
        t2=time.time()
        #s=mas[nn+1]
        print(t2-t1)
        return s
    except:
        return 'Нет ответа'

