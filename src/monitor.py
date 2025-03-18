from typing import List
import pickle
import pandas as pd

class Alarm():
    def __init__(self):
        self.alarm_raised = False

    def raise_alarm(self):
        self.alarm_raised = True

class Monitor():
    def __init__(self, num_of_features: int, dtree=None):
        if dtree == None:
            with open('tree.pkl', 'rb') as f:
                self.dtree = pickle.load(f)
                f.close()
        else:
            self.dtree = dtree
        
        self.num_of_features = num_of_features
        self.window = [0]*(self.num_of_features*5)
        self.first = True

    def reset_window(self):
        self.window = [0]*(self.num_of_features*5)
        self.first = True

    def reset(self, dtree):
        self.dtree = dtree
        self.window = [0]*(self.num_of_features*5)
        self.first = True

    def add_new_step(self, step: List):
        if self.first:
            self.window = step*5
            self.first = False
        else:
            self.window = self.window[self.num_of_features:]
            self.window.extend(step)

    def predict(self):
        return bool(self.dtree.predict([self.window])[0])
    

    def check_for_alarm(self, dist_fl: float, dist_fr: float, steer: float, same_lane: int = None) -> bool:
        if same_lane is not None:
            current_state = [dist_fl, dist_fr, self.window[26] - dist_fl, self.window[27] - dist_fr, steer, same_lane]
        else:
            current_state = [dist_fl, dist_fr, self.window[22] - dist_fl, self.window[23] - dist_fr, steer]

        self.add_new_step(current_state)

        return self.predict()