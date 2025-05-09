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
monitor.reset_window()
alarm = False

# Behavior for when the monitor raises an alarm
behavior Brake():
    global alarm
    alarm = True
    take SetBrakeAction(1)
    take SetSpeedAction(0)
    take SetThrottleAction(0)

behavior BrakewhenIntersecting(lane):
    do FollowLaneBehavior(laneToFollow=lane) until ego.intersects(parkedCar)
    take SetBrakeAction(1)
    take SetSpeedAction(0)
    take SetThrottleAction(0)

# Do followlane behavior until monitor raises an alarm
behavior FollowLaneWithMonitor(laneToFollow=None):
    try:
        do BrakewhenIntersecting(laneToFollow)
    interrupt when monitor.check_for_alarm(round(parkedCar.distanceTo(ego.corners[1]), 4),
                                            round(parkedCar.distanceTo(ego.corners[0]), 4),
                                            round(ego.steer, 4),
                                            int(ego.lane == parkedCar.lane)):
        do Brake()

# Select starting spot for the cars
select_road = network.roads[0]
ego_lane = select_road.lanes[2]

# Create two cars with correct behavior
ego = new Car on ego_lane.centerline,
                    with behavior FollowLaneWithMonitor(ego_lane)

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
record alarm as alarm
record int(ego.lane == parkedCar.lane) as same_lane

require ego.lane == parkedCar.lane implies always ego.lane == parkedCar.lane
require ego.lane != parkedCar.lane implies always ego.lane != parkedCar.lane
require (ego.lane != parkedCar.lane) implies not eventually ego.intersects(parkedCar)

terminate after 5 seconds
