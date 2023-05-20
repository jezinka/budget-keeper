import json

class FixedCostService:
    db_utils = None

    def __init__(self, db_utils):
        self.db_utils = db_utils

    def check(self, message):
        fixed_costs = self.db_utils.find_all_fixed_costs()
        fixed_cost = None
        for cost in fixed_costs:

            if cost[3] is None:
                continue

            condition = json.loads(cost[3])
            if message.get_title() == condition['title'] and ("payee" not in condition.keys() or message.get_who() == condition['payee']):
                fixed_cost = cost
                break
        return fixed_cost


    def mark_as_payed(self, fixed_cost, message):
        self.db_utils.insert_fixed_cost_payed(message.get_date(), message.get_amount(to_string=False), fixed_cost[0])