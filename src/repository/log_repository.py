from src.entity.model import Log


def create_log(type, message):
    Log.create(type=type, message=message)
