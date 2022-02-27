import sqlite3

class Sql:
    def __init__(self,config = None):
        self.filename= config.PATHS['db'];
        self.table   = config.DB_NAME;
        del config
    def insert(self,row,condition=''):
        if type(row) is str:
            return self.execute(row)
        keys = tuple([c for c in row.keys()])
        vals = tuple([c for c in row.values()])
        command='INSERT INTO {} {} VALUES{} {}'.format(self.table,keys,vals,condition)
        print(command)
        return self.execute(command);

    def update(self,key,val,condition=''):
        if type(val) is str: val=f'\'{val}\''
        command='UPDATE {} SET {} = {} {}'.format(self.table,key,val,condition)
        return self.execute(command);

    def delete(self,condition=''):
        return self.execute('DELETE FROM {} {}'.format(self.table,condition));

    def execute(self,text):
        with sqlite3.connect(self.filename) as f:
            data=f.cursor().execute(text)
            f.commit();
        return data;

    def select(self,el='*',condition='',_to_dict=False):
        command ='SELECT {} FROM {} {}'.format(el,self.table,condition)
        with sqlite3.connect(self.filename) as f:
            if _to_dict:f.row_factory = sqlite3.Row
            data = f.cursor().execute(command).fetchall();
        return data

    def description(self):
        desc = self.execute('SELECT * FROM {}'.format(self.table)).description;
        return [i[0] for i in desc];

    def convert_to_char(self,dataset):
        dataset_label=[];
        dataset_datasets={'gas':[],'count':[],'temp':[],'hum':[]}
        for i in dataset:
            dataset_label.append(int(i[0]))
            dataset_datasets['count'].append(int(i[1]));dataset_datasets['gas'].append(int(i[2]))
            dataset_datasets['temp'].append(int(i[3]));dataset_datasets['hum'].append(int(i[4]))
        return dataset_label,dataset_datasets


    def get_complete_data(self,args=None):
        el=None;res=None
        if args and ('selected_date' in args and 'type' in args):
            
            selected_date = args['selected_date']
            if args['type']=='day':
                el='strftime(\'%H\',created_datetime),count,gas,temp,hum,date(created_datetime)'
                condition='WHERE date(created_datetime)=\'{}\''.format(selected_date)
            elif args['type']=='month':
                condition="WHERE strftime(\'%Y-%m\',created_datetime)=\'{}\' GROUP BY date(created_datetime)".format(selected_date)
                el='strftime(\'%d\',created_datetime),avg(count),avg(gas),avg(temp),avg(hum),strftime(\'%Y-%m\',created_datetime)'
        else:
            condition="GROUP BY date(created_datetime)  ORDER BY date(created_datetime) DESC LIMIT 1"#HAVING count(*)>2
            selected_date = self.select('date(created_datetime)',condition)
            print(selected_date)
            if selected_date:
                selected_date=selected_date[0][0]
                condition='WHERE date(created_datetime)=\'{}\''.format(selected_date)
                el = 'strftime(\'%H\',created_datetime),count,gas,temp,hum,date(created_datetime)'
        if not el:
            return False
        res=self.select(el,condition);
        print(res)
        return {
            'data_links':{
                'month':{
                    'data':self.select('strftime(\'%Y-%m\',created_datetime)','GROUP BY strftime(\'%Y-%m\',created_datetime) ORDER BY date(created_datetime) DESC'),
                    'name':'За месяц'},
                'day':{
                    'data':self.select('date(created_datetime)','GROUP BY date(created_datetime) ORDER BY date(created_datetime) DESC'),
                    'name':'За день'}
            },
            'res':False if not res else self.convert_to_char(res),
            'selected_date':selected_date
        };