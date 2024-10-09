import scenic

from scenic.simulators.newtonian import NewtonianSimulator
from scenic.domains.driving.roads import Network
import shapely as shapely
import pandas as pd
import monitor

NUM_SIMULATIONS = 3
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

def calc_distance(a: tuple[scenic.core.vectors.Vector], b: tuple[scenic.core.vectors.Vector]) -> float:
    poly_a = shapely.Polygon(a[0:3])
    poly_b = shapely.Polygon(b[0:3])

    return round(shapely.distance(poly_a, poly_b), 4)

def format_trace(result: dict) -> pd.DataFrame:
    dist = [calc_distance(result["parkedCorners"][i][1], result["drivingCorners"][i][1]) for i in range(len(result["parkedCorners"]))]
    speed = [x[1] for x in result["speed"]]
    
    return pd.DataFrame({
        'distance': dist,
        'speed': speed
    })

def main():
    # for _ in range(NUM_SIMULATIONS):
    #     simulation_result = exec_simulation()
    #     if simulation_result is not None:
    #         trace = format_trace(simulation_result)

    # print(trace)

    simulation_result = exec_simulation()
    if simulation_result is not None:
        trace = format_trace(simulation_result)

    print(trace)
    print(monitor.monitor(trace))


main()

# DONE:
# marges auto inbouwen

# TODO:
# meer relevante data: snelheid? gas/throttle?
    
# hoe goed is de monitor: remmen na 0.3s bij piepje: botsing of niet?
# zelf monitor schrijven: basic informatie over traces (python)
# Achtergrond informatie automata learning/monitor learning (hoe werkt dit/wat voor vormen zijn er?)
# Trace printen: dit om te kunnen exporteren (misschien al met label?)
# basic simulation

# CARLA?