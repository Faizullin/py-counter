# Функция которая ищет во фразе имя бота
def isbotname(x):
    if('лиле' in x.lower() or 'реле' in x.lower() or 'вилли' in x.lower() or 'билет' in x.lower() or 'билли' in x.lower()  or 'лили' in x.lower() or x.lower()[:4]=='или ' or 'лидия' in x.lower() or 'ливия' in x.lower() or 'лилия' in x.lower() or 'лиля' in x.lower() or 'диля' in x.lower()):
        s=x.replace('Лилия','')
        s=s.replace('лилия','')
        s=x.replace('Ливия','')
        s=s.replace('ливия','')
        s=x.replace('Лидия','')
        s=s.replace('лидия','')
        s=s.replace('лили','')
        s=s.replace('Лили','')
        s=s.replace('Диля','')
        s=s.replace('Лиля','')
        s=s.replace('лиля','')
        s=s.replace('диля','')
        s=s.replace('реле','')
        s=s.replace('вилли','')
        s=s.replace('билет','')
        s=s.replace('Или','')
        s=s.replace('или','')
        s=s.replace('Лиле','')
        s=s.replace('лиле','')
        s=s.strip()
        return s
    else:
        return None
