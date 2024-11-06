import scenic

from scenic.simulators.newtonian import NewtonianSimulator
from scenic.domains.driving.roads import Network
import shapely as shapely
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import decision_tree as dTree
from sklearn.tree import plot_tree
from tqdm import tqdm
from typing import List
from sklearn.utils import shuffle
import tester
import pickle

NUM_SIMULATIONS = 10
CAR_WIDTH = 2
CAR_LENGTH = 4.5
SCENARIO_RIGHTSIDE = scenic.scenarioFromFile('simulation/parkedRight.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)
SCENARIO_LEFTSIDE = scenic.scenarioFromFile('simulation/parkedLeft.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)

def exec_simulation(scenario, network: Network = Network.fromFile('Scenic/assets/maps/CARLA/Town05.xodr')) -> dict | None:
    """Executes one run of a simulation"""
    simulator = NewtonianSimulator(network, render=False)

    # Execute NUM_SIMULATIONS simulations and evaluate them
    scene, _ = scenario.generate()
    simulation = simulator.simulate(scene, maxIterations = 10)
    result = None

    if simulation:  # `simulate` can return None if simulation fails
        # The records will be seen as the result of the simulation
        result = simulation.result.records

    simulator.destroy()
    return result

def distance_car_to_point(a: tuple[scenic.core.vectors.Vector], b: scenic.core.vectors.Vector) -> float:
    """Calculates the distance between a point and a car"""
    poly_a = shapely.Polygon(a[0:4])
    point_b = shapely.Point(b)

    return round(shapely.distance(poly_a, point_b), 4)

def distance_car_to_car(a: tuple[scenic.core.vectors.Vector], b: tuple[scenic.core.vectors.Vector]):
    """Calculates the distance between a car and a car"""
    poly_a = shapely.Polygon(a[0:4])
    poly_b = shapely.Polygon(b[0:4])

    return round(shapely.distance(poly_a, poly_b), 5)

def calc_closing_rate(distances: List) -> List:
    """Returns a list of closing rates"""
    closing_rates = [0]

    for i in range(1, len(distances)): # timestep meenemen
        closing_rate = distances[i-1] - distances[i]
        closing_rates.append(closing_rate)

    return closing_rates

def intersection_during_simulation(intersections: List) -> bool:
    for _, x in intersections:
        if x:
            return True
    return False

def format_trace(result: dict) -> pd.DataFrame:
    """Returns a Pandas DataFrame representing a trace of the system"""
    dist_fl = [distance_car_to_point(result["parkedCorners"][i][1], result["drivingCorners"][i][1][1]) for i in range(len(result["drivingCorners"]))]
    dist_fr = [distance_car_to_point(result["parkedCorners"][i][1], result["drivingCorners"][i][1][0]) for i in range(len(result["drivingCorners"]))]
    closing_rate_fr = calc_closing_rate(dist_fr)
    closing_rate_fl = calc_closing_rate(dist_fl)
    # speed = [x[1] for x in result["speed"]]
    steer = [x[1] for x in result['steer']]
    
    return pd.DataFrame({
        'dist_fl': dist_fl,
        'dist_fr': dist_fr,
        'closing_rate_fl': closing_rate_fl,
        'closing_rate_fr': closing_rate_fr,
        # 'speed': speed,
        'steering_angle': steer,
    })

def generate_labels(interection_result):
    """Returns a list of labels for the generation timesteps""" 
    return [1 if i else 0 for t, i in interection_result]

# def testing(dtree: tester.Predictor):
#     testing_scenario = scenic.scenarioFromFile('simulation/tester.scenic',
#                                     params={'dtree': dtree},
#                                     model='scenic.simulators.newtonian.driving_model',
#                                     mode2D=True)

def main():
    traces = []
    labels = []

    # Run NUM_SIMULATIONS simulations of cars parked on the right side
    for _ in tqdm(range(NUM_SIMULATIONS), desc='Running right parked simulations', unit='sim'):
        simulation_result = exec_simulation(SCENARIO_RIGHTSIDE)
        if simulation_result is not None:
            # When a simulation is succesful, we format the trace and add it to our list of traces
            formatted_trace = format_trace(simulation_result)
            generated_labels = (generate_labels(simulation_result['intersecting']))
            traces.append(formatted_trace)
            labels.append(generated_labels)
    
    # Run NUM_SIMULATIONS simulations of cars parked on the left side
    for _ in tqdm(range(NUM_SIMULATIONS), desc='Running left  parked simulations', unit='sim'):
        simulation_result = exec_simulation(SCENARIO_LEFTSIDE)
        if simulation_result is not None:
            # When a simulation is succesful, we format the trace and add it to our list of traces
            formatted_trace = format_trace(simulation_result)
            generated_labels = (generate_labels(simulation_result['intersecting']))
            traces.append(formatted_trace)
            labels.append(generated_labels)

    traces, labels = shuffle(traces, labels, random_state=69)

    # learn a decision tree
    clf = dTree.train_classifier(traces, labels, 5, 5)
    
    with open("test.pkl", 'wb') as f:
        pickle.dump(clf, f, protocol=5)
        f.close()

    # feature_names = []
    # for i in range(5):  # Assuming window size of 5
    #     feature_names.extend([f'dist_fl_{i}', f'dist_fr_{i}', f'closing_rate_fl_{i}', f'closing_rate_fr_{i}', f'steering_angle_{i}'])

    # plot the learned decision tree
    # plt.figure(figsize=(12, 8))
    # plot_tree(clf, feature_names=feature_names, filled=True)
    # plt.show()
  
if __name__ == '__main__':
    main()

# TODO:

# Vragen
# Overfitting, hoe kan ik hier het beste mee omgaan?

# Balans in samples (dupliceren of geen botsing rejecten)
# hoe goed is de monitor: remmen na 0.3s bij piepje: botsing of niet?
# meer situaties qua parkeren

# wegrijden als parkeren ipv. followlane

# CARLA?