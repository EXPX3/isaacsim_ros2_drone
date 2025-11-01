FROM nvcr.io/nvidia/isaac-sim:5.1.0

ENV DEBIAN_FRONTEND=noninteractive
# install dependencies via apt
ENV DEBCONF_NOWARNINGS=yes

USER root
# install dependencies via apt
RUN set -x && \
  apt-get update -y -qq && \
  apt-get upgrade -y -qq --no-install-recommends && \
  apt-get install -y -qq \
    libyaml-cpp-dev curl software-properties-common \
    vim v4l-utils exfat-* \
    openssh-server \
    terminator dbus-x11 \
    python3-pip && \
  : "remove cache" && \
  apt-get autoremove -y -qq && \
  rm -rf /var/lib/apt/lists/*

RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null && \
    apt-add-repository "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main" && \
    apt update && \
    apt install -y -qq cmake

    # Install common tools and enable universe repo
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    gnupg2 \
    lsb-release \
    && add-apt-repository universe \
    && apt-get update \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 3. Add ROS 2 Jazzy repository (noble)
# ------------------------------------------------------------
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
        -o /usr/share/keyrings/ros-archive-keyring.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
        http://packages.ros.org/ros2/ubuntu noble main" \
        > /etc/apt/sources.list.d/ros2.list

# ------------------------------------------------------------
# 4. Install ROS 2 Jazzy + your extra packages
# ------------------------------------------------------------
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        # ---- graphics / audio libs you wanted (most already in Isaac Sim) ----
        mesa-utils libglu1-mesa-dev freeglut3-dev mesa-common-dev \
        libglew-dev libglfw3-dev libglm-dev libao-dev libmpg123-dev libasio-dev \
        \
        # ---- ROS 2 Jazzy -------------------------------------------------
        ros-jazzy-desktop \
        \
        # Build & core tools
        ros-jazzy-ament-cmake \
        \
        # Robot-specific
        ros-jazzy-angles \
        ros-jazzy-controller-manager \
        ros-jazzy-pluginlib \
        ros-jazzy-urdf \
        ros-jazzy-yaml-cpp-vendor \
        \
        # Joint state (exact names, no glob)
        ros-jazzy-joint-state-publisher \
        ros-jazzy-joint-state-publisher-gui \
        \
        # Vision & diagnostics
        ros-jazzy-cv-bridge \
        ros-jazzy-diagnostic-updater \
        \
        # Motion planning
        ros-jazzy-moveit \
        \
        # Additional packages you listed
        ros-jazzy-xacro \
        ros-jazzy-realtime-tools \
        ros-jazzy-control-toolbox \
        ros-jazzy-ros2-control \
        ros-jazzy-ros2-controllers \
        ros-jazzy-teleop-twist-keyboard \
        ros-jazzy-vision-msgs \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -q -y --no-install-recommends \
    dirmngr \
    gnupg2 \
    lsb-release \
    python3-colcon-ros \
    telnet \
    nano \
    && apt-get clean

RUN apt install git make cmake python3-pip python3.12-venv -y

# Drone dev
WORKDIR /root
RUN python3 -m venv /opt/build-venv && \
    /opt/build-venv/bin/pip install --upgrade pip && \
    /opt/build-venv/bin/pip install --no-cache-dir \
        kconfiglib jinja2 empy jsonschema pyros-genmsg \
        packaging toml numpy future

# Make it the default python for subsequent RUN commands
ENV PATH="/opt/build-venv/bin:$PATH"


RUN export ISAACSIM_PATH="/isaac-sim" && \
    echo 'export ISAACSIM_PATH="/isaac-sim"' >> ~/.bashrc && \
    git clone https://github.com/PegasusSimulator/PegasusSimulator.git && \
    cd /root/PegasusSimulator/extensions && \
    /isaac-sim/python.sh -m pip install --editable pegasus.simulator


WORKDIR /root
RUN git clone https://github.com/PX4/PX4-Autopilot.git
WORKDIR /root/PX4-Autopilot/
RUN git checkout v1.14.3
RUN git submodule update --init --recursive

# Install QGroundControl and configure user
WORKDIR /home/ubuntu
RUN wget https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl-x86_64.AppImage && \
    chmod +x ./QGroundControl-x86_64.AppImage && \
    usermod -a -G dialout ubuntu

# Install and configure tmux
RUN git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm && \
    wget https://raw.githubusercontent.com/SasaKuruppuarachchi/SasaKuruppuarachchi/main/.tmux.conf -P ~/ && \
    echo 'alias tmuxsrc="tmux source ~/.tmux.conf"' >> ~/.bashrc

# Configure bash environment
RUN echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc && \
    echo 'export ISAACSIM_PATH="/isaac-sim"' >> ~/.bashrc && \
    echo 'alias ISAACSIM_PYTHON="/isaac-sim/python.sh"' >> ~/.bashrc && \
    echo 'alias ISAACSIM="/isaac-sim/runapp.sh"' >> ~/.bashrc
    # Note: /root/colcon_ws is not created; remove or create it if needed
    # echo 'source /root/colcon_ws/install/setup.sh' >> ~/.bashrc

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*


ENTRYPOINT ["/bin/bash"]