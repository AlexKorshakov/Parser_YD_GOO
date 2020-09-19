from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn
from Servises.Notify_by_Message import l_message


def get_my_company_title(DIV):
    """Найти и вернуть название компании"""

    try:
        my_company_title: str = DIV.find('h2', attrs={
            'class': "organic__title-wrapper typo typo_text_l typo_line_m"}).text.strip()
        l_message(gfn(), f'company_title {my_company_title}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        my_company_title: str = 'N\A'

    return my_company_title


def get_my_company_cid(DIV):
    """Найти и вернуть порядковый номер компании на странице."""

    try:
        my_company_cid: str = str(DIV.get('data-cid'))
        l_message(gfn(), f'company_cid {my_company_cid}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        my_company_cid: str = ''

    return my_company_cid


def get_my_company_contact(DIV):
    """Найти и вернуть контакты компании."""

    try:
        my_company_contact: str = DIV.find('div', attrs={
            'class': 'serp-meta__item'}).text.strip()

        text: int = my_company_contact.rfind('+')
        if text > 0:
            my_company_contact = my_company_contact[text:]

        l_message(gfn(), f'company_contact {my_company_contact}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        my_company_contact: str = 'N\A'

    return my_company_contact


def get_my_company_text(DIV):
    """Найти и вернуть описание компании."""

    try:
        my_company_text: str = DIV.find('div', attrs={
            'class': 'text-container typo typo_text_m typo_line_m organic__text'}).text.strip()
        l_message(gfn(), f'company_text  {my_company_text}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        my_company_text: str = ''

    return my_company_text


def get_my_company_sitelinks(DIV):
    """Найти и вернуть ссылку на сайт компании."""

    try:
        my_company_sitelinks: str = DIV.find('div', attrs={
            'class': 'sitelinks sitelinks_size_m organic__sitelinks'}).text.strip()
        l_message(gfn(), f'company_site_links  {my_company_sitelinks}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        my_company_sitelinks: str = 'N\A'

    return my_company_sitelinks


def get_my_company_link_1(DIV):
    """Найти и вернуть быструю ссылку на сайт компании."""

    try:
        my_company_link_1: str = DIV.find('a', attrs={
            'class': 'link link_theme_outer path__item i-bem'}).text.strip()
        text: int = my_company_link_1.rfind('›')
        if text > 0:
            my_company_link_1 = my_company_link_1[0:text]
        l_message(gfn(), f'company_link_1 {my_company_link_1}', color=Nm.BColors.OKBLUE)

    except AttributeError as err:
        l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.BColors.FAIL)
        my_company_link_1: str = ''

    return my_company_link_1
