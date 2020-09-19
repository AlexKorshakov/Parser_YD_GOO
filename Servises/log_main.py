from datetime import datetime

NOW = str(datetime.now().strftime("%d.%m.%Y %H.%M.%S")) + " :: "


def log_vis_rec(*, param_name: str = None, p_value=None, d_path=None, r_log: bool = None, r_print: bool = None):
    """Функция логирования в файл и отображения данны в консоли"""

    if r_log:
        write_to_console(param_name=param_name, p_value=p_value)

    if r_print:
        write_to_text_log(param_name=param_name, p_value=p_value, d_path=d_path)


def write_to_console(*, param_name: str = None, p_value=None):
    """ Запись в консоль"""

    try:
        if param_name == 'NLine':
            print('=' * 100)

        try:
            if len(p_value) < 100:
                print(NOW + f'Параметр {param_name} Значение: {p_value}')
            else:
                print(NOW + f'Параметр {param_name} Значение: {p_value[:100] + "..."}')

        except Exception as err:
            print('Не итерируемый параметр', str(err.args), True)
            print(NOW + f'Параметр {param_name} Значение: {p_value}')

    except ConnectionError as err:
        log_vis_rec(param_name='log_vis_rec: Ошибка вывода в консоль', p_value=str(err.args), r_log=True)


def write_to_text_log(*, param_name: str = None, p_value=None, d_path=None):
    """ Запись в логфайл"""

    try:
        with open(d_path + r'_Log.txt', 'a', encoding='utf-8') as file:
            text = NOW + f'Параметр *** {param_name} *** Значение : {p_value}'
            file.write(text + '\n')

    except ConnectionError as err:
        log_vis_rec(param_name='log_vis_rec: Ошибка записи в файл', p_value=str(err.args), r_log=True)
