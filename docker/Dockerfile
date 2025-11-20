# syntax=docker/dockerfile:1.7
FROM nvcr.io/nvidia/isaac-sim:5.1.0

USER root
ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NOWARNINGS=yes \
    PX4_VENV=/opt/px4_venv

# ------------------------------------------------------------
# 1. Fix apt lists + System dependencies
# ------------------------------------------------------------
RUN mkdir -p /var/lib/apt/lists/partial && \
    chown -R root:root /var/lib/apt/lists && \
    chmod -R 755 /var/lib/apt/lists && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update -y -qq && \
    apt-get upgrade -y -qq --no-install-recommends && \
    apt-get install -y -qq --no-install-recommends \
      git wget make build-essential \
      libc6-dev libstdc++-12-dev \
      python3-pip python3-venv ca-certificates \
      libyaml-cpp-dev curl software-properties-common \
      vim v4l-utils exfatprogs openssh-server terminator dbus-x11 \
      dirmngr gnupg2 lsb-release telnet gstreamer1.0-plugins-bad \
      gstreamer1.0-libav gstreamer1.0-gl libqt5gui5 libfuse2 gedit tmux \
      mesa-utils libglu1-mesa-dev freeglut3-dev mesa-common-dev \
      libglew-dev libglfw3-dev libglm-dev libao-dev libmpg123-dev \
      libasio-dev libfreetype6-dev libfontconfig1-dev libbrotli-dev && \
    \
    # Add Kitware repo with proper key isolation
    wget -qO - https://apt.kitware.com/keys/kitware-archive-latest.asc | \
      gpg --dearmor -o /usr/share/keyrings/kitware-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ noble main" > /etc/apt/sources.list.d/kitware.list && \
    \
    apt-get update -y -qq && \
    apt-get install -y -qq cmake && \
    \
    # Fully remove Kitware repo and key
    rm -f /etc/apt/sources.list.d/kitware.list && \
    rm -f /usr/share/keyrings/kitware-archive-keyring.gpg && \
    \
    # Remove conflicting packages
    apt-get remove -y modemmanager || true && \
    apt-get autoremove -y -qq && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 2. ROS 2 Jazzy + Robotics Packages
# ------------------------------------------------------------
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && \
    add-apt-repository universe -y && \
    \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu noble main" > /etc/apt/sources.list.d/ros2.list && \
    \
    apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
      python3-rosdep python3-colcon-common-extensions \
      ros-jazzy-desktop \
      ros-jazzy-ament-cmake ros-jazzy-angles ros-jazzy-controller-manager \
      ros-jazzy-pluginlib ros-jazzy-urdf ros-jazzy-yaml-cpp-vendor \
      ros-jazzy-joint-state-publisher* ros-jazzy-cv-bridge \
      ros-jazzy-diagnostic-updater ros-jazzy-moveit ros-jazzy-xacro \
      ros-jazzy-realtime-tools ros-jazzy-control-toolbox \
      ros-jazzy-ros2-control* ros-jazzy-teleop-twist-keyboard ros-jazzy-topic-based-ros2-control \
      ros-jazzy-vision-msgs && \
    \
    /isaac-sim/python.sh -m pip install --no-cache-dir colcon-ros && \
    \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 3. Clone PX4-Autopilot
# ------------------------------------------------------------
WORKDIR /root
RUN git clone https://github.com/PX4/PX4-Autopilot.git && \
    cd PX4-Autopilot && \
    git checkout v1.16.0 && \
    git submodule update --init --recursive

# ------------------------------------------------------------
# 4. Setup PX4 Virtual Environment + Dependencies
# ------------------------------------------------------------
RUN python3 -m venv $PX4_VENV && \
    $PX4_VENV/bin/pip install --no-cache-dir --upgrade pip && \
    $PX4_VENV/bin/pip install --no-cache-dir \
      kconfiglib jinja2 "empy<4.0" jsonschema pyros-genmsg \
      packaging toml numpy future pyyaml

# ------------------------------------------------------------
# 5. Build PX4 SITL (with Isaac Sim compatibility patches)
# ------------------------------------------------------------
RUN . $PX4_VENV/bin/activate && \
    cd PX4-Autopilot && \
    # find /root/PX4-Autopilot -name CMakeLists.txt \
    # -exec grep -l "cmake_minimum_required.*VERSION [0-2]\." {} \; \
    # -exec sed -i '1s/.*/cmake_minimum_required(VERSION 3.5)/' {} \; && \
    # sed -i '/#include <unistd.h>/a #include <stdint.h>' platforms/posix/src/px4/common/px4_daemon/pxh.cpp && \
    # sed -i 's/return _data\[i\]\[j\];/return _data[0][0];/g' src/lib/matrix/matrix/Matrix.hpp && \
    make px4_sitl_default && \
    echo "PX4 SITL BUILD COMPLETE — BINARY READY" && \
    deactivate

