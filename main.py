import src.simulation as sim
import src.decision_tree as dTree
import src.monitor as mon

from sklearn.utils import shuffle
from sklearn.tree import plot_tree, export_graphviz
import matplotlib.pyplot as plt
from typing import List
import graphviz

import scenic
import pickle

import csv
import os

import time

NUM_SIMULATIONS = 2000
NUM_OF_ITERATIONS = 10
SEED = 24
PREDICTION_HORIZON = 10

SCENE_LEFT = 'src/scenarios/parkedLeft.scenic'
SCENE_RIGHT = 'src/scenarios/parkedRight.scenic'
SCENE_SIMPLE = 'src/scenarios/simple.scenic'
SCENE_SIMPLEST = 'src/scenarios/simplest.scenic'

MON_LEFT = 'src/scenarios/monitor_left.scenic'
MON_RIGHT = 'src/scenarios/monitor_right.scenic'
MON_SIMPLE = 'src/scenarios/monitor_simple.scenic'
MON_SIMPLEST = 'src/scenarios/monitor_simplest.scenic'

def initialize_dirs():
    result_dir = os.path.join(os.getcwd(), 'results')
    fig_dir = os.path.join(result_dir, 'figs')
    tree_dir = os.path.join(result_dir, 'trees')
    csv_dir = os.path.join(result_dir, 'csvs')
    data_dir = os.path.join(result_dir, 'data')

    # Check if directory exists, create it if it doesn't
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)
    if not os.path.exists(tree_dir):
        os.makedirs(tree_dir)
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)


    return result_dir, fig_dir, tree_dir, csv_dir, data_dir

def get_feature_names(num_of_features: int):
    feature_names = []
    if num_of_features == 6:
        for i in range(5):  # Assuming window size of 5
            feature_names.extend([f'dist_fl_{i}', f'dist_fr_{i}', f'closing_rate_fl_{i}', f'closing_rate_fr_{i}', f'steering_angle_{i}', f'same_lane_{i}'])
    elif num_of_features == 5:
        for i in range(5):  # Assuming window size of 5
            feature_names.extend([f'dist_fl_{i}', f'dist_fr_{i}', f'closing_rate_fl_{i}', f'closing_rate_fr_{i}', f'steering_angle_{i}'])
    
    return feature_names


def training_loop(traces: List, labels: List, scenarios, monitor: mon.Monitor, max_iterations: int = 50, result_dir = None, name: str = None, num_of_features: int = None):
    
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
            scenario_traces, scenario_labels, scen_intersections, scen_alarms, scen_late_alarms = sim.training_data_from_scenario(scenario_file=scenario, num_simulations=NUM_SIMULATIONS, monitor=monitor, render=False, prediction_horizon=PREDICTION_HORIZON)
            num_alarms += scen_alarms
            late_alarms += scen_late_alarms
            filtered_traces = [trace for trace, intersect in zip(scenario_traces, scen_intersections) if intersect]
            filtered_labels = [label for label, intersect in zip(scenario_labels, scen_intersections) if intersect]
            
            traces = traces + filtered_traces
            labels = labels + filtered_labels
            intersections = intersections + scen_intersections


        traces, labels = shuffle(traces, labels, random_state=42)

        violations = intersections.count(True)
        alarms = num_alarms.count(True)
        late_alarm_amount = late_alarms.count(True)
        violation_rate = violations / (max(len(intersections), 1))
        alarm_rate = alarms / (max(len(num_alarms),1))
        late_alarm_rate = late_alarm_amount / (max(len(late_alarms),1))

        violation_rates.append(violation_rate*100)
        alarm_rates.append(alarm_rate*100)
        late_alarm_rates.append(late_alarm_rate*100)
        late_alarms.append(late_alarm_rate*100)

        print(f'{iteration}:\t{violations} ({violation_rate:.2%}) system violations\t{alarms} ({alarm_rate:.2%}) alarms raised\t{late_alarm_amount} ({late_alarm_rate:.2%}) late alarms')

        dtree = dTree.train_classifier(traces=traces, labels=labels, windows_size=5, prediction_horizon=PREDICTION_HORIZON)

        feature_names = get_feature_names(num_of_features)

        if ((iteration+1) % 10 == 0) or iteration == 24:
            fig = plt.figure(iteration)

            plot_tree(dtree, filled=True, feature_names=feature_names)

            if result_dir:
                fig_file = os.path.join(result_dir, 'figs', f'{name}_tree_{iteration}.png')
                tree_file = os.path.join(result_dir, 'trees', f'{name}_tree_{iteration}.pkl')
                trace_file = os.path.join(result_dir, 'data', f'{name}_traces_{iteration}.pkl')
                label_file = os.path.join(result_dir, 'data', f'{name}_labels_{iteration}.pkl')

                plt.savefig(fig_file, dpi=600)
                with open(tree_file, 'wb') as f:
                    pickle.dump(dtree, f, protocol=5)
                    f.close()

                with open(trace_file, 'wb') as f:
                    pickle.dump(traces, f)
                    f.close()
                
                with open(label_file, 'wb') as f:
                    pickle.dump(labels, f)
                    f.close()

            # plt.show()
            plt.close(fig)

        monitor.reset(dtree)
        
        iteration += 1

    return violation_rates, alarm_rates, late_alarm_rates, monitor

