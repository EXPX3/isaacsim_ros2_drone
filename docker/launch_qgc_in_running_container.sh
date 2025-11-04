#!/bin/bash

# Launch QGroundControl (extracted version) inside the Isaac Sim ROS2 container as ubuntu user

docker exec -it \
  --user ubuntu \
  --workdir /home/ubuntu \
  isaac-sim-ros2 \
  bash -c "./QGroundControl/AppRun"