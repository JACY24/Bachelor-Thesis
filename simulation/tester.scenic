param map = localPath('../Scenic/assets/maps/CARLA/Town05.xodr')
param carla_map = 'Town05'
param time_step = 1.0/10

import simulation

model scenic.simulators.newtonian.driving_model

# Uniformly select a weather type
param weather = Uniform('ClearNoon', 'CloudyNoon', 
                        'WetNoon', 'MidRainyNoon', 
                        'ClearSunSet')

behavior FollowLaneWithMonitor(laneToFollow=None):
    try:
        do FollowLaneBehavior(laneToFollow=laneToFollow)
    interrupt when parkedCar.distanceTo(ego.corners[0]) < 0.05:
        print('breakinggggg')
        take SetBrakeAction(1)

# OLD SCENARIO:
select_road = Uniform(*network.roads)
select_lanegroup = Uniform(*select_road.laneGroups)

rightCurb = select_lanegroup.curb
spot = new OrientedPoint on rightCurb

ego = new Car left of spot by 0.5,
                    with behavior FollowLaneWithMonitor(laneToFollow=select_lanegroup.lanes[0])
parkedCar = new Car ahead of ego by Range(3, 6)

record round(ego.heading, 4) as drivingCarHeading
record ego.intersects(parkedCar) as intersecting
record ego.corners as drivingCorners
record parkedCar.corners as parkedCorners
record round(ego.speed, 4) as speed
record round(ego.steer, 4) as steer

terminate after 4 seconds