def run_scenes_from_list(scenarios, monitor=None, render=False):
    """
    Runs scenes from list

    Returns:
        traces: List
            List of resulting traces

        labels: List
            List of resulting labels

        intersections: List
            List of per simulation, if there is an intersection anywhere in that simulation

        alarms: List
            List representing if an alarm is raised at any point during the simulation

        late_alarms: List
            List representing if there is a late alarm per simulation
    """
    traces = []
    labels = []
    intersections = []
    alarms = []
    late_alarms = []

    for scene in scenarios:
        scene_traces, scene_labels, scene_intersections, scen_alarms , scen_late_alarms = sim.training_data_from_scenario(scenario_file=scene,
                                                                                            num_simulations=NUM_SIMULATIONS,
                                                                                            seed=SEED,
                                                                                            monitor=monitor,
                                                                                            render=render,
                                                                                            prediction_horizon=PREDICTION_HORIZON)
        traces += scene_traces
        labels += scene_labels
        intersections += scene_intersections
        alarms += scen_alarms
        late_alarms += scen_late_alarms

    return traces, labels, intersections, alarms, late_alarms

def run_one_experiment(scenarios, monitors, num_of_features, name, result_dir):
    scenarios = scenarios
    monitor_scenarios = monitors

    traces, labels, intersections, _, _ = run_scenes_from_list(scenarios, render=False)

    accuracy = intersections.count(True) / (len(intersections))
    print(f'{accuracy:.2%} had a collision without a monitor')

    traces, labels = shuffle(traces, labels, random_state=69)

    # learn a decision tree
    dtree = dTree.train_classifier(traces=traces, labels=labels, windows_size=5, prediction_horizon=PREDICTION_HORIZON)
    
    # create a list of feature names to make the tree more human readable
    feature_names = get_feature_names(num_of_features=num_of_features)

    fig_init = plt.figure('init')
    plot_tree(dtree, filled=True, feature_names=feature_names)
    fig_path = os.path.join(result_dir, 'figs', f'{name}_initial_tree.png')
    plt.savefig(fig_path, dpi=600)
    # plt.show()
    plt.close(fig_init)

    tree_path = os.path.join(result_dir, 'trees', f'{name}_initial_tree.pkl')
    with open(tree_path, 'wb') as f:
        pickle.dump(dtree, f, protocol=5)
        f.close()
    
    monitor = mon.Monitor(dtree=dtree, num_of_features=num_of_features)

    training_start = time.time()
    violation_rates, alarm_rates, late_alarm_rates, monitor = training_loop(traces=traces, 
                                                labels=labels,
                                                scenarios=monitor_scenarios,#scenario_monitor_left_file, scenario_monitor_right_file],
                                                monitor=monitor,
                                                result_dir=result_dir,
                                                name=name,
                                                num_of_features=num_of_features)
    training_end = time.time()

    with open(os.path.join(result_dir, f'csvs/{name}_results.csv'), 'w', newline='') as f:
        data = [{'violation_rate': violation_rates, 'alarm_rate': alarm_rates, 'late_alarm_rate': late_alarm_rates}]
        fieldnames = ['violation_rate', 'alarm_rate', 'late_alarm_rate']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        f.close()

    res_fig = plt.figure('results')
    plt.plot(violation_rates, label='Violation rate', ls='-')
    plt.plot(alarm_rates, label='Alarm rate', ls='-')
    plt.plot(late_alarm_rates, label='Late alarm rate', ls=':')
    plt.xlabel('Iteration')
    plt.ylabel('Percentage')
    plt.title('Monitor quality over time')
    plt.legend()
    results = os.path.join(result_dir, 'figs', f'{name}_results.png')
    plt.savefig(results, dpi=600)
    # plt.show()
    plt.close(res_fig)

    _, _, comparing_intersections, comparing_alarms, comparing_late_alarms = run_scenes_from_list(monitor_scenarios, monitor=monitor)
    
    comp_accuracy = comparing_intersections.count(True) / len(comparing_intersections)
    comparing_alarm_rate = comparing_alarms.count(True) / len(comparing_alarms)
    comparing_late_alarm_rate = comparing_late_alarms.count(True) / len(comparing_late_alarms)
    print(f'{comp_accuracy:.2%} had a collision with the final monitor, compared to {accuracy:.2%} without')

    return accuracy, comp_accuracy, comparing_alarm_rate, comparing_late_alarm_rate, training_end-training_start

