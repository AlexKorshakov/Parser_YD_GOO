from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn
from Servises.Notify_by_Message import l_message


def get_my_company_title(DIV):
    """Найти и вернуть название компании"""

    try:
        my_company_title: str = DIV.text.replace('Почему мне показано это объявление?', '')
        l_message(gfn(), f'company_title {my_company_title}', color=Nm.bcolors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
        my_company_title: str = 'N\A'

    return my_company_title


def get_my_company_cid(iroW=None):
    """Найти и вернуть порядковый номер компании на странице."""

    try:
        my_company_cid: str = str(iroW - 1)
        l_message(gfn(), f'company_cid {my_company_cid}', color=Nm.bcolors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
        my_company_cid: str = ''

    return my_company_cid


def get_my_company_contact(DIV):
    """Найти и вернуть контакты компании."""

    try:
        my_company_contact: str = 'N\A'
        l_message(gfn(), f'company_contact {my_company_contact}', color=Nm.bcolors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
        my_company_contact: str = 'N\A'

    return my_company_contact


def get_my_company_text(DIV):
    """Найти и вернуть описание компании."""

    try:
        my_company_text: str = DIV.find('div', attrs={'class': 'MUxGbd yDYNvb lyLwlc'}).text.strip()
        l_message(gfn(), f'company_text  {my_company_text}', color=Nm.bcolors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
        my_company_text: str = ''

    return my_company_text


def get_my_company_site_links(DIV):
    """Найти и вернуть ссылку на сайт компании."""

    try:
        get_my_company_site_link: str = DIV.find('cite', attrs={'class': 'iUh30 bc tjvcx'})
        l_message(gfn(), f'company_site_links  {get_my_company_site_link}', color=Nm.bcolors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
        get_my_company_site_link: str = 'N\A'

    return get_my_company_site_link


def get_my_company_link_1(DIV):
    """Найти и вернуть быструю ссылку на сайт компании."""

    try:
        my_company_link_1: str = DIV.find('span', attrs={'class': 'gBIQub KETUZd qzEoUe'}).text
        x: int = my_company_link_1.index('/')
        my_company_link_1 = my_company_link_1[0:x]
        l_message(gfn(), f'company_link_1 {my_company_link_1}', color=Nm.bcolors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
        my_company_link_1: str = ''

    return my_company_link_1
