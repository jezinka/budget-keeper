from model import Category


class CategoryRepository:

    def get_category_by_name(self, name):
        if name == '':
            return None
        return Category.get(Category.name == name)
