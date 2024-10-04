param map = localPath('../Scenic/assets/maps/CARLA/Town05.xodr')
param carla_map = 'Town05'
param time_step = 1.0/10

model scenic.simulators.newtonian.driving_model

select_road = Uniform(*network.roads)
select_lanegroup = Uniform(*select_road.laneGroups)

rightCurb = select_lanegroup.curb
spot = new OrientedPoint on rightCurb

ego = new Car left of spot by 0.5,
                    with behavior FollowLaneBehavior(laneToFollow=select_lanegroup.lanes[0])
parkedCar = new Car ahead of ego by 3

record round(ego.heading, 4) as drivingCarHeading
record ego.intersects(parkedCar) as intersecting
record ego.corners as drivingCorners
record parkedCar.corners as parkedCorners
record ego.speed as speed

terminate after 3 seconds
