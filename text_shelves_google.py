from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn
from Servises.Notify_by_Message import l_message


def get_my_company_title(div):
    """Найти и вернуть название компании"""

    try:
        my_company_title: str = div.text.replace('Почему мне показано это объявление?', '')
        l_message(gfn(), f'company_title {my_company_title}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        my_company_title: str = 'N\A'

    return my_company_title


def get_my_company_cid(i_row=None):
    """Найти и вернуть порядковый номер компании на странице."""

    try:
        my_company_cid: str = str(i_row - 1)
        l_message(gfn(), f'company_cid {my_company_cid}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        my_company_cid: str = ''

    return my_company_cid


def get_my_company_contact(div=None):
    """Найти и вернуть контакты компании."""

    try:
        my_company_contact: str = 'N\A'
        l_message(gfn(), f'company_contact {my_company_contact}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        my_company_contact: str = 'N\A'

    return my_company_contact


def get_my_company_text(div):
    """Найти и вернуть описание компании."""

    try:
        my_company_text: str = div.find('div', attrs={'class': 'MUxGbd yDYNvb lyLwlc'}).text.strip()
        l_message(gfn(), f'company_text  {my_company_text}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        my_company_text: str = ''

    return my_company_text


def get_my_company_site_links(div):
    """Найти и вернуть ссылку на сайт компании."""

    try:
        get_my_company_site_link: str = div.find('cite', attrs={'class': 'iUh30 bc tjvcx'})
        l_message(gfn(), f'company_site_links  {get_my_company_site_link}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        get_my_company_site_link: str = 'N\A'

    return get_my_company_site_link


def get_my_company_link_1(div):
    """Найти и вернуть быструю ссылку на сайт компании."""

    try:
        my_company_link_1: str = div.find('span', attrs={'class': 'gBIQub KETUZd qzEoUe'}).text
        x: int = my_company_link_1.index('/')
        my_company_link_1 = my_company_link_1[0:x]
        l_message(gfn(), f'company_link_1 {my_company_link_1}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        my_company_link_1: str = ''

    return my_company_link_1
