import src.simulation as sim
import src.decision_tree as dTree
import src.monitor as mon

from sklearn.utils import shuffle
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
from typing import List

import scenic
import pickle

NUM_SIMULATIONS = 100
NUM_OF_ITERATIONS = 10
SEED = 42
SCENARIO_LEFTSIDE = 'src/scenarios/parkedLeft.scenic'
SCENARIO_RIGHTSIDE = 'src/scenarios/parkedRight.scenic'
SIMPLE_SCENE = 'src/scenarios/simple_scene.scenic'

def training_loop(traces: List, labels: List, scenarios, monitor: mon.Monitor, max_iterations = 30):
    
    # Initialize variables
    violation_rate = 0
    alarm_rate = 0
    iteration = 0

    violation_rates = []
    alarm_rates = []
    late_alarm_rates = []

    # Execute training loop until some minimum accuracy, or a maximum number of iterations is reached
    while iteration < max_iterations:
        intersections = []
        num_alarms = []
        late_alarms = []

        # Loop over every scenario
        for scenario in scenarios:
            monitor.reset_window()

            # Run scenarios but with a monitor this time
            scenario_traces, scenario_labels, scen_intersections, scen_alarms = sim.training_data_from_scenario(scenario_file=scenario, num_simulations=NUM_SIMULATIONS, monitor=monitor, render=False)

            num_alarms += scen_alarms
            filtered_traces = [trace for trace, intersect in zip(scenario_traces, scen_intersections) if intersect]
            filtered_labels = [label for label, intersect in zip(scenario_labels, scen_intersections) if intersect]

            traces = traces + filtered_traces
            labels = labels + filtered_labels
            intersections = intersections + scen_intersections

            late_alarms += [alarm and intersect for alarm, intersect in zip(scen_alarms, scen_intersections)]

        traces, labels = shuffle(traces, labels, random_state=42)

        violations = intersections.count(True)
        alarms = num_alarms.count(True)
        late_alarm_amount = late_alarms.count(True)
        violation_rate = violations / (NUM_SIMULATIONS*len(scenarios))
        alarm_rate = alarms / (NUM_SIMULATIONS*len(scenarios))
        late_alarm_rate = late_alarm_amount / (NUM_SIMULATIONS*len(scenarios))

        violation_rates.append(violation_rate*100)
        alarm_rates.append(alarm_rate*100)
        late_alarm_rates.append(late_alarm_rate*100)
        late_alarms.append(late_alarm_amount)


        print(f'{iteration}:\t{violations} ({violation_rate:.2%}) system violations\t{alarms} ({alarm_rate:.2%}) alarms raised\t{late_alarm_amount} ({late_alarm_rate:.2%}) late alarms')

        dtree = dTree.train_classifier(traces=traces, labels=labels, windows_size=5, prediction_horizon=6)
    

        monitor.reset(dtree)      

        with open("tree.pkl", 'wb') as f:
            pickle.dump(dtree, f, protocol=5)
            f.close()
        
        iteration += 1

    return violation_rates, alarm_rates, late_alarm_rates, monitor
        

def main():

    # Run NUM_SIMULATIONS simulations of both scenarios
    traces_left, labels_left, intersections_left, _ = sim.training_data_from_scenario(scenario_file=SCENARIO_LEFTSIDE, num_simulations=NUM_SIMULATIONS, seed=SEED, render=False)
    traces_right, labels_right, intersections_right, _ = sim.training_data_from_scenario(scenario_file=SCENARIO_RIGHTSIDE, num_simulations=NUM_SIMULATIONS, seed=SEED, render=False)
    traces = traces_left + traces_right
    labels = labels_left + labels_right
    intersections = intersections_left + intersections_right

    accuracy = intersections.count(True) / (NUM_SIMULATIONS*2)

    print(f'{accuracy:.2%} had a collision without a monitor')

    traces, labels = shuffle(traces, labels, random_state=69)

    # learn a decision tree
    clf = dTree.train_classifier(traces=traces, labels=labels, windows_size=5, prediction_horizon=10)
    
    # create a list of feature names to make the tree more human readable
    feature_names = []
    for i in range(5):  # Assuming window size of 5
        feature_names.extend([f'dist_fl_{i}', f'dist_fr_{i}', f'closing_rate_fl_{i}', f'closing_rate_fr_{i}', f'steering_angle_{i}'])#, f'same_lane_{i}'])
        # feature_names.extend([f'same_lane_{i}'])

    # plot_tree(clf, feature_names=feature_names)
    # plt.show()

    with open("tree.pkl", 'wb') as f:
        pickle.dump(clf, f, protocol=5)
        f.close()
    
    monitor = mon.Monitor(dtree=clf)

    scenario_monitor_left_file = 'src/scenarios/testerLeft.scenic'
    scenario_monitor_right_file = 'src/scenarios/testerRight.scenic'
    scenario_monitor_simple = 'src/scenarios/test_simple_scene.scenic'

    violation_rates, alarm_rates, late_alarm_rates, monitor = training_loop(traces=traces, 
                                                labels=labels,
                                                scenarios=[scenario_monitor_left_file, scenario_monitor_right_file],#scenario_monitor_left_file, scenario_monitor_right_file],
                                                monitor=monitor)
    
    plt.plot(violation_rates, label='Violation rate')
    plt.plot(alarm_rates, label='Alarm rate')
    plt.plot(late_alarm_rates, label='Late alarm rate')
    plt.xlabel('Iteration')
    plt.ylabel('Percentage')
    plt.legend()
    plt.show()

    # traces, labels, intersections, alarms = sim.training_data_from_scenario(scenario_file=scenario_monitor_simple, num_simulations=NUM_SIMULATIONS, monitor=None, seed=SEED, render=False)

if __name__ == '__main__':
    main()

    # scenario versimpelen: werkt het nu? 
    # Veranderd de tree nog?
    # gaat de seed goed?
