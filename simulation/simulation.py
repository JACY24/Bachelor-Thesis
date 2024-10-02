import scenic
import math
import matplotlib.pyplot as plt
import geopandas as gpd

from scenic.simulators.newtonian import NewtonianSimulator
from scenic.domains.driving.roads import Network
from shapely.geometry import Polygon


NUM_SIMULATIONS = 5
CAR_WIDTH = 2
CAR_LENGTH = 4.5
SCENARIO = scenic.scenarioFromFile('simulation/test.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)

def main():
    
    # Setup the simulation
    network = Network.fromFile('Scenic/assets/maps/CARLA/Town05.xodr')
    simulator = NewtonianSimulator(network, render=True)

    # initialise collisions list
    collisions = []

    # Execute NUM_SIMULATIONS simulations and evaluate them
    for i in range(NUM_SIMULATIONS):
        scene, _ = SCENARIO.generate()
        simulation = simulator.simulate(scene, maxIterations = 10)

        if simulation:  # `simulate` can return None if simulation fails
            # The result of the simulation
            result = simulation.result
 
            collisions.append((i, False, -1))
            for timestep, collision in result.records['intersecting']:
                if collision:
                    collisions[i] = (i, True, timestep)
                    break

    simulator.destroy()
    
    different = False
    # Print the result of the analyses
    for collision in collisions:
        print(f'{collision[0]}: {f"   collision at timestep {collision[2]}" if collision[1] else "no collision"}')
        if collision[2] != -1 and collision[2] != 14:
            different = True
    
    print(f'{"Something different happened!" if different else "Always at step 14"}')

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