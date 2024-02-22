import json

from category_condition_repository import CategoryConditionRepository


class CategoryService:

    def __init__(self):
        self.category_condition_repository = CategoryConditionRepository()

    def match_category(self, message):
        category_conditions = self.category_condition_repository.get_all()
        title = message.get_title().lower()
        who = message.get_who().lower()

        category = None
        for category_condition in category_conditions:

            if category_condition.conditions is None:
                continue

            condition = json.loads(category_condition.conditions)
            if ('title' in condition.keys() and condition['title'] in title) or (
                    'who' in condition.keys() and condition['who'] in who):
                category = category_condition.category
                break

        return category
