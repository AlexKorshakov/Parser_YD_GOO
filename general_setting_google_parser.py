import inspect
import os
from datetime import datetime
from random import choice

timeout = 180
max_proxies = 25  # максимальное кооличество прокси
request_timeout = 10.24

HOST: str = 'https://google.com'

agents = ['Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0']
# 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)',
# 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)',
# 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)',
# 'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)']

kad_head = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': HOST,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': choice(agents)}

HEADERS = {'Accept': '*/*',
           'Connection': 'keep-alive',
           'Upgrade-Insecure-Requests': '1',
           'Cache-Control': 'max-age=0',
           'host': HOST,
           'User-Agent': choice(agents)}

HEADERS_TEST = {'Accept': '*/*',
                'User-Agent': choice(agents)}

headers_tab = {'rowNom': 'п\п',  # i_row
               'ques': 'Ключ',  # url_ques
               'company_title': 'Заголовок',  # my_company_title
               'company_cid': 'Позиция',  # my_company_cid
               'company_link_1': 'Домен',  # my_company_link_1
               'company_sitelinks': 'Быстрая',  # my_company_site_links
               'company_text': 'Текст',  # my_company_text
               'company_contact': 'Контакты'}

current_dir = str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

# базовый запрос
base_url_google: str = f'https://www.google.com/search'

date_today: str = datetime.today().strftime("%d.%m.%Y")
full_path: str = current_dir + '\\'
extension: str = '.xlsx'

# задаём полный путь к файлу с выгрузкой
report_name: str = '\Parser_Google.xlsx'

# задаём полный путь к файлу с ключами
queries_path: str = 'queries.txt'

# задаём полный путь к файлу с прокси
proxy_path: str = 'proxyeslist.txt'

# задаём максимальное кооличество запросов

url_max_pos_google = 2

region_google = '+' + 'Краснодар'

# параметры парсинга ответов

soup_name = 'li'
soup_class = 'ads-fr'
soup_attribute = 'text'