# ------------------------------------------------------------
# 6. Clone and install Pegasus Simulator (editable)
# ------------------------------------------------------------
RUN export ISAACSIM_PATH="/isaac-sim" && \
    git clone https://github.com/PegasusSimulator/PegasusSimulator.git /root/PegasusSimulator && \
    mkdir -p /root/PegasusSimulator/extensions/pegasus.simulator && \
    { \
      echo "[build-system]"; \
      echo "requires = [\"setuptools\", \"wheel\", \"toml\"]"; \
      echo "build-backend = \"setuptools.build_meta\""; \
    } > /root/PegasusSimulator/extensions/pegasus.simulator/pyproject.toml && \
    /isaac-sim/python.sh -m pip install --editable /root/PegasusSimulator/extensions/pegasus.simulator

# ------------------------------------------------------------
# 7. QGroundControl
# ------------------------------------------------------------
WORKDIR /home/ubuntu

RUN wget -q https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl-x86_64.AppImage -O QGroundControl.AppImage && \
    chmod +x QGroundControl.AppImage && \
    ./QGroundControl.AppImage --appimage-extract && \
    mv squashfs-root QGroundControl && \
    chmod +x QGroundControl/AppRun && \
    rm QGroundControl.AppImage && \
    usermod -a -G dialout ubuntu || true

# ------------------------------------------------------------
# 8. tmux + config
# ------------------------------------------------------------
RUN mkdir -p /root/.tmux/plugins && \
    git clone https://github.com/tmux-plugins/tpm /root/.tmux/plugins/tpm && \
    wget -q https://raw.githubusercontent.com/SasaKuruppuarachchi/SasaKuruppuarachchi/main/.tmux.conf -O /root/.tmux.conf && \
    echo 'alias tmuxsrc="tmux source ~/.tmux.conf"' >> /root/.bashrc

# ------------------------------------------------------------
# 9. Isaac Sim environment setup in ~/.bashrc
# ------------------------------------------------------------
RUN cat <<'EOF' >> /root/.bashrc

# ---------------------------
# ISAAC SIM SETUP
# ---------------------------
export ISAACSIM_PATH="/isaac-sim"
export ISAACSIM_PYTHON="${ISAACSIM_PATH}/python.sh"
export ISAACSIM="${ISAACSIM_PATH}/isaac-sim.sh"
alias ISAACSIM_PYTHON="/isaac-sim/python.sh"

isaac_run() {
    if [ ! -x "$ISAACSIM_PYTHON" ]; then
        echo "IsaacSim python.sh not found at: $ISAACSIM_PYTHON"
        return 1
    fi
    if [ ! -x "$ISAACSIM" ]; then
        echo "IsaacSim launcher not found at: $ISAACSIM"
        return 1
    fi

    unset ROS_VERSION ROS_PYTHON_VERSION ROS_DISTRO AMENT_PREFIX_PATH COLCON_PREFIX_PATH PYTHONPATH CMAKE_PREFIX_PATH

    local ros_paths=()
    ros_paths+=("/opt/ros/humble")
    ros_paths+=("/opt/ros/jazzy")
    ros_paths+=("/opt/ros/iron")
    for ros_path in "${ros_paths[@]}"; do
        export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "^${ros_path}" | paste -sd ':' -)
    done

    if [ -f /etc/os-release ]; then
        UBUNTU_VERSION=$(grep "^VERSION_ID=" /etc/os-release | cut -d'"' -f2)
    fi

    if [[ "$UBUNTU_VERSION" == "24.04" ]]; then
        export ROS_DISTRO=jazzy
        export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
        export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${ISAACSIM_PATH}/exts/isaacsim.ros2.bridge/jazzy/lib"
        echo "Detected Ubuntu 24.04 -> Using ROS_DISTRO=jazzy"
    else
        export ROS_DISTRO=humble
        export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
        export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${ISAACSIM_PATH}/exts/isaacsim.ros2.bridge/humble/lib"
        echo "Detected Ubuntu ${UBUNTU_VERSION:-unknown} -> Using ROS_DISTRO=humble"
    fi

    if [ $# -eq 0 ]; then
        echo "Launching Isaac Sim GUI..."
        "${ISAACSIM}"
    elif [[ "$1" == --* ]]; then
        echo "Launching Isaac Sim with options: $*"
        "${ISAACSIM}" "$@"
    elif [ -f "$1" ]; then
        local SCRIPT_PATH="$1"
        shift
        echo "Running Python script with Isaac Sim: $SCRIPT_PATH"
        "${ISAACSIM_PYTHON}" "$SCRIPT_PATH" "$@"
    else
        echo "Unknown argument or file not found: '$1'"
        return 1
    fi
}

# Source ROS 2
source /opt/ros/jazzy/setup.bash 2>/dev/null || echo "ROS Jazzy not found"
EOF
# ------------------------------------------------------------
# 10. Final Cleanup
# ------------------------------------------------------------
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
           /root/.cache/pip
# ------------------------------------------------------------
# 11. Default Workdir & Entrypoint
# ------------------------------------------------------------
WORKDIR /root
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["cd /root/PX4-Autopilot && ./build/px4_sitl_default/bin/px4 -d"] 