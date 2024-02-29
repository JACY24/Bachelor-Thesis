import scenic
from scenic.simulators.newtonian import NewtonianSimulator
from math import dist, degrees, cos, sin
from shapely.geometry import Polygon

NUM_SIMULATIONS = 5
CAR_WIDTH = 2
CAR_LENGTH = 4.5

def print_dict(dictionary):
    for key in dictionary.keys():
        print(key, end=": ")
        print(list(map(lambda x: (x[0], degrees(x[1])) , dictionary[key])))


def calculateRotatedPoint(point, centerCoords, theta):
    tempX = point[0] - centerCoords[0]
    tempY = point[1]- centerCoords[1]

    rotatedX = tempX*cos(theta) - tempY*sin(theta)
    rotatedY = tempX*sin(theta) + tempY*sin(theta)

    return (rotatedX+centerCoords[0], rotatedY+centerCoords[1])


def calculatePolygon(center, length, width, heading):
    topRightX = center[0] + 0.5*length + 0.5*width
    topLeftX = center[0] + 0.5*length - 0.5*width
    bottomRightX = center[0] - 0.5*length + 0.5*width
    bottomLeftX = center[0] - 0.5*length - 0.5*width

    topRightY = center[1] + 0.5*length + 0.5*width
    topLeftY = center[1] + 0.5*length - 0.5*width
    bottomRightY = center[1] - 0.5*length + 0.5*width
    bottomLeftY = center[1] - 0.5*length - 0.5*width

    topRightCoord = calculateRotatedPoint((topRightX, topRightY), center, heading)
    bottomRightCoord = calculateRotatedPoint((bottomRightX, bottomRightY), center, heading)
    topLeftCoord = calculateRotatedPoint((topLeftX, topLeftY), center, heading)
    bottomLeftCoord = calculateRotatedPoint((bottomLeftX, bottomLeftY), center, heading)

    return Polygon([bottomLeftCoord, topLeftCoord, topRightCoord, bottomRightCoord])


scenario = scenic.scenarioFromFile('simulation/test.scenic',
                                   model='scenic.simulators.newtonian.driving_model',
                                   mode2D=True)
scene, _ = scenario.generate()
simulator = NewtonianSimulator(render=True)
distances = []

for i in range(NUM_SIMULATIONS):
    scene, _ = scenario.generate()
    simulation = simulator.simulate(scene, maxIterations = 10)


    if simulation:  # `simulate` can return None if simulation fails
        result = simulation.result
        min_distance = 999 # because of our scenic implementation, other distances will always be smaller

        print_dict(result.records)

        # loop over the states per time step and save the minimal distance between the two cars
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
    