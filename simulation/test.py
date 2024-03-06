import scenic
import math
import matplotlib.pyplot as plt
import geopandas as gpd

from scenic.simulators.newtonian import NewtonianSimulator
from scenic.domains.driving.roads import Network
from shapely.geometry import Polygon


NUM_SIMULATIONS = 10
CAR_WIDTH = 2
CAR_LENGTH = 4.5
SCENARIO = scenic.scenarioFromFile('simulation/test.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)


def print_dict(dictionary: dict) -> None:
    ''' Prints a dictionary of records

    Parameters
    ----------
        dictionary : dict
            A dictionary where key is the name of the recorded item, 
            and value is a list of tuples, containing the timestep and the heading of a car in radians.

    Returns
    -------
        None
    '''
    for key in dictionary.keys():
        print(key, end=": ")
        print(list(map(lambda x: (x[0], math.degrees(x[1])) , dictionary[key])))


def calculateRotatedPoint(point: tuple[float, float], center: tuple[float, float], theta: float) -> tuple[float,float]:
    '''
    Calculates a coordinate, rotateted theta degrees around a centerpoint

    Parameters
    ----------
    point : (float, float)
        the coordinate of the point to rotate

    centerCoords : (float, float)
        the centerpoint to rotate arount

    theta : float
        the angle to rotate the point

    Returns
    -------
    rotatedPoint : (float, float)
        the coordinate of the rotated point    
    '''

    rotatedX = (point[0] - center[0])*math.cos(theta) - (point[1]-center[1])*math.sin(theta) + center[0]
    rotatedY = (point[0] - center[0])*math.sin(theta) + (point[1]-center[1])*math.cos(theta) + center[1]

    return (rotatedX, rotatedY)


def createRotatedRectangle(center: tuple[float,float], length: float, width: float, theta: float) -> Polygon:
    '''
    Create a polygon representing a rotated rectangle

    Parameters
    ----------
    center : (float, float)
        coordinate of the center of the rectangle
    
    length : float
        length of the rectangle

    width : float
        width of the rectangle

    theta : float
        the angle that the rectangle is rotated, in radians

    Returns
    -------
    rotatedRectangle : shapely.geometry.Polygon
        A polygon representing a rotated rectangle
    '''
    topRightX = center[0] + 0.5*width
    topLeftX = center[0] - 0.5*width
    bottomRightX = center[0] + 0.5*width
    bottomLeftX = center[0] - 0.5*width

    topRightY = center[1] + 0.5*length
    topLeftY = center[1] + 0.5*length
    bottomRightY = center[1] - 0.5*length
    bottomLeftY = center[1] - 0.5*length

    if theta < 0:
        theta = 2*math.pi - abs(theta)

    topRightCoord = calculateRotatedPoint((topRightX, topRightY), center, theta)
    bottomRightCoord = calculateRotatedPoint((bottomRightX, bottomRightY), center, theta)
    topLeftCoord = calculateRotatedPoint((topLeftX, topLeftY), center, theta)
    bottomLeftCoord = calculateRotatedPoint((bottomLeftX, bottomLeftY), center, theta)

    return Polygon([bottomLeftCoord, 
                    topLeftCoord, 
                    topRightCoord, 
                    bottomRightCoord,
                    ])


def main():
    
    # Setup the simulation
    network = Network.fromFile('../Scenic/assets/maps/CARLA/Town05.xodr')
    simulator = NewtonianSimulator(network, render=True)
    # simulator = NewtonianSimulator()

    # initialise collisions list
    collisions = []

    # Execute NUM_SIMULATIONS simulations and evaluate them
    for i in range(NUM_SIMULATIONS):
        scene, _ = SCENARIO.generate()
        simulation = simulator.simulate(scene, maxIterations = 10)


        if simulation:  # `simulate` can return None if simulation fails
            # The result of the simulation
            result = simulation.result

            # The parked car heading (1 value per simulation)
            parkedCarHeading = result.records['parkedCarHeading']
            # The driving car heading (a list of tuples per time step)
            drivingCarHeading = result.records['drivingCarHeading']
            # Print(result.records['distance'])

            # Go through each time step and check if the cars intersect at some point
            for j, state in enumerate(result.trajectory):
                # Positions of the cars
                _, parkedCarPos, drivingCarPos = state

                # Cars have not collided at the start of the simulation
                collided = False

                # Create polygons of the cars
                parkedCar = createRotatedRectangle(parkedCarPos, CAR_LENGTH, CAR_WIDTH, parkedCarHeading)
                drivingCar = createRotatedRectangle(drivingCarPos, CAR_LENGTH, CAR_WIDTH, drivingCarHeading[j][1])

                # Check if the cars intersect at the current timestep
                if parkedCar.intersects(drivingCar):
                    collided = True
                    ax = plt.axes()
                    p1 = gpd.GeoSeries([parkedCar])
                    p1.boundary.plot(ax=ax)
                    p2 = gpd.GeoSeries([drivingCar])
                    p2.boundary.plot(ax=ax)
                    plt.show()
                    break

            # Update the collisions list
            collisions.append((i, collided))

    # Print the result of the analyses
    for collision in collisions:
        print(f'Simulation {collision[0]}: Cars collide: {collision[1]}')


main()

# TODO:
# marges auto inbouwen
# meer relevante data: snelheid? gas/throttle?
    
# hoe goed is de monitor: remmen na 0.3s bij piepje: botsing of niet?
# zelf monitor schrijven
# data opslaan
# half kantje problem statement
# slack channel scenic
