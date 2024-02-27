import scenic
from scenic.simulators.newtonian import NewtonianSimulator
from math import dist

NUM_SIMULATIONS = 10

scenario = scenic.scenarioFromFile('simulation/test.scenic',
                                   model='scenic.simulators.newtonian.driving_model',
                                   mode2D=True)
simulator = NewtonianSimulator()
distances = []

for i in range(NUM_SIMULATIONS):
    scene, _ = scenario.generate()
    simulation = simulator.simulate(scene, maxIterations = 10)

    if simulation:  # `simulate` can return None if simulation fails
        result = simulation.result
        min_distance = 999 # because of our scenic implementation, other distances will always be smaller

        for j, state in enumerate(result.trajectory):
            _, parkedCarPos, drivingCarPos = state
            distance = dist(parkedCarPos, drivingCarPos)
            if distance < min_distance:
                min_distance = distance

        distances.append((i, min_distance))

        print(simulation.result.terminationReason)

for distance in distances:
    print(f'Simulation {distance[0]}: minimum distance between cars: {distance[1]}')

# TODO:
# marges auto inbouwen
# meer relevante data: snelheid? gas/throttle?
    
# hoe goed is de monitor: remmen na 0.3s bij piepje: botsing of niet?
# zelf monitor schrijven
# data opslaan
    