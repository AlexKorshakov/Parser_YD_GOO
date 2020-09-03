import random


class Fanny_Bot:
    @staticmethod
    def get_advice():
        ADVICES_VERBS = ['выключите',
                         'включите',
                         'перезагрузите',
                         'проверьте',
                         'переустановите',
                         'запустите',
                         'закройте',
                         'ебаните',
                         'сожгите',
                         'расщепите'
                         ]
        ADVICES_NOUNS = [['компьютер'],
                         ['роутер'],
                         ['программу'],
                         ['средство', 'восстановления', 'Windows'],
                         ['браузер'],
                         ['сайт'],
                         ['панель', 'управления'],
                         ['антивирус'],
                         ['мозг'],
                         ['голову'],
                         ['соседа'],
                         ]
        ADVICES_PREPS = [['а', 'затем'],
                         ['после', 'чего'],
                         ['и'],
                         ['а', 'если', 'это', 'не', 'сработает,', 'то'],
                         ]
        verbs = random.sample(ADVICES_VERBS, 2)
        nouns = random.sample(ADVICES_NOUNS, 2)
        prep = random.choice(ADVICES_PREPS)
        return '{} {}{}{} {} {}.'.format(verbs[0].capitalize(),
                                         ' '.join(nouns[0]),
                                         (', ' if prep[0] != 'и' else ' '),
                                         ' '.join(prep),
                                         verbs[1],
                                         ' '.join(nouns[1])
                                         )


# print(*[get_advice() for _ in range(20)], sep='\n')
def bububu():
    print(random.choice(['Кря! КРЯ!!', 'Зря! ЗРЯ!!', Fanny_Bot.get_advice()]))
