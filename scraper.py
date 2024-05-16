import requests
from bs4 import BeautifulSoup

#scraping logic

#link - a->class<tm-title__link>

def articles_data(rel_url):
    abs_url = 'https://habr.com' + rel_url
    page = requests.get(abs_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    data = {}

    id = rel_url.split('/')
    data.update({'art_id':id[-2]})
    title = soup.find('meta', property='og:title')
    if (title is not None) :
        data.update({'art_name': title.get('content')})
    date = soup.find('time')
    if (date is not None):
        data.update({'publication_date': date.get('datetime')})
     
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
       
    return data


page = requests.get('https://habr.com/ru/articles/')
soup = BeautifulSoup(page.text, 'html.parser')
#поиск ссылок на главной странице
main_page = []
main_page = soup.find_all('a', class_ = 'tm-title__link')
all_text, all_link = [], [],
for data in main_page:
    if data.find('span') is not None:
        all_text.append(data.text)
        all_link.append(data.get('href'))

print('cicle')



for i in all_link:
     art = articles_data(i)
     print(art)
#     print(art)
    # url = 'https://habr.com' + i
    # article_page = requests.get(url)
    # s = BeautifulSoup(article_page.text, 'html.parser')
    # date = s.find('time')#берем первый элемент, тк далее в тексте страницы встречаем другие даты(например дату регистрации компании)
    # print(url)
    # auth = s.find('a', class_ = 'tm-user-info__username') #may be None
    # if (auth is not None):
    #     print(auth)
    #     print(auth.text)
    #     print(auth.get('href'))
    
    # publication_dates.append(date.get('datetime'))
    
    



