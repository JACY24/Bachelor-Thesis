import scenic
from scenic.simulators.newtonian import NewtonianSimulator
from math import dist, degrees, cos, sin
from shapely.geometry import Polygon

NUM_SIMULATIONS = 20
CAR_WIDTH = 2
CAR_LENGTH = 4.5

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
        print(list(map(lambda x: (x[0], degrees(x[1])) , dictionary[key])))


def calculateRotatedPoint(point: tuple[float, float], centerCoords: tuple[float, float], theta: float) -> tuple[float,float]:
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
    tempX = point[0] - centerCoords[0]
    tempY = point[1]- centerCoords[1]

    rotatedX = tempX*cos(theta) - tempY*sin(theta)
    rotatedY = tempX*sin(theta) + tempY*sin(theta)

    return (rotatedX+centerCoords[0], rotatedY+centerCoords[1])


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
    topRightX = center[0] + 0.5*length + 0.5*width
    topLeftX = center[0] + 0.5*length - 0.5*width
    bottomRightX = center[0] - 0.5*length + 0.5*width
    bottomLeftX = center[0] - 0.5*length - 0.5*width

    topRightY = center[1] + 0.5*length + 0.5*width
    topLeftY = center[1] + 0.5*length - 0.5*width
    bottomRightY = center[1] - 0.5*length + 0.5*width
    bottomLeftY = center[1] - 0.5*length - 0.5*width

    topRightCoord = calculateRotatedPoint((topRightX, topRightY), center, theta)
    bottomRightCoord = calculateRotatedPoint((bottomRightX, bottomRightY), center, theta)
    topLeftCoord = calculateRotatedPoint((topLeftX, topLeftY), center, theta)
    bottomLeftCoord = calculateRotatedPoint((bottomLeftX, bottomLeftY), center, theta)

    return Polygon([bottomLeftCoord, topLeftCoord, topRightCoord, bottomRightCoord])


scenario = scenic.scenarioFromFile('simulation/test.scenic',
                                   model='scenic.simulators.newtonian.driving_model',
                                   mode2D=True)
scene, _ = scenario.generate()
simulator = NewtonianSimulator()
collisions = []

for i in range(NUM_SIMULATIONS):
    scene, _ = scenario.generate()
    simulation = simulator.simulate(scene, maxIterations = 10)

    if simulation:  # `simulate` can return None if simulation fails
        result = simulation.result


        # The parked car heading (1 value per simulation)
        parkedCarHeading = result.records['parkedCarHeading']
        # The driving car heading (a list of tuples per time step)
        drivingCarHeading = result.records['drivingCarHeading']

        # go through each time step and check if the cars intersect at some point
        for j, state in enumerate(result.trajectory):
            # positions of the cars
            _, parkedCarPos, drivingCarPos = state

            collided = False

            parkedCar = createRotatedRectangle(parkedCarPos, CAR_LENGTH, CAR_WIDTH, parkedCarHeading)
            drivingCar = createRotatedRectangle(drivingCarPos, CAR_LENGTH, CAR_WIDTH, drivingCarHeading[j][1])

            if parkedCar.intersects(drivingCar):
                collided = True
                break

        collisions.append((i, collided))


for collision in collisions:
    print(f'Simulation {collision[0]}: Cars collide: {collision[1]}')

# TODO:
# marges auto inbouwen
# meer relevante data: snelheid? gas/throttle?
    
# hoe goed is de monitor: remmen na 0.3s bij piepje: botsing of niet?
# zelf monitor schrijven
# data opslaan
    