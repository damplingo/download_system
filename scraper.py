from pickle import FALSE, TRUE
import requests
from bs4 import BeautifulSoup
import os
import sys

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
    if (number <= 50):
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
        data.update({'publication_date': date.get('datetime')})
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

    # text = soup.find('div', class_ = 'tm-article-body').text
    # data.update({'content':text})
    return data


#main_pages_pars('https://habr.com/ru/articles/page17/')
#main
try :
     page = requests.get('https://habr.com/ru/articles/page17/')
     soup = BeautifulSoup(page.text, 'html.parser')
except requests.exceptions.InvalidSchema:
    print('исправь пж ссылку как-то')#сработает только на первую часть ссылки
    sys.exit(1)
 #поиск ссылок на главной странице
test = soup.find('a', class_ = 'tm-pagination__page')#беру первый элмент тк дальше под тем  же классом ссылка на 49, 50 страницу
print(test.get('href'))
main_page = []
main_page = soup.find_all('a', class_ = 'tm-title__link')
all_text, all_link = [], []
for data in main_page:
    if data.find('span') is not None:
        all_text.append(data.text)
        all_link.append(data.get('href'))
for i in all_link:
         print(i)
         art = articles_data(i)





    
    



