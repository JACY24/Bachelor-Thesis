from typing import List
import pickle
import pandas as pd

class Alarm():
    def __init__(self):
        self.alarm_raised = False

    def raise_alarm(self):
        self.alarm_raised = True

class Monitor():
    def __init__(self, window=[0]*25, dtree=None):
        if dtree == None:
            with open('tree.pkl', 'rb') as f:
                self.dtree = pickle.load(f)
                f.close()
        else:
            self.dtree = dtree
        self.window = window

    def reset_window(self):
        self.window = [0]*25

    def reset(self, dtree):
        self.dtree = dtree
        self.window = [0]*25

    def add_new_step(self, step: List):
        self.window = self.window[5:]
        self.window.extend(step)

    def predict(self):
        return bool(self.dtree.predict([self.window])[0])
    
    def print_window(self):
        frame = pd.DataFrame({
            'dist_fl': [self.window[i] for i in range(0,25,5)],
            'dist_fr': [self.window[i+1] for i in range(0,25,5)],
            'closing_rate_fl': [self.window[i+2] for i in range(0,25,5)],
            'closing_rate_fr': [self.window[i+3] for i in range(0,25,5)],
            'steering_angle': [self.window[i+4] for i in range(0,25,5)],
            # 'same_lane': [self.window[i+5] for i in range(0,25,5)]
        })
        print(f'{frame}')

    def check_for_alarm(self, dist_fl: float, dist_fr: float, steer: float) -> bool:

        current_state = [dist_fl, dist_fr, self.window[22] - dist_fl, self.window[23] - dist_fr, steer]
        # current_state = [dist_fl, dist_fr, self.window[26] - dist_fl, self.window[27] - dist_fr, steer, same_lane]

        self.add_new_step(current_state)

        return self.predict()
    
    # nieuwe data relevanter maken? hier is de monitor al actief dus wellicht relevanter voor de classifier
    # is monitor afgegaan bijhouden. Dit is relevant voor welke traning data de classifier moet gebruiken. Als de monitor afgaat en er nog steeds een crash is is de monitor gewoon te laat, niet perse fout.
    # resolutie aanpassen?
    # hyper parameter tuning (wellicht binnen SKlearn opties?)
    # logaritmisch schalen van windows?