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


NUM_SIMULATIONS = 1000
CAR_WIDTH = 2
CAR_LENGTH = 4.5
SCENARIO = scenic.scenarioFromFile('simulation/test.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)

def exec_simulation(network: Network = Network.fromFile('Scenic/assets/maps/CARLA/Town05.xodr')) -> dict | None:
    """Executes one run of a simulation"""
    simulator = NewtonianSimulator(network, render=False)

    # Execute NUM_SIMULATIONS simulations and evaluate them
    scene, _ = SCENARIO.generate()
    simulation = simulator.simulate(scene, maxIterations = 10)
    result = None

    if simulation:  # `simulate` can return None if simulation fails
        # The records will be seen as the result of the simulation
        result = simulation.result.records

    simulator.destroy()
    return result

def calc_distance(a: tuple[scenic.core.vectors.Vector], b: scenic.core.vectors.Vector) -> float:
    """Calculates the distance between a point and a shape"""
    poly_a = shapely.Polygon(a[0:4])
    point_b = shapely.Point(b)

    return round(shapely.distance(poly_a, point_b), 4)

def calc_closing_rate(distances: List) -> List:
    """Returns a list of closing rates"""
    closing_rates = [0]

    for i in range(1, len(distances)):
        closing_rate = distances[i-1] - distances[i]
        closing_rates.append(closing_rate)

    return closing_rates


def format_trace(result: dict) -> pd.DataFrame:
    """Returns a Pandas DataFrame representing a trace of the system"""
    dist_fr = [calc_distance(result["parkedCorners"][i][1], result["drivingCorners"][i][1][0]) for i in range(len(result["drivingCorners"]))]
    dist_fl = [calc_distance(result["parkedCorners"][i][1], result["drivingCorners"][i][1][1]) for i in range(len(result["drivingCorners"]))]
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

def main():
    traces = []
    labels = []

    # Run NUM_SIMULATIONS simulations
    for _ in tqdm(range(NUM_SIMULATIONS), desc='Running simulations'):
        simulation_result = exec_simulation()
        if simulation_result is not None:
            # When a simulation is succesful, we format the trace and add it to our list of traces
            traces.append(format_trace(simulation_result))
            labels.append(generate_labels(simulation_result['intersecting']))

    # learn a decisiont ree
    clf = dTree.train_classifier(traces, labels, 5, 3)

    # # # plot the learned decision tree
    plt.figure(figsize=(12, 8))
    plot_tree(clf, filled=True)
    plt.show()

        
if __name__ == '__main__':
    main()

# DONE:
# marges auto inbouwen

# TODO:
# meer relevante data: snelheid? gas/throttle?
    
# hoe goed is de monitor: remmen na 0.3s bij piepje: botsing of niet?
# zelf monitor schrijven: basic informatie over traces (python)
# delta d -> relatieve snelheid
# Scikit -> decision tree
# twee afstandspunten toevoegen

# Vragen
# Overfitting, hoe kan ik hier het beste mee omgaan?

# CARLA?