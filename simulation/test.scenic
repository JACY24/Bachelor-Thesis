param map = localPath('../Scenic/assets/maps/CARLA/Town05.xodr')
param carla_map = 'Town05'
param time_step = 1.0/10

model scenic.simulators.newtonian.driving_model

ego = new Car

rightCurb = ego.laneGroup.curb
spot = new OrientedPoint on visible rightCurb

parkedCar = new Car left of spot by 0.5
drivingCar = new Car behind parkedCar by 3, 
                    with behavior FollowLaneBehavior(laneToFollow=ego.laneGroup.lanes[len(ego.laneGroup.lanes)-1])

record initial round(parkedCar.heading, 4) as parkedCarHeading
record round(drivingCar.heading, 4) as drivingCarHeading

require always parkedCar not in intersection
require always ((distance to parkedCar) > 8)

terminate after 3 seconds
