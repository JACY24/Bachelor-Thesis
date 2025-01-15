import src.simulation as sim
import src.decision_tree as dTree
import src.monitor as mon

from sklearn.utils import shuffle
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
from typing import List

import scenic
import pickle

NUM_SIMULATIONS = 10
NUM_OF_ITERATIONS = 5
SEED = 11
SCENARIO_LEFTSIDE = scenic.scenarioFromFile('src/scenarios/parkedLeft.scenic',
                                    params = {'seed': SEED},
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)
SCENARIO_RIGHTSIDE = scenic.scenarioFromFile('src/scenarios/parkedRight.scenic',
                                    params = {'seed': SEED},                                             
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)

def find_monitor_errors(alarms, intersections):
    num_of_errors = 0
    for i in range(len(alarms)):
        if alarms[i] and intersections[i]:
            num_of_errors += 1

    return num_of_errors

def training_loop(traces: List, labels: List, scenarios, monitor: mon.Monitor, min_accuracy: float = 0.95, delta:float = 0.0005, max_iterations = 10):
    
    accuracy = 0
    count = 0

    while accuracy <= min_accuracy or count < max_iterations:
        intersections = []
        num_of_errs = 0

        num_of_alarms = 0

        for scenario in scenarios:
            monitor.reset_window()
            # Run scenarios but with a monitor this time
            scenario_traces, scenario_labels, scenario_intersections, alarms = sim.training_data_from_scenario(scenario, NUM_SIMULATIONS, render=False)

            filtered_traces = [trace for trace, intersect in zip(scenario_traces, scenario_intersections) if intersect]
            filtered_labels = [label for label, intersect in zip(scenario_labels, scenario_intersections) if intersect]

            traces = traces + filtered_traces
            labels = labels + filtered_labels
            intersections = intersections + scenario_intersections
            num_of_errs += find_monitor_errors(alarms, scenario_intersections)
            num_of_alarms += alarms.count(True)

        traces, labels = shuffle(traces, labels, random_state=69)

        accuracy = intersections.count(False) / (NUM_SIMULATIONS * 2)

        print(f'{count}: {1-accuracy:.2%} collisions, {num_of_errs} alarms raised that still collided, {num_of_alarms} alarms raised')

        dtree = dTree.train_classifier(traces=traces, labels=labels, windows_size=5, prediction_horizon=6)
        monitor.reset(dtree)

        # plot the learned decision tree
        # plt.figure(figsize=(12, 8))
        # plot_tree(dtree, filled=True)
        # plt.show()

        with open("tree.pkl", 'wb') as f:
            pickle.dump(dtree, f, protocol=5)
            f.close()
        
        count += 1

    # return dtree
        

def main():

    # Run NUM_SIMULATIONS simulations of both scenarios
    traces_left, labels_left, intersections_left, alarms_left = sim.training_data_from_scenario(SCENARIO_LEFTSIDE, NUM_SIMULATIONS, False)
    traces_right, labels_right, intersections_right, alarms_right = sim.training_data_from_scenario(SCENARIO_RIGHTSIDE, NUM_SIMULATIONS, False)
    traces = traces_left + traces_right
    labels = labels_left + labels_right
    intersections = intersections_left + intersections_right

    accuracy = intersections.count(False) / (NUM_SIMULATIONS*2)

    print(f'{1-accuracy:.2%} had a collision without a monitor')

    traces, labels = shuffle(traces, labels, random_state=69)

    # learn a decision tree
    clf = dTree.train_classifier(traces=traces, labels=labels, windows_size=5, prediction_horizon=8)
    
    # create a list of feature names to make the tree more human readable
    feature_names = []
    for i in range(5):  # Assuming window size of 5
        feature_names.extend([f'dist_fl_{i}', f'dist_fr_{i}', f'closing_rate_fl_{i}', f'closing_rate_fr_{i}', f'steering_angle_{i}'])

    # plot the learned decision tree
    # plt.figure(figsize=(12, 8))
    # plot_tree(clf, feature_names=feature_names, filled=True)
    # plt.show()

    with open("tree.pkl", 'wb') as f:
        pickle.dump(clf, f, protocol=5)
        f.close()
    
    monitor = mon.Monitor(dtree=clf)

    SCENARIO_MONITOR_LEFTSIDE = scenic.scenarioFromFile('src/scenarios/testerLeft.scenic',
                                        params={'seed': SEED, 'monitor': monitor},
                                        model='scenic.simulators.newtonian.driving_model',
                                        mode2D=True)
    SCENARIO_MONITOR_RIGHTSIDE = scenic.scenarioFromFile('src/scenarios/testerRight.scenic',
                                        params={'seed': SEED, 'monitor': monitor},
                                        model='scenic.simulators.newtonian.driving_model',
                                        mode2D=True)

    training_loop(traces=traces, 
                  labels=labels,
                  scenarios=[SCENARIO_MONITOR_LEFTSIDE, SCENARIO_MONITOR_RIGHTSIDE],
                  monitor=monitor,
                  min_accuracy=0.98,
                  delta=0.0005)
    
  
if __name__ == '__main__':
    main()

# TODO:

# Vragen
# hoe goed is de monitor: remmen na 0.3s bij piepje: botsing of niet?
# meer situaties qua parkeren

# wegrijden als parkeren ipv. followlane

# CARLA?traces = []


# check of randomness hetzelfde blijft bij monitor breaking monitor.
# gaat ie niet opeens altijd remmen?
# bijhouden hoe vaak die remt
# scenic forum vraag stellen over alarm uit de simulatie halen
# gaat ie op een gegeven moment 'obviously unsafe' cases als grensgeval zien?