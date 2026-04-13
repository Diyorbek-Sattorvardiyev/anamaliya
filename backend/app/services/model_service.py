from app.ml.training import ModelTrainer


class ModelService:
    def __init__(self):
        self.trainer = ModelTrainer()

    def train(self, samples: int, epochs: int) -> dict:
        return self.trainer.train(samples=samples, epochs=epochs)
