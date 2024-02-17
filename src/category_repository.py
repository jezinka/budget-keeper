from model import Category


def get_category_by_name(name):
    if name == '':
        return None
    return Category.get(Category.name == name)
