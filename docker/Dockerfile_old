FROM nvcr.io/nvidia/isaac-sim:4.5.0

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NOWARNINGS=yes

# Install all APT dependencies in one layer
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
    apt-get remove modemmanager -y && \
    apt-get autoremove -y -qq && \
    /isaac-sim/python.sh -m pip install colcon-ros

# Install ROS 2 Humble
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && \
    apt-get update -y && \
    apt-get install -f -y && \
    dpkg --configure -a && \
    # Ensure correct version of libbrotli1
    apt-get install -y --allow-downgrades libbrotli1=1.0.9-2build6 && \
    apt-get install -y software-properties-common mesa-utils libglu1-mesa-dev \
      freeglut3-dev mesa-common-dev libglew-dev libglfw3-dev libglm-dev \
      libao-dev libmpg123-dev libasio-dev libfreetype6-dev libfontconfig1-dev libbrotli-dev && \
    add-apt-repository universe && \
    apt-get update -y && \
    apt-get install -y curl && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null && \
    apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y ros-humble-desktop \
      ros-humble-ament-cmake ros-humble-angles ros-humble-controller-manager \
      ros-humble-pluginlib ros-humble-urdf ros-humble-yaml-cpp-vendor ros-humble-joint-state-pub* \
      ros-humble-cv-bridge ros-humble-diagnostic-updater \
      ros-humble-moveit ros-humble-xacro ros-humble-realtime-tools \
      ros-humble-control-toolbox ros-humble-ros2-control* \
      ros-humble-teleop-twist-keyboard ros-humble-vision-msgs || { echo "Failed to install ROS 2 packages"; apt-get install -y --fix-broken; exit 1; } && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Ensure Python deps are available before Pegasus install
WORKDIR /root
# RUN /isaac-sim/python.sh -m pip install \
#       kconfiglib jinja2 empy jsonschema pyros-genmsg packaging toml numpy future && \
#     git clone https://github.com/PegasusSimulator/PegasusSimulator.git && \
#     cd PegasusSimulator/extensions/pegasus.simulator && \
#     /isaac-sim/python.sh setup.py develop

RUN pip3 install kconfiglib jinja2 empy jsonschema pyros-genmsg packaging toml numpy future

# Clone and patch Pegasus with pyproject.toml for editable install
RUN git clone https://github.com/Robotgir/PegasusSimulator_IsaacSim_4.5.git && \
    mkdir -p PegasusSimulator/extensions/pegasus.simulator && \
    echo "[build-system]" > PegasusSimulator/extensions/pegasus.simulator/pyproject.toml && \
    echo "requires = [\"setuptools\", \"wheel\", \"toml\"]" >> PegasusSimulator/extensions/pegasus.simulator/pyproject.toml && \
    echo "build-backend = \"setuptools.build_meta\"" >> PegasusSimulator/extensions/pegasus.simulator/pyproject.toml && \
    cd PegasusSimulator/extensions/pegasus.simulator && \
    /isaac-sim/python.sh -m pip install --editable .


RUN git clone https://github.com/PX4/PX4-Autopilot.git && \
    cd PX4-Autopilot && \
    git checkout v1.14.1 && \
    git submodule update --init --recursive

# Install QGroundControl and configure user
WORKDIR /home/ubuntu
RUN wget https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl.AppImage && \
    chmod +x ./QGroundControl.AppImage && \
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