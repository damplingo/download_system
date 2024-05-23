from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import psycopg2
import psycopg2.errors as pg2errors
import requests
import datetime

class Habr_resource(Resource):
    def get(self, id):
        try:
    # пытаемся подключиться к базе данных
            conn = psycopg2.connect(dbname='test_3', user='server', password='server', host='localhost', port='5432')
        except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
            print('Can`t establish connection to database')
            conn.close()
        ans = {}
        cur = conn.cursor() 
        query_find = 'SELECT COUNT (*) FROM Articles WHERE Art_id_hubr = ' + str(id) + ';'    
        cur.execute(query_find)
        count = cur.fetchone()[0]
        if count == 0:   
            return "no this id"
        else:
            query = 'SELECT Art_id_hubr, title, publication_date, content, tags, name FROM Articles JOIN Auth_art_id ON Auth_art_id.art_id = articles.id Join Authors ON Auth_art_id.auth_id = Authors.auth_id;'
            cur.execute(query)
            q_m = cur.fetchone()
            ans.update({'art_id': q_m[0]})
            ans.update({'title':q_m[1]})
            ans.update({'piblication_date':q_m[2]})
            ans.update({'content':q_m[3]})
            ans.update({'tags':q_m[4]})
            ans.update({'auth': q_m[5]})
        conn.close()
        return jsonify(ans)

class dates_resource(Resource):
    def get(self, date_after, date_before, max_lim):
        try:
    # пытаемся подключиться к базе данных
            conn = psycopg2.connect(dbname='test_3', user='server', password='server', host='localhost', port='5432')
        except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
            print('Can`t establish connection to database')
            conn.close()
        query = 'SELECT Art_id_hubr, title, publication_date, tags, name FROM Articles JOIN Auth_art_id ON Auth_art_id.art_id = articles.id Join Authors ON Auth_art_id.auth_id = Authors.auth_id WHERE (Articles.publication_date > '+ '$$'+date_after+'$$'+'AND  Articles.publication_date <' + '$$'+date_before +'$$) ' +'LIMIT '+ str(max_lim)+';'
             
        cur = conn.cursor()
        cur.execute(query)
        q_m = cur.fetchall()
        res = {}
        list = []
        res.update({'count':len(q_m)})

        for i in q_m :
            loc={}
            loc.update({'art_id':i[0]})
            loc.update({'title':i[1]})
            loc.update({'publication_date': str(i[2])})
            loc.update({'tags':i[3]})
            loc.update({'auth_name':i[4]})
            list.append(loc)
        res.update({'list':list}) 
        conn.close()   
        return res
    
class one_date_resource(Resource):
    def get(self, date, max_lim):
        try:
# пытаемся подключиться к базе данных
            conn = psycopg2.connect(dbname='test_3', user='server', password='server', host='localhost', port='5432')
        except:
# в случае сбоя подключения будет выведено сообщение в STDOUT
            print('Can`t establish connection to database')
            conn.close()
        query =   'SELECT Art_id_hubr, title, publication_date, tags, name FROM Articles JOIN Auth_art_id ON Auth_art_id.art_id = articles.id Join Authors ON Auth_art_id.auth_id = Authors.auth_id WHERE (date(Articles.publication_date) = '+ 'date($$'+date+'$$)'+')' +'LIMIT '+ str(max_lim)+';'
        cur = conn.cursor()
        cur.execute(query)
        q_m = cur.fetchall()
        res = {}
        list = []
        res.update({'count':len(q_m)})

        for i in q_m :
            loc={}
            loc.update({'art_id':i[0]})
            loc.update({'title':i[1]})
            loc.update({'publication_date': str(i[2])})
            loc.update({'tags':i[3]})
            loc.update({'auth_name':i[4]})
            list.append(loc)
        res.update({'list':list})
        conn.close()    
        return res 

class authors_resource(Resource):
    def get(self, author_name):
        if author_name[-1] != ' ':
            author_name= author_name + ' '
        try:
# пытаемся подключиться к базе данных
            conn = psycopg2.connect(dbname='test_3', user='server', password='server', host='localhost', port='5432')
        except:
# в случае сбоя подключения будет выведено сообщение в STDOUT
            print('Can`t establish connection to database')
            conn.close()   
        cur = conn.cursor()    
        query_a = 'SELECT auth_id, name, registration_date FROM Authors WHERE name = '+'$$'+author_name+'$$;'
        print(query_a)
        res = {}
        cur.execute(query_a)
        qf_m = cur.fetchone()
        res.update({'auth_id':qf_m[0]})
        res.update({'name':qf_m[1]})
        res.update({'registration_date':str(qf_m[2])})
        query = 'SELECT Art_id_hubr, title, publication_date, tags FROM Articles JOIN Auth_art_id ON Auth_art_id.art_id = articles.id Join Authors ON Auth_art_id.auth_id = Authors.auth_id WHERE Authors.name = '+'$$'+author_name+'$$' ';'
        print(query)
        list = []
        cur.execute(query)
        q_m = cur.fetchall()
        res.update({'count':len(q_m)})
        for i in q_m :
            loc={}
            loc.update({'art_id':i[0]})
            loc.update({'title':i[1]})
            loc.update({'publication_date': str(i[2])})
            loc.update({'tags':i[3]})
            list.append(loc)
        res.update({'list':list})
        conn.close()
        return res    



            
app = Flask(__name__)
api = Api(app)
api.add_resource(Habr_resource, "/articles/<int:id>")
api.add_resource(dates_resource,"/articles/<string:date_after>/<string:date_before>/<int:max_lim>")
api.add_resource(one_date_resource, "/articles/<string:date>/<int:max_lim>")
api.add_resource(authors_resource, "/authors/<string:author_name>")
app.run(debug=True)



