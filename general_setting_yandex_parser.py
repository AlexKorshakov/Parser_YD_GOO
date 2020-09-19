import inspect
import os
from datetime import datetime
from random import choice

timeout = 180
max_proxies = 25  # максимальное кооличество прокси
request_timeout = 10.24

HOST: str = 'https://yandex.ru'

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
base_url_yandex: str = f'https://www.yandex.ru/search/ads?text='

date_today = datetime.today().strftime("%d.%m.%Y")
full_path = current_dir + '\\'
extension = '.xlsx'

# задаём полный путь к файлу с выгрузкой
report_name = '\Parser_Yandex.xlsx'

# задаём полный путь к файлу с ключами
queries_path = 'queries.txt'

proxy_path = 'proxieslist.txt'

# задаём максимальное кооличество запросов
url_max_pos_yandex = 2

# Задаём регион. Санкт-Петербург – 2. Краснодар  - 35
# Список идентификаторов российских регионов https://tech.yandex.ru/xml/doc/dg/reference/regions-docpage/
region_yandex = 35
region_google = '+' + 'Краснодар'

# период
# 1 – последние две недели;
# 2 – последний месяц;
# 3 – три месяца;
# 4 – полгода;
# 5 – год;
# 7 – текущие сутки(даже если новый день наступил пару минут назад, поиск будет
# ограничен именно этой парой минут);
# 77 – сутки(24 часа, независимо от того, сколько длятся секущие сутки);
# 8 – трое суток;
# 9 – неделя
within_time = 5

# колличество ссылок в каждой выдаче
num_doc = 10  # не рекомендуется менять от слова совсем
# – определяет количество документов (ссылок), отображаемых на одной странице результатов выдачи.
#  по умолчанию = 10
# колличество одновременных процессов / потоков
max_process = 1

# параметры парсинга ответов

soup_name = 'li'
soup_class = 'serp-item'
soup_attribute = 'text'
