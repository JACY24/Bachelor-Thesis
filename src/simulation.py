import scenic
import multiprocessing

from scenic.simulators.newtonian import NewtonianSimulator
from scenic.domains.driving.roads import Network
import shapely as shapely
import pandas as pd
from typing import List
from tqdm import tqdm
import random

def exec_simulation(scenario, network: Network = Network.fromFile('Scenic/assets/maps/CARLA/Town05.xodr'), render: bool = False) -> dict | None:
    """Executes one run of a simulation"""
    simulator = NewtonianSimulator(network, render=render)

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

def event_during_simulation(record: List) -> bool:
    """gets a record of boolean values and returns true if there is at least one value 'true' during the simulation run"""
    for _, x in record:
        if x:
            return True
    return False

def format_trace(result: dict) -> pd.DataFrame:
    """Returns a Pandas DataFrame representing a trace of the system"""
    dist_fl = [distance_car_to_point(result["parkedCorners"][i][1], result["drivingCorners"][i][1][1]) for i in range(len(result["drivingCorners"]))]
    dist_fr = [distance_car_to_point(result["parkedCorners"][i][1], result["drivingCorners"][i][1][0]) for i in range(len(result["drivingCorners"]))]
    closing_rate_fr = calc_closing_rate(dist_fr)
    closing_rate_fl = calc_closing_rate(dist_fl)
    steer = [x[1] for x in result['steer']]
    
    return pd.DataFrame({
        'dist_fl': dist_fl,
        'dist_fr': dist_fr,
        'closing_rate_fl': closing_rate_fl,
        'closing_rate_fr': closing_rate_fr,
        'steering_angle': steer,
        # 'same_lane': [x[1] for x in result['same_lane']]
    })

def generate_labels(interection_result):
    """Returns a list of labels for the generation timesteps""" 
    return [1 if i else 0 for _, i in interection_result]

def training_data_from_scenario(scenario_file, num_simulations: int = 1, seed: int = None, monitor = None, render: bool = False):
    """Generates traces, labels and a list of truth values indicating if intersections occur during simulation runs"""
    if seed:
        random.seed(seed)

    traces = []
    labels = []
    intersections = []
    alarms = []

    # Run NUM_SIMULATIONS simulations of the provided scenario
    scenario = scenic.scenarioFromFile(scenario_file,
                                params = {'seed': random.randint(0, 2**32) if seed else None, 'monitor': monitor},
                                model='scenic.simulators.newtonian.driving_model',
                                mode2D=True)
    
    for i in tqdm(range(num_simulations), desc='Running simulations', unit='sim'):
        
        simulation_result = exec_simulation(scenario, render = render)

        if simulation_result is not None:
            # When a simulation is succesful, we format the trace and add it to our list of traces
            formatted_trace = format_trace(simulation_result)
            generated_labels = generate_labels(simulation_result['intersecting'])
            # if formatted_trace['same_lane'][0] != event_during_simulation(simulation_result['intersecting']):
            #     print(f"{i}: NOT THE SAME!!!!")
            traces.append(formatted_trace)
            labels.append(generated_labels)
    
            intersections.append(event_during_simulation(simulation_result['intersecting']))
            if 'alarm' in simulation_result.keys():
                alarms.append(event_during_simulation(simulation_result['alarm']))

    return traces, labels, intersections, alarms
