#!/bin/bash
xhost +local:

docker run --name isaac-sim-ros2-humble-mountpegasus --entrypoint bash -it --gpus all -e "ACCEPT_EULA=Y" --rm --network=host --ipc=host --privileged --shm-size=16G \
    -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
    -e ROS_DOMAIN_ID=42 \
    -v ~/docker/isaac-sim-ros2-humble-mountpegasus/cache/kit:/isaac-sim/kit/cache/Kit:rw \
    -v ~/docker/isaac-sim-ros2-humble-mountpegasus/cache/ov:/root/.cache/ov:rw \
    -v ~/docker/isaac-sim-ros2-humble-mountpegasus/cache/pip:/root/.cache/pip:rw \
    -v ~/docker/isaac-sim-ros2-humble-mountpegasus/cache/glcache:/root/.cache/nvidia/GLCache:rw \
    -v ~/docker/isaac-sim-ros2-humble-mountpegasus/cache/computecache:/root/.nv/ComputeCache:rw \
    -v ~/docker/isaac-sim-ros2-humble-mountpegasus/logs:/root/.nvidia-omniverse/logs:rw \
    -v ~/docker/isaac-sim-ros2-humble-mountpegasus/data:/root/.local/share/ov/data:rw \
    -v ~/docker/isaac-sim-ros2-humble-mountpegasus/documents:/root/Documents:rw \
    -v /home/giri/Documents/robotspace/IsaacSim-ros_workspaces:/root/IsaacSim-ros_workspaces \
    -v /home/giri/Documents/robotspace/IsaacSim-files:/root/IsaacSim-files \
    -v /home/giri/Documents/robotspace/ws_isaacsim_ros2_drone_2/PegasusSimulator:/root/PegasusSimulator \
    -v /home/giri/Documents/robotspace/ws_isaacsim_ros2_drone_2/isaacsim_ros2_drone/examples:/root/examples \
    -v /home/giri/Documents/robotspace/ws_isaacsim_ros2_drone_2/isaacsim_ros2_drone/colcon_isaac_ws/config/px4_config_for_non_sim_time.yaml:/opt/ros/humble/share/mavros/launch/px4_config.yaml \
    --env="DISPLAY" \
    -v $HOME/.Xauthority:/root/.Xauthority:rw \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    --workdir="/root/colcon_isaac_ws" \
    --volume="$(pwd)/../colcon_isaac_ws:/root/colcon_isaac_ws" \
    --volume="$(pwd)/../lidar_cfg/hokuyo:/isaac-sim/exts/omni.isaac.sensor/data/lidar_configs/hokuyo" \
    --volume="/home/giri/Documents/robotspace/bags/:/root/colcon_isaac_ws/bags/" \
    isaacsim510_mountpegasus_humble:latest