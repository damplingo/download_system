from imghdr import what
import requests
from bs4 import BeautifulSoup
import psycopg2
import os
import sys
import psycopg2.errors as pg2errors
import hashlib


#scraping logic

#link - a->class<tm-title__link>
#функция, работающая с главной страницей
def main_pages_pars(main_url, number):
    try :
        page = requests.get(main_url)
        soup = BeautifulSoup(page.text, 'html.parser')
    except requests.exceptions.InvalidSchema:
        print('исправь пж ссылку как-то')#сработает только на первую часть ссылки
        sys.exit(1)
    #поиск ссылок на главной странице
    main_page = []
    main_page = soup.find_all('a', class_ = 'tm-title__link')
    all_text, all_link = [], []
    for data in main_page:
        if data.find('span') is not None:
            all_text.append(data.text)
            all_link.append(data.get('href'))
    
    for i in all_link:
         art = articles_data(i)
         save_data(art)
    next = soup.find_all('a', class_ = 'tm-pagination__page')
    next_url = 'https://habr.com'
    if (number == 1):
        next_url += next[0].get('href')
    elif number < 5:
        for i in next:#следующую ссылку после такой же как у нас
            
            if (int(i.text) == number+1):
                next_url +=i.get('href')
                break

    print(next_url)
    # print(number)
    number += 1
    if (number <= 5):
        main_pages_pars(next_url, number)
        
    

