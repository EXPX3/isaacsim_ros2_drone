#!/bin/bash
xhost +local:

docker run --name isaac-sim-ros2 --entrypoint bash -it --gpus device=1 -e "ACCEPT_EULA=Y" --rm --network=host --privileged --shm-size=16G \
    -v ~/docker/isaac-sim-ros2/cache/kit:/isaac-sim/kit/cache/Kit:rw \
    -v ~/docker/isaac-sim-ros2/cache/ov:/root/.cache/ov:rw \
    -v ~/docker/isaac-sim-ros2/cache/pip:/root/.cache/pip:rw \
    -v ~/docker/isaac-sim-ros2/cache/glcache:/root/.cache/nvidia/GLCache:rw \
    -v ~/docker/isaac-sim-ros2/cache/computecache:/root/.nv/ComputeCache:rw \
    -v ~/docker/isaac-sim-ros2/logs:/root/.nvidia-omniverse/logs:rw \
    -v ~/docker/isaac-sim-ros2/data:/root/.local/share/ov/data:rw \
    -v ~/docker/isaac-sim-ros2/documents:/root/Documents:rw \
    -v /home/giri/Documents/robotspace/IsaacSim-ros_workspaces:/root/IsaacSim-ros_workspaces \
    -v /home/giri/Documents/robotspace/IsaacSim-files:/root/IsaacSim-files \
    -v /home/giri/Documents/robotspace/ws_isaacsim_ros2_drone_2/PegasusSimulator:/root/PegasusSimulator \
    -v /home/giri/Documents/robotspace/ws_isaacsim_ros2_drone_2/mavros:/root/IsaacSim-ros_workspaces/jazzy_ws/src/mavros \
    -v /home/giri/Documents/robotspace/ws_isaacsim_ros2_drone_2/9_ros2_graph_lidar_examples:/root/9_ros2_graph_lidar_examples \
    -v /home/giri/Documents/robotspace/ws_isaacsim_ros2_drone_2/isaacsim_ros2_drone/rviz_config:/root/rviz_config \
    --env="DISPLAY" \
    -v $HOME/.Xauthority:/root/.Xauthority:rw \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    --workdir="/root/colcon_isaac_ws" \
    --volume="$(pwd)/../colcon_isaac_ws:/root/colcon_isaac_ws" \
    --volume="$(pwd)/../colcon_isaac_ws:/root/colcon_isaac_ws" \
    --volume="$(pwd)/../lidar_cfg/hokuyo:/isaac-sim/exts/omni.isaac.sensor/data/lidar_configs/hokuyo" \
    isaacsim510_mountpegasus_humble:latest