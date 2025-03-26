import random
import numpy

param map = localPath('../../Scenic/assets/maps/CARLA/Town05.xodr')
param carla_map = 'Town05'
param time_step = 1.0/10

model scenic.simulators.newtonian.driving_model

behavior FollowLaneUntilIntersect(laneToFollow):
    do FollowLaneBehavior(laneToFollow=laneToFollow) until ego.intersects(parkedCar)
    take SetBrakeAction(1)
    take SetSpeedAction(0)
    take SetThrottleAction(0)

# Set a seed so that scene sampling becomes deterministic
if globalParameters['seed']:
    random.seed(globalParameters['seed'])
    numpy.random.seed(globalParameters['seed'])

# Select starting spot for the cars
select_road = Uniform(*network.roads)
select_lanegroup = Uniform(*select_road.laneGroups)
start_spot = new OrientedPoint on select_lanegroup.lanes[-1].leftEdge

# Create two cars with correct behavior
ego = new Car left of start_spot by 0.5,
                    with behavior FollowLaneUntilIntersect(laneToFollow=select_lanegroup.lanes[-1])

parkedCar = new Car ahead of ego by Range(3, 6)

# Record the observations of interest
record round(ego.heading, 4) as drivingCarHeading
record ego.intersects(parkedCar) as intersecting
record ego.corners as drivingCorners
record parkedCar.corners as parkedCorners
record round(ego.speed, 4) as speed
record round(ego.steer, 4) as steer

terminate after 5 seconds
