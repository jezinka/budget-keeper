import json

from src.entity.model import Fixed_Cost, Fixed_Cost_Payed


class FixedCostService:

    def check(self, message):
        fixed_costs = Fixed_Cost.select()
        fixed_cost = None
        for cost in fixed_costs:

            if cost.conditions is None:
                continue

            condition = json.loads(cost.conditions)
            if message.get_title() == condition['title'] and (
                    "payee" not in condition.keys() or message.get_who() == condition['payee']):
                fixed_cost = cost
                break
        return fixed_cost

    def mark_as_payed(self, fixed_cost, message):
        Fixed_Cost_Payed.create(pay_date=message.get_date(),
                                amount=message.get_amount(to_string=False),
                                fixed_cost=fixed_cost)
