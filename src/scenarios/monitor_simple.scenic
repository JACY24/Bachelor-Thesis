import random
import numpy

param map = localPath('../../Scenic/assets/maps/CARLA/Town05.xodr')
param carla_map = 'Town05'
param time_step = 1.0/10

# Set a seed so that scene sampling becomes deterministic
if globalParameters['seed']:
    random.seed(globalParameters['seed'])
    numpy.random.seed(globalParameters['seed'])

import src.monitor as monitor

model scenic.simulators.newtonian.driving_model

# Initialize the monitor
monitor = globalParameters['monitor']
alarm = False

# Behavior for when the monitor raises an alarm
behavior Brake():
    global alarm 
    alarm = True
    take SetBrakeAction(1)

behavior FollowLaneUntilIntersect(laneToFollow):
    do FollowLaneBehavior(laneToFollow=laneToFollow) until ego.intersects(parkedCar)
    take SetBrakeAction(1)
    take SetSpeedAction(0)
    take SetThrottleAction(0)

# Do followlane behavior until monitor raises an alarm
behavior FollowLaneWithMonitor(laneToFollow=None):
    try:
        do FollowLaneUntilIntersect(laneToFollow=laneToFollow)
    interrupt when monitor.check_for_alarm(round(parkedCar.distanceTo(ego.corners[1]), 4),
                                            round(parkedCar.distanceTo(ego.corners[0]), 4),
                                            round(ego.steer, 4)):
        do Brake()

# Select starting spot for the cars
select_road = Uniform(*network.roads)
select_lanegroup = Uniform(*select_road.laneGroups)
select_ego_lane = Uniform(*select_lanegroup.lanes)

# Create two cars with correct behavior
ego = new Car on select_ego_lane.centerline,
                    with behavior FollowLaneWithMonitor(laneToFollow=select_ego_lane)

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
record alarm as alarm

terminate after 5 seconds

