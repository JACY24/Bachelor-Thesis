import scenic

from scenic.simulators.newtonian import NewtonianSimulator
from scenic.domains.driving.roads import Network
import shapely as shapely
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import decision_tree as dTree
from sklearn.tree import plot_tree


NUM_SIMULATIONS = 10000
CAR_WIDTH = 2
CAR_LENGTH = 4.5
SCENARIO = scenic.scenarioFromFile('simulation/test.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)

def exec_simulation(network: Network = Network.fromFile('Scenic/assets/maps/CARLA/Town05.xodr')) -> dict | None:
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
    poly_a = shapely.Polygon(a[0:3])
    point_b = shapely.Point(b)

    return round(shapely.distance(poly_a, point_b), 4)

def format_trace(result: dict) -> pd.DataFrame:
    dist_fr = [calc_distance(result["parkedCorners"][i][1], result["drivingCorners"][i][1][0]) for i in range(len(result["drivingCorners"]))]
    dist_fl = [calc_distance(result["parkedCorners"][i][1], result["drivingCorners"][i][1][1]) for i in range(len(result["drivingCorners"]))]
    speed = [x[1] for x in result["speed"]]
    
    return pd.DataFrame({
        'dist_fl': dist_fl,
        'dist_fr': dist_fr,
        'speed': speed
    })

def intersecting(intersecting_list):
    for (_, x) in intersecting_list:
            if x:
                return True
            
    return False

def main():
    traces = []

    for _ in range(NUM_SIMULATIONS):
        simulation_result = exec_simulation()
        if simulation_result is not None:
            trace = format_trace(simulation_result)
            traces.append(trace)

    clf = dTree.train_classifier(traces, 5, 3)

    plt.figure(figsize=(12, 8))  # Optional: Adjust the size of the plot
    plot_tree(clf, filled=True)  # Use 'filled=True' for color in nodes
    plt.show()  # This ensures the plot is displayed

        # print(trace)
        # f_m = monitor.monitor(trace)
        # sim_intersects = intersecting(simulation_result['intersecting'])



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
# Achtergrond informatie automata learning/monitor learning (hoe werkt dit/wat voor vormen zijn er?)
# Trace printen: dit om te kunnen exporteren (misschien al met label?)
# basic simulation

# CARLA?