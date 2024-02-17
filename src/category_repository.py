from model import Category


def get_category_by_name(name):
    return Category.get(Category.name == name)
