FROM nvcr.io/nvidia/isaac-sim:5.1.0

USER root 
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NOWARNINGS=yes

# ------------------------------------------------------------
# 1. System dependencies (apt) - merged & cleaned
# ------------------------------------------------------------
RUN apt-get update -y -qq && \
    apt-get upgrade -y -qq --no-install-recommends && \
    apt-get install -y -qq \
      libyaml-cpp-dev curl software-properties-common \
      vim v4l-utils exfatprogs \
      openssh-server terminator dbus-x11 \
      python3-pip dirmngr gnupg2 lsb-release \
      telnet git make cmake \
      gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl \
      libqt5gui5 libfuse2 gedit tmux && \
    wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null && \
    apt-add-repository "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main" && \
    apt-get update -y -qq && \
    apt-get install -y -qq cmake && \
    apt-get remove modemmanager -y || true && \
    apt-get autoremove -y -qq && \
    /isaac-sim/python.sh -m pip install colcon-ros && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 2. ROS 2 Jazzy + Robotics Packages
# ------------------------------------------------------------
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && \
    apt-get update -y && \
    apt-get install -f -y && \
    dpkg --configure -a && \
    apt-get install -y software-properties-common mesa-utils libglu1-mesa-dev \
      freeglut3-dev mesa-common-dev libglew-dev libglfw3-dev libglm-dev \
      libao-dev libmpg123-dev libasio-dev libfreetype6-dev libfontconfig1-dev libbrotli-dev && \
    add-apt-repository universe && \
    apt-get update -y && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu noble main" > /etc/apt/sources.list.d/ros2.list && \
    apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y ros-jazzy-desktop \
      ros-jazzy-ament-cmake ros-jazzy-angles ros-jazzy-controller-manager \
      ros-jazzy-pluginlib ros-jazzy-urdf ros-jazzy-yaml-cpp-vendor \
      ros-jazzy-joint-state-publisher* \
      ros-jazzy-cv-bridge ros-jazzy-diagnostic-updater \
      ros-jazzy-moveit ros-jazzy-xacro ros-jazzy-realtime-tools \
      ros-jazzy-control-toolbox ros-jazzy-ros2-control* \
      ros-jazzy-teleop-twist-keyboard ros-jazzy-vision-msgs || { echo "Failed to install ROS 2 packages"; apt-get install -y --fix-broken; exit 1; } && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 3. Python dependencies for Pegasus & PX4 (via Isaac Sim Python)
# ------------------------------------------------------------
WORKDIR /root
RUN pip3 install --force-reinstall --break-system-packages \
    pyros-genmsg jinja2 toml kconfiglib
RUN apt-get update && apt-get install -y pipx && \
    pipx ensurepath && \
    pipx install jsonschema && \
    pipx install future
# ------------------------------------------------------------
# 4. Clone and install Pegasus Simulator (editable, no venv)
# ------------------------------------------------------------
RUN export ISAACSIM_PATH="/isaac-sim" && \
    git clone https://github.com/PegasusSimulator/PegasusSimulator.git && \
    mkdir -p PegasusSimulator/extensions/pegasus.simulator && \
    echo "[build-system]" > PegasusSimulator/extensions/pegasus.simulator/pyproject.toml && \
    echo "requires = [\"setuptools\", \"wheel\", \"toml\"]" >> PegasusSimulator/extensions/pegasus.simulator/pyproject.toml && \
    echo "build-backend = \"setuptools.build_meta\"" >> PegasusSimulator/extensions/pegasus.simulator/pyproject.toml && \
    cd PegasusSimulator/extensions/pegasus.simulator && \
    /isaac-sim/python.sh -m pip install --editable .

# ------------------------------------------------------------
# 5. Clone PX4-Autopilot
# ------------------------------------------------------------
RUN git clone https://github.com/PX4/PX4-Autopilot.git && \
    cd PX4-Autopilot && \
    git checkout v1.14.3 && \
    git submodule update --init --recursive

# ------------------------------------------------------------
# 6. Build PX4 SITL using Isaac Sim Python directly
# ------------------------------------------------------------

RUN find /root/PX4-Autopilot -name CMakeLists.txt \
    -exec grep -l "cmake_minimum_required.*VERSION [0-2]\." {} \; \
    -exec sed -i '1s/.*/cmake_minimum_required(VERSION 3.5)/' {} \;

RUN pip3 install --force-reinstall --break-system-packages \
    jsonschema

RUN cd /root/PX4-Autopilot && \
    make distclean && \
    cmake -B build/px4_sitl_default \
          -S . \
          -DCMAKE_BUILD_TYPE=Release && \
    make -C build/px4_sitl_default px4 && \
    ls -l build/px4_sitl_default/bin/px4 && \
    echo "PX4 SITL BUILD SUCCESSFUL"

# ------------------------------------------------------------
# 7. QGroundControl
# ------------------------------------------------------------
WORKDIR /home/ubuntu
RUN wget https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl-x86_64.AppImage && \
    chmod +x ./QGroundControl-x86_64.AppImage && \
    usermod -a -G dialout ubuntu

# ------------------------------------------------------------
# 8. tmux + config
# ------------------------------------------------------------
RUN mkdir -p /root/.tmux/plugins && \
    git clone https://github.com/tmux-plugins/tpm /root/.tmux/plugins/tpm && \
    wget https://raw.githubusercontent.com/SasaKuruppuarachchi/SasaKuruppuarachchi/main/.tmux.conf -P /root/ && \
    echo 'alias tmuxsrc="tmux source ~/.tmux.conf"' >> /root/.bashrc

# ------------------------------------------------------------
# 9. Isaac Sim environment setup in ~/.bashrc (EXACTLY as provided)
# ------------------------------------------------------------
RUN cat <<'EOF' >> /root/.bashrc

# ---------------------------
# ISAAC SIM SETUP
# ---------------------------
export ISAACSIM_PATH="/isaac-sim"
export ISAACSIM_PYTHON="${ISAACSIM_PATH}/python.sh"
export ISAACSIM="${ISAACSIM_PATH}/isaac-sim.sh"

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
        export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "^${ros_path}" | paste -sd':' -)
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

export PATH="/opt/venv/bin:$PATH"
export PYTHONPATH="/opt/venv/lib/python3.11/site-packages:$PYTHONPATH"
EOF

# ------------------------------------------------------------
# 10. Final ROS sourcing
# ------------------------------------------------------------
RUN echo 'source /opt/ros/jazzy/setup.bash' >> /root/.bashrc

# ------------------------------------------------------------
# 11. Cleanup
# ------------------------------------------------------------
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# ------------------------------------------------------------
# 12. Default entrypoint
# ------------------------------------------------------------
WORKDIR /root
ENTRYPOINT ["/bin/bash"]