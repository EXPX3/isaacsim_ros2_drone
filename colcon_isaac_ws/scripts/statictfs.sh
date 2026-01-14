#!/usr/bin/env bash

echo "Launching static transforms..."

# Syntax: x y z yaw pitch roll parent child --ros-args -p use_sim_time:=true

# ros2 run tf2_ros static_transform_publisher \
# 0.0 0.0 0.0 0 0 0 map_ned drone_base_link_frd \
# --ros-args -p use_sim_time:=true &

ros2 run tf2_ros static_transform_publisher \
0.0 0.0 0.15 0 0 0 drone_base_link_frd altax_center_frd \
--ros-args -p use_sim_time:=true &

ros2 run tf2_ros static_transform_publisher \
0.12 0.0 0.03 0 1.5708 0 altax_center_frd camera \
--ros-args -p use_sim_time:=true &

ros2 run tf2_ros static_transform_publisher \
0.0 0.0 0.08 0 0 0 altax_center_frd rtxlidar \
--ros-args -p use_sim_time:=true &

echo "All static transforms launched in background."