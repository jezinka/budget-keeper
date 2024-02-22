from model import CategoryCondition


class CategoryConditionRepository:

    def get_all(self):
        return CategoryCondition.select().select_related()