#функция, получающая на вход ссылку на статью и собирающая необходимую информацию о ней
def articles_data(rel_url):
    abs_url = 'https://habr.com' + rel_url
    page = requests.get(abs_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    data = {}
    error = soup.find('div', class_ = 'tm-error-message')#проверка на то есть ли доступ к статье - бывает, что в ссылках остается статья, к которой автор закрыл доступ
    if (error is not None):
        return data
    id = rel_url.split('/')
    data.update({'art_id':id[-2]})
    title = soup.find('meta', property='og:title')
    if (title is not None) :
        data.update({'art_name': title.get('content')})
        print(title.get('content'))
    date = soup.find('span', class_ = 'tm-article-datetime-published').time
    if (date is not None):
        data.update({'publication_date': date.get('title')})
#auth_inform
    auth = soup.find('a', class_ = 'tm-user-info__username') #may be None

    if (auth is not None):
        data.update({'auth_name': auth.text})
        auth_url = 'https://habr.com' + auth.get('href')
        a_page = requests.get(auth_url)
        a_soup = BeautifulSoup(a_page.text, 'html.parser')
        a_dt = a_soup.find_all('dt')
        a_dd = a_soup.find_all('dd')
        for i in range(len(a_dd)):
            if (a_dt[i].text== ' Зарегистрирован ' or a_dt[i].text== ' Зарегистрирована ') :
                data.update({'registration_date':a_dd[i].time.get('datetime')})

    #text of article 

    text = soup.find('div', class_ = 'tm-article-body').text
    new_text = ''
    text = text.split('.')
    for i in text:
        new_text += i
        new_text += "\n"
    data.update({'content':new_text})


    #тэги
    tags = soup.find_all('meta')
    
    for i in tags:
        if (i.get('name') == 'keywords') :
            print(i.get('content'))
            data.update({'tags':i.get('content')})

    return data


def save_data(data) :
    try:
    # пытаемся подключиться к базе данных
        conn = psycopg2.connect(dbname='test', user='pi', password='12345', host='localhost', port='5432')
    except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
        print('Can`t establish connection to database')
        conn.close()  
    try:
        title = ''
        update_queries = []
        insert_queries = []    
        if (data.get('art_name') is not None):
            title =  data.get('art_name')
        tag_mas = data.get('tags').split(',')
        tag_text = ''
        auth_name = data.get('auth_name')
        art_id = data.get('art_id')
        hash_object = hashlib.md5((auth_name + art_id).encode())
        hash = hash_object.hexdigest()
        for i in tag_mas:
            tag_text += '$$'
            tag_text += i
            tag_text += '$$'
            tag_text += ','
        tag_text = tag_text[:-1]        
        add_article_query = "INSERT INTO Articles VALUES("+ art_id + ', $$'+title + '$$, $$' + data.get('publication_date') + '$$, $$'+data.get('content') + '$$ ,' + 'ARRAY['+ tag_text + "]);"
        update_article_query = 'UPDATE Articles SET (Title, publication_date, content, tags) ='+'($$'+title + '$$, $$' + data.get('publication_date') + '$$, $$'+data.get('content') + '$$ ,' + 'ARRAY['+ tag_text + "])" + "WHERE art_id="+art_id+";"
        cur = conn.cursor()
        insert_queries.append(add_article_query)
        update_queries.append(update_article_query)
        # cur.execute(add_article_query)
        # conn.commit()
        
        if data.get('auth_name') is not None:
            registration_date = 'NULL'
            auth_name = data.get('auth_name')
            if exist_author(cur, auth_name) :#не нужно проверять на полный дубликат, просто проверяем нет ли автора
                hash_object = hashlib.md5((auth_name + art_id).encode())
                hash = hash_object.hexdigest()

                if data.get('registration_date') is not None:
                    registration_date = data.get('registration_date')
                add_auth_query = 'INSERT INTO Authors(name, registration_date) VALUES(' + '$$' + auth_name + '$$, $$'+ registration_date + '$$) RETURNING auth_id;'
                cur.execute(add_auth_query)
                auth_id = cur.fetchone()[0]
                
                add_auth_art_id_query = "INSERT INTO Auth_art_id(art_id, auth_id, hash) VALUES(" + str(art_id) + ',' + str(auth_id) +','+ '$$'+hash +'$$' +');'
                insert_queries.append(add_auth_art_id_query)
                # cur.execute(add_auth_art_id_query)
                # conn.commit()


        elif data.get('auth_name') is None:
            hash_object = hashlib.md5((art_id+'null').encode)
            hash = hash_object.hexdigest()
            auth_id = -1 #default
            add_auth_art_id_query =  "INSERT INTO Auth_art_id(art_id, auth_id, hash) VALUES(" + str(art_id) + ',' + str(auth_id) +','+ hash +');'
            insert_queries.append(add_auth_art_id_query)   
            # cur.execute(add_auth_art_id_query)
            # conn.commit()
        
        print(hash)
        if is_dublicate(cur, hash):
            print('dublicate')
            for i in update_queries:
                #print(i)
                cur.execute(i)
                conn.commit()

        else:
            print('not dublicate')
            for j in insert_queries:
                #print(j)
                cur.execute(j)
                conn.commit()       
        cur.close()
        # with conn.cursor as curs:
        #     curs.execute(add_article_query)
        #     conn.commit()

        
        conn.close()

        
    except psycopg2.OperationalError as _ex:
        print('ну что-то не так пошло, закроем подключение')
        conn.close()    
    except psycopg2.errors.UniqueViolation as ex:
        print('not_uniq value')
        conn.close()

def is_dublicate(cur, hash):
    print(hash)
    query = 'SELECT COUNT (*) FROM Auth_art_id WHERE hash = ' + '$$'+hash+'$$;'
    cur.execute(query)
    count = cur.fetchone()[0]

    print('count')
    print(count)

    if count == 0:
        return False
    elif count == 1:
        return True
    else:
        print('problems')

def exist_author(cur, auth_name):
    query = 'SELECT COUNT (*) FROM Authors WHERE name =' + '$$' + auth_name + '$$;'
    cur.execute(query)
    count = cur.fetchone()[0]

    if count == 0:
        print('can append auth')
        return True
    elif count == 1:
        print('already exist this auth')
        return False


#main
main_pages_pars('https://habr.com/ru/', 1)

#data = articles_data('/ru/companies/otus/articles/814041/')

#save_data(data)







    
    



