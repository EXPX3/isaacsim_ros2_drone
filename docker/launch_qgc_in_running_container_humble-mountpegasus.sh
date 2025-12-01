#!/bin/bash

# Launch QGroundControl (extracted version) inside the Isaac Sim ROS2 container as ubuntu user

docker exec -it \
  --user ros \
  --workdir /home/ubuntu \
  isaac-sim-ros2-humble-mountpegasus \
  bash -c "./QGroundControl/AppRun"