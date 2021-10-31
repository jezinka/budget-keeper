import logging
import shutil

from ludwig.api import LudwigModel

from budget_logging import logging_config


def predict():
    ludwig_model = LudwigModel.load('ludwig/model')
    predictions, _ = ludwig_model.predict(dataset='data/input.csv')

    return predictions.values[0][0]


def learn():
    config = {
        "input_features": [
            {"name": "CO", "type": "text"},
            {"name": "KTO", "type": "text"},
            {"name": "MAILE", "type": "text"},
            {"name": "ILE", "type": "numerical"}
        ],
        "output_features": [
            {"name": "KATEGORIA", "type": "category"}
        ]
    }
    ludwig_model = LudwigModel(config)
    train_stats, _, _ = ludwig_model.train(dataset='data/history.csv')
    ludwig_model.save('ludwig/model')
    shutil.rmtree('results/')


if __name__ == "__main__":
    logging_config()
    logging.debug(f'Learning model - start')
    learn()
    logging.debug(f'Learning model - stop')
