import random
import numpy

param map = localPath('../../Scenic/assets/maps/CARLA/Town05.xodr')
param carla_map = 'Town05'
param time_step = 1.0/10

model scenic.simulators.newtonian.driving_model

# Set a seed so that scene sampling becomes deterministic
if globalParameters['seed']:
    random.seed(globalParameters['seed'])
    numpy.random.seed(globalParameters['seed'])

# Select starting spot for the cars
select_road = Uniform(*network.roads)
select_lanegroup = Uniform(*select_road.laneGroups)
select_ego_lane = Uniform(*select_lanegroup.lanes)

# Create two cars with correct behavior
ego = new Car on select_ego_lane.centerline,
                    with behavior FollowLaneBehavior(laneToFollow=select_ego_lane)

select_npc_lane = Uniform(*select_lanegroup.lanes)
parkedCar = new Car on visible select_npc_lane.centerline#,
                    #with behavior FollowLaneBehavior(laneToFollow=select_npc_lane)

# Record the observations of interest
record round(ego.heading, 4) as drivingCarHeading
record ego.intersects(parkedCar) as intersecting
record ego.corners as drivingCorners
record parkedCar.corners as parkedCorners
record round(ego.speed, 4) as speed
record round(ego.steer, 4) as steer
record int(select_ego_lane == select_npc_lane) as same_lane 

require (select_ego_lane == select_npc_lane) implies eventually ego.intersects(parkedCar)

terminate after 5 seconds
