import scenic
from sklearn.tree import DecisionTreeClassifier
from typing import List


class Predictor():
    def __init__(self, dtree: DecisionTreeClassifier):
        self.dtree = dtree
        self.window = [0]*25

    def add_new_step(self, step: List):
        self.window = self.window[5:]
        self.window.extend(step)

    def predict(self):
        return self.dtree.predict(self.window)
