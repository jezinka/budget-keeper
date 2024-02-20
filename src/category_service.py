from category_repository import get_category_by_name


def match_category(message):
    title = message.get_title().lower()
    who = message.get_who().lower()

    category_name = ''

    if 'końcówek' in title:
        category_name = 'końcówki'
    if 'ikze' in title:
        category_name = 'emerytura'
    if 'legimi' in title or 'doładowanie telefonu' in title or 'spotify' in title or 'disney' in title:
        category_name = 'abonament'
    if 'urbancard' in title:
        category_name = 'bilety'
    if 'finax' in who or '27534' in title:
        category_name = 'inwestycje'
    if 'steam' in title:
        category_name = 'gry'
    if 'apteka' in title:
        category_name = 'zdrowie'
    if 'zabka' in title and message.amount > -30:
        category_name = 'osiedlowy'
    if 'lidl' in title or 'biedronka' in title or 'miedzy twoimi kontami' in title:
        category_name = 'na życie'
    if 'fryzjer' in title:
        category_name = 'fryzjer'
    if 'szkolna kasa' in who:
        category_name = 'szkoła'
    if ('stowarzyszenie' in title or 'siepomaga' in title or 'darowizna' in title
            or 'pomoc' in title or 'fundacja' in title):
        category_name = 'darowizny'
    if 'polisa' in title:
        category_name = 'ubezpieczenie'
    if 'patronite' in title:
        category_name = 'patronite'

    return get_category_by_name(category_name)