def main():
    result_dir, _, _, _, _ = initialize_dirs()

    simplest_scenarios = [SCENE_SIMPLEST]
    simplest_monitors = [MON_SIMPLEST]

    simple_scenarios = [SCENE_SIMPLE]
    simple_monitor = [MON_SIMPLE]

    normal_scenarios = [SCENE_LEFT, SCENE_RIGHT]
    normal_monitors = [MON_LEFT, MON_RIGHT]


    simplest_start = time.time()
    simplest_init_acc, simplest_end_acc, simplest_end_alarm_rate, simplest_end_late_alarm_rate, simplest_training_time = run_one_experiment(scenarios=simplest_scenarios, 
                                                              monitors=simplest_monitors, 
                                                              num_of_features=6, 
                                                              name='simplest', 
                                                              result_dir=result_dir)
    simplest_end = time.time()

    simple_start = time.time()
    simple_init_acc, simple_end_acc, simple_end_alarm_rate, simple_end_late_alarm_rate, simple_training_time = run_one_experiment(scenarios=simple_scenarios, 
                                                         monitors=simple_monitor, 
                                                         num_of_features=5, 
                                                         name='simple', 
                                                         result_dir=result_dir)
    simple_end = time.time()

    normal_start = time.time()
    norm_init_acc, norm_end_acc, norm_end_alarm_rate, norm_end_late_alarm_rate, normal_training_time = run_one_experiment(scenarios=normal_scenarios, 
                                                     monitors= normal_monitors, 
                                                     num_of_features=5, 
                                                     name='normal', 
                                                     result_dir=result_dir)
    normal_end = time.time()

    data = [{'name': 'simplest', 'initial_accuracy': simplest_init_acc, 'end_accuracy': simplest_end_acc, 'end_alarm': simplest_end_alarm_rate, 'end_late_alarm': simplest_end_late_alarm_rate,'training_time': simplest_training_time, 'total_time': simplest_end-simplest_start},
            {'name': 'simple', 'initial_accuracy': simple_init_acc, 'end_accuracy': simple_end_acc, 'end_alarm': simple_end_alarm_rate, 'end_late_alarm': simple_end_late_alarm_rate, 'training_time': simple_training_time, 'total_time': simple_end-simple_start},
            {'name': 'normal', 'initial_accuracy': norm_init_acc, 'end_accuracy': norm_end_acc, 'end_alarm': norm_end_alarm_rate, 'end_late_alarm': norm_end_late_alarm_rate, 'training_time': normal_training_time, 'total_time': normal_end-normal_start}]

    with open(os.path.join(result_dir, 'csvs/results.csv'), 'w', newline='') as f:
        fieldnames = ['name', 'initial_accuracy', 'end_accuracy', 'end_alarm', 'end_late_alarm', 'training_time', 'total_time']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        f.close()

if __name__ == '__main__':
    main()
