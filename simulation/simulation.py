import scenic

from scenic.simulators.newtonian import NewtonianSimulator
from scenic.domains.driving.roads import Network
import shapely as shapely

NUM_SIMULATIONS = 3
CAR_WIDTH = 2
CAR_LENGTH = 4.5
SCENARIO = scenic.scenarioFromFile('simulation/test.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)

def exec_simulation(network = Network.fromFile('Scenic/assets/maps/CARLA/Town05.xodr')):
    simulator = NewtonianSimulator(network, render=True)

    # Execute NUM_SIMULATIONS simulations and evaluate them
    scene, _ = SCENARIO.generate()
    simulation = simulator.simulate(scene, maxIterations = 10)

    if simulation:  # `simulate` can return None if simulation fails
        # The result of the simulation
        result = simulation.result

        collided = (False, -1)
        for timestep, collision in result.records['intersecting']:
            if collision:
                collided = (True, timestep)
                break

    simulator.destroy()

    return collided, simulation.result.records

def calc_distance(a, b):
    poly_a = shapely.Polygon(a[0:3])
    poly_b = shapely.Polygon(b[0:3])

    return shapely.distance(poly_a, poly_b)

def main():
    collisions, distances = [], []

    for i in range(NUM_SIMULATIONS):
        collided, simulation_result = exec_simulation()
        collisions.append(collided)

        dist = []
        for i in range(len(simulation_result["parkedCorners"])):
            dist.append(calc_distance(simulation_result["parkedCorners"][i][1], simulation_result["drivingCorners"][i][1]))
            
        distances.append(dist)

    for i in range(len(distances)):
        print(f"#{i}:\t{collisions[i]}:")
        for j in range(len(distances[i])):
            print(f"{j}:\t{distances[i][j]}")

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