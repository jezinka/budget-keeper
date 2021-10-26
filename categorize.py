from ludwig.api import LudwigModel


def predict():
    ludwig_model = LudwigModel.load('ludwig/results/experiment_run_0/model')
    predictions, _ = ludwig_model.predict(dataset='data/input.csv')

    return predictions.values[0][0]
