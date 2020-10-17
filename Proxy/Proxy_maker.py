import asyncio
import multiprocessing
import random
import time
import requests
from proxybroker import Broker
from requests.exceptions import ConnectTimeout, ProxyError
from requests.sessions import Session

from Parser_Google import general_setting_google_parser as gs
from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn
from Servises.Notify_by_Message import l_message

print(f'Invoking __init__.py for {__name__}')

PROXIES_LIST: str = str(gs.current_dir) + r'\proxyeslist.txt'
PROXIES: str = str(gs.current_dir) + r'\proxies.txt'


async def save_proxies(proxies, filename: str):
    """ Сохраняем прокси от Broker в файл PROXIES
        :param proxies: найденный Broker прокси: object
        :param filename: полный путь к файлу для записи и хранения прокси: str
    """
    l_message(gfn(), f'proxyes {proxies}', color=Nm.BColors.OKBLUE)
    with open(filename, 'w') as file:
        while True:
            proxy = await proxies.get()
            if proxy is None:
                break
            proto = 'https' if 'HTTPS' in proxy.types else 'http'
            row = f'{proto}://{proxy.host}:{proxy.port}\n'
            file.write(row)


def get_proxies(limit: int = 10):
    """ Собираем прокси с помощью proxybroker
        :return: proxies_list_get : список найденных прокси: list
        :param limit: лимит на колличество найденных прокси: int
    """
    loop = asyncio.get_event_loop()

    proxies = asyncio.Queue()
    broker = Broker(proxies, timeout=12, max_conn=200, max_tries=2, verify_ssl=False, loop=loop)
    tasks = asyncio.gather(broker.grab(countries=['RU'], limit=limit), save_proxies(proxies, filename=PROXIES))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)

    # записываем собранное в proxies_list_get
    with open(PROXIES, 'r') as prx_row:
        proxies_list_get = prx_row.read().split('\n')

    l_message(gfn(), f'proxies_list_get {str(proxies_list_get)}', color=Nm.BColors.OKBLUE)
    return proxies_list_get


def check_proxies(proxies_list: list):
    """ Проверяем список прокси
        :return: valid_proxies_list: возвращает список проверенных прокси: list
        :param proxies_list: лист с прокси для проверки : list
    """
    l_message(gfn(), f'proxies_list {str(proxies_list)}', color=Nm.BColors.OKBLUE)
    mgr = multiprocessing.Manager()
    valid_proxies_list: list = mgr.list()

    n_chunks: int = 4
    chunks = [proxies_list[i::n_chunks] for i in range(n_chunks)]

    parcs_list: list = []
    for chunk in chunks:
        chunk_p = multiprocessing.Process(target=check_proxy, args=(chunk, valid_proxies_list))
        parcs_list.append(chunk_p)
        chunk_p.start()

    for chunk_p in parcs_list:
        chunk_p.join()

    l_message(gfn(), f'valid_proxies_list {str(valid_proxies_list)}', color=Nm.BColors.OKBLUE)

    return valid_proxies_list


def check_proxy(proxies_for_check, valid_proxies):
    """ Проверяем каждый прокси
        :param proxies_for_check: список прокси для проверки прокси : list
        :param valid_proxies: список валидных прокси : list
    """
    session: Session = requests.Session()

    for nu_proxy in proxies_for_check:
        l_message(gfn(), f'nu_proxy {str(nu_proxy)}', color=Nm.BColors.OKBLUE)
        try:
            # time_rand(2, 3)  # задержка исполнеия
            request = session.get(gs.HOST, headers=gs.HEADERS_TEST, proxies={'http': nu_proxy, 'https': nu_proxy},
                                  timeout=gs.timeout)
            l_message(gfn(), f'request.status_code {str(request.status_code)}', color=Nm.BColors.OKBLUE)

            if check_request_status_code(request=request, url=nu_proxy):
                valid_proxies.append(nu_proxy)
                l_message(gfn(), f"valid_proxies {str(nu_proxy)} : {str(request.headers['Content-Type'])}",
                          color=Nm.BColors.OKBLUE)
                session.close()
                return valid_proxies
            else:
                session.close()

        except ProxyError as err:
            l_message(gfn(), f"ProxyError: {repr(err)}", color=Nm.BColors.FAIL)
            session.close()

        except ConnectTimeout as err:
            l_message(gfn(), f"ConnectTimeout: {repr(err)}", color=Nm.BColors.FAIL)
            session.close()

        except AttributeError as err:
            l_message(gfn(), f"AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
            session.close()

        except Exception as err:
            l_message(gfn(), f"Exception: {repr(err)}", color=Nm.BColors.FAIL)
            session.close()


def check_request_status_code(request, url) -> bool:
    """ Проверка кода ответа запроса.
    """
    if request.status_code == 200:  # если запрос был выполнен успешно то
        l_message(gfn(), 'Успешный запрос!', color=Nm.BColors.OKBLUE)
        return True

    elif request.status_code == 400:
        l_message(gfn(), f'BAD request {url} : {str(request.status_code)}', color=Nm.BColors.FAIL)
        return False

    elif 400 < request.status_code < 500:
        l_message(gfn(), f'Client Error {url} : {str(request.status_code)}', color=Nm.BColors.FAIL)
        return False

    elif 500 <= request.status_code < 600:
        l_message(gfn(), f'Server Error {url} : {str(request.status_code)}', color=Nm.BColors.FAIL)
        return False

    else:
        l_message(gfn(), f'Неудачный запрос! Ответ {str(request.status_code)} : {str(request.status_code)}',
                  color=Nm.BColors.FAIL)
        return False


def app_load_proxies_list(get_proxy: list):
    """ Добавляем проверенные прокси в proxies_list.
        :param get_proxy: добаляет список get_proxy в файл PROXIES_LIST: list
    """
    try:
        # добавляем прокси к уже проверенным
        with open(PROXIES_LIST, 'r') as file:
            proxies_list: list = file.read().split('\n')

    except Exception as err:
        l_message(gfn(), f"Exception: {repr(err)}", color=Nm.BColors.FAIL)
        # если файл пустой - обнуляем список
        proxies_list = []

    if proxies_list:
        get_proxy.extend(proxies_list)
    # преобразуев множество чтобы удалить повторы и обратно в list
    get_proxy = list(set(get_proxy))
    l_message(gfn(), f"{str(get_proxy)}", color=Nm.BColors.OKBLUE)

    with open(PROXIES_LIST, 'w') as file:
        file.write('\n'.join(get_proxy))


def time_rand(t_start: int = 1, t_stop: int = 30):
    """ Функция задержки выполнения кода на рандомный промежуток.
    """
    time_random = random.randint(t_start, t_stop)
    l_message(gfn(), f'Время ожидания нового запроса time_rand  {str(time_random)} sec', color=Nm.BColors.OKBLUE)

    for _ in range(time_random):
        time.sleep(random.uniform(0.8, 1.2))


def main():
    """ Основная функция
    """
    l_message(gfn(), '\n**** Start ****\n', color=Nm.BColors.OKBLUE)

    for _ in range(10):
        proxies_list_get = get_proxies(limit=gs.max_proxies)
        get_proxy = check_proxies(proxies_list_get)
        app_load_proxies_list(get_proxy)
        time_rand(10, 15)

    l_message(gfn(), '\n**** Done ****\n', color=Nm.BColors.OKBLUE)


if __name__ == '__main__':
    main()
