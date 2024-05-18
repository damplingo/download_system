from imghdr import what
import requests
from bs4 import BeautifulSoup
import psycopg2
import os
import sys
import psycopg2.errors as pg2errors


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
    next = soup.find_all('a', class_ = 'tm-pagination__page')
    next_url = 'https://habr.com'
    if (number == 1):
        next_url += next[0].get('href')
    elif number < 50:
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
    data.update({'content':text})


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
        if (data.get('art_name') is not None):
            title =  data.get('art_name')
        tag_mas = data.get('tags').split(',')
        tag_text = ''
        for i in tag_mas:
            tag_text += '$$'
            tag_text += i
            tag_text += '$$'
            tag_text += ','
        tag_text = tag_text[:-1]         
        add_article_query = "INSERT INTO Articles VALUES("+ data.get('art_id') + ', $$'+title + '$$, $$' + data.get('publication_date') + '$$, $$'+data.get('content') + '$$ ,' + 'ARRAY['+ tag_text + "]);"
        print(add_article_query)
        cur = conn.cursor()
        cur.execute(add_article_query)
        conn.commit()
        cur.close()
        # with conn.cursor as curs:
        #     curs.execute(add_article_query)
        #     conn.commit()
        conn.close()

    except psycopg2.OperationalError as _ex:
        print('ну что-то не так пошло, закроем подключение')
        conn.close()    



#main
#main_pages_pars('https://habr.com/ru/', 1)


data = articles_data('/ru/companies/testograf/articles/815249/')

save_data(data)







    
    



