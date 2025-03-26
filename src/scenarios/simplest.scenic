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
select_road = network.roads[0]
ego_lane = select_road.lanes[2]

# Create two cars with correct behavior
ego = new Car on ego_lane.centerline,
                    with behavior FollowLaneUntilIntersect(ego_lane)

offset = (Uniform(-1,1)*Range(0,8),0,0)
point = new OrientedPoint ahead of ego by 3
parked_car_pos = offset relative to point
parkedCar = new Car at parked_car_pos#,
                    #with behavior FollowLaneBehavior(laneToFollow=select_npc_lane)

# Record the observations of interest
record round(ego.heading, 4) as drivingCarHeading
record ego.intersects(parkedCar) as intersecting
record ego.corners as drivingCorners
record parkedCar.corners as parkedCorners
record round(ego.speed, 4) as speed
record round(ego.steer, 4) as steer
record int(ego.lane == parkedCar.lane) as same_lane

require (ego.lane == parkedCar.lane) implies eventually ego.intersects(parkedCar)
require ego.lane == parkedCar.lane implies always ego.lane == parkedCar.lane
require ego.lane != parkedCar.lane implies always ego.lane != parkedCar.lane
require (ego.lane != parkedCar.lane) implies not eventually ego.intersects(parkedCar)

terminate after 5 seconds
