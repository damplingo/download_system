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
            conn = psycopg2.connect(dbname='test', user='server', password='server', host='localhost', port='5432')
        except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
            print('Can`t establish connection to database')
            conn.close()
        ans = {}
        cur = conn.cursor() 
        query_find = 'SELECT COUNT (*) FROM Articles WHERE art_id = ' + str(id) + ';'    
        cur.execute(query_find)
        count = cur.fetchone()[0]
        if count == 0:   
            return "no this id"
        else:
            query = 'SELECT Articles.art_id, title, publication_date, content, tags, name FROM Articles JOIN Auth_art_id ON Auth_art_id.art_id = articles.art_id Join Authors ON Auth_art_id.auth_id = Authors.auth_id;'
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

class date_resource(Resource):
    def get(self, date_after, date_before, max_lim):
        try:
    # пытаемся подключиться к базе данных
            conn = psycopg2.connect(dbname='test', user='server', password='server', host='localhost', port='5432')
        except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
            print('Can`t establish connection to database')
            conn.close()
        query = 'SELECT Articles.art_id, title, publication_date, tags, name FROM Articles JOIN Auth_art_id ON Auth_art_id.art_id = articles.art_id Join Authors ON Auth_art_id.auth_id = Authors.auth_id WHERE (Articles.publication_date > '+ '$$'+date_after+'$$'+'AND  Articles.publication_date <' + '$$'+date_before +'$$) ' +'LIMIT '+ str(max_lim)+';'
             
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
        return res
app = Flask(__name__)
api = Api(app)
api.add_resource(Habr_resource, "/articles/<int:id>")
api.add_resource(date_resource,"/articles/<string:date_after>/<string:date_before>/<int:max_lim>")
app.run(debug=True)



