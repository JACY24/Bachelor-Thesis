import scenic

from scenic.simulators.newtonian import NewtonianSimulator
from scenic.domains.driving.roads import Network
import shapely as shapely
import pandas as pd
from typing import List

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
    """Returns True if a collision happens during a simulation run and false otherwise"""
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
    steer = [x[1] for x in result['steer']]
    
    return pd.DataFrame({
        'dist_fl': dist_fl,
        'dist_fr': dist_fr,
        'closing_rate_fl': closing_rate_fl,
        'closing_rate_fr': closing_rate_fr,
        'steering_angle': steer,
    })

def generate_labels(interection_result):
    """Returns a list of labels for the generation timesteps""" 
    return [1 if i else 0 for _, i in interection_result]
