from typing import List
import pickle

class Monitor():
    def __init__(self, window=[0]*25, dtree=None):
        if dtree == None:
            with open('test.pkl', 'rb') as f:
                self.dtree = pickle.load(f)
                f.close()
        else:
            self.dtree = dtree
        self.window = window

    def add_new_step(self, step: List):
        self.window = self.window[5:]
        self.window.extend(step)

    def predict(self):
        return bool(self.dtree.predict([self.window])[0])
    
    def check_for_alarm(self, dist_fl: float, dist_fr: float, steer: float) -> bool:

        current_state = [dist_fl, dist_fr, self.window[23] - dist_fl, self.window[24] - dist_fr, steer]

        self.add_new_step(current_state)

        return self.predict()