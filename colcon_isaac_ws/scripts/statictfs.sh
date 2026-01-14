#!/usr/bin/env bash

echo "Launching static transforms..."

# ==========================================
# Tree Structure:
# drone_base_link_frd -> altax_center_frd -> (rtxlidar, camera)
# ==========================================

# 1. drone_base_link_frd -> altax_center_frd
# Offset: Y = -0.095 (45mm Left/Right adjustment based on your comment logic)
# Rotation: None
ros2 run tf2_ros static_transform_publisher \
0.0 -0.095 0.0 0 0 0 drone_base_link_frd altax_center_frd \
--ros-args -p use_sim_time:=true &

# 2. altax_center_frd -> rtxlidar
# Offset: x=0.075, y=0.24, z=0.075
# Rotation: Pitch = -20 degrees (approx -0.349066 radians)
# Syntax: x y z yaw pitch roll parent child
ros2 run tf2_ros static_transform_publisher \
0.075 0.24 0.075 0 -0.349066 0 altax_center_frd rtxlidar \
--ros-args -p use_sim_time:=true &

# 3. altax_center_frd -> camera
# Offset: z=0.20 (20cm down)
# Rotation: None
ros2 run tf2_ros static_transform_publisher \
0.0 0.0 0.20 0 0 0 altax_center_frd camera \
--ros-args -p use_sim_time:=true &

# 4. camera_body_frd -> gimbal_link
# (Commented out in Python script, kept here for reference if needed later)
# ros2 run tf2_ros static_transform_publisher \
# 0 0 0 0 0 0 camera_body_frd gimbal_link \
# --ros-args -p use_sim_time:=true &

echo "All static transforms launched in background."