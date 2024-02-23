from model import CategoryCondition, Category


class CategoryConditionRepository:

    def get_all(self):
        return (CategoryCondition
                .select()
                .join(Category))
