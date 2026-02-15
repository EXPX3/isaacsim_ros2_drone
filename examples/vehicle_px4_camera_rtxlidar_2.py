#!/usr/bin/env python
"""
| File: 8_camera_vehicle.py
| License: BSD-3-Clause. Copyright (c) 2024, Marcelo Jacinto. All rights reserved.
| Description: This files serves as an example on how to build an app that makes use of the Pegasus API, 
| where the data is send/received through mavlink, the vehicle is controled using mavlink and
| camera data is sent to ROS2 topics at the same time.
"""

# Imports to start Isaac Sim from this script
import carb
from isaacsim import SimulationApp

# Start Isaac Sim's simulation environment
# Note: this simulation app must be instantiated right after the SimulationApp import, otherwise the simulator will crash
# as this is the object that will load all the extensions and load the actual simulator.
simulation_app = SimulationApp({"headless": False})

# -----------------------------------
# The actual script should start here
# -----------------------------------
import omni.timeline
from omni.isaac.core.world import World
# In camera_lidar_px4_vehicle.py
import omni.graph.core as og
import omni.isaac.core.utils.prims as prims_utils

from omni.isaac.core.objects import DynamicCuboid
import numpy as np

from omni.isaac.core.utils.extensions import enable_extension
enable_extension("isaacsim.sensors.rtx")
import asyncio

# Import the Pegasus API for simulating drones
from pegasus.simulator.params import ROBOTS, SIMULATION_ENVIRONMENTS
from pegasus.simulator.logic.graphical_sensors.monocular_camera import MonocularCamera
from pegasus.simulator.logic.graphical_sensors.lidar import Lidar
from pegasus.simulator.logic.backends.px4_mavlink_backend import PX4MavlinkBackend, PX4MavlinkBackendConfig
from pegasus.simulator.logic.backends.ros2_backend import ROS2Backend
from pegasus.simulator.logic.vehicles.multirotor import Multirotor, MultirotorConfig
from pegasus.simulator.logic.interface.pegasus_interface import PegasusInterface

# Auxiliary scipy and numpy modules
from scipy.spatial.transform import Rotation

class PegasusApp:
    """
    A Template class that serves as an example on how to build a simple Isaac Sim standalone App.
    """

    def __init__(self):
        """
        Method that initializes the PegasusApp and is used to setup the simulation environment.
        """

        # Acquire the timeline that will be used to start/stop the simulation
        self.timeline = omni.timeline.get_timeline_interface()

        # Start the Pegasus Interface
        self.pg = PegasusInterface()

        # Acquire the World, .i.e, the singleton that controls that is a one stop shop for setting up physics,
        # spawning asset primitives, etc.
        self.pg._world = World(**self.pg._world_settings)
        self.world = self.pg.world

        # Launch one of the worlds provided by NVIDIA
        self.pg.load_environment(SIMULATION_ENVIRONMENTS["Stairs Plane"])
        # self.pg.load_environment("/root/examples/rivermark.usd")
        cube_2 = self.world.scene.add(
            DynamicCuboid(
                prim_path="/new_cube_2",
                name="cube_1",
                position=np.array([-3.0, 0, 2.0]),
                scale=np.array([1.0, 1.0, 1.0]),
                size=1.0,
                color=np.array([255, 0, 0]),
            )
        )

        # Create the vehicle
        # Try to spawn the selected robot in the world to the specified namespace
        config_multirotor = MultirotorConfig()
        # Create the multirotor configuration
        mavlink_config = PX4MavlinkBackendConfig({
            "vehicle_id": 0,
            "px4_autolaunch": True,
            "px4_dir": "/root/PX4-Autopilot"
        })
        config_multirotor.backends = [
            PX4MavlinkBackend(mavlink_config), 
            ROS2Backend(vehicle_id=0, 
                        config={
                            "namespace": 'drone', 
                            "pub_sensors": True,
                            "pub_graphical_sensors": True,
                            "pub_state": True,
                            "sub_control": False,
                            "pub_tf": False,})]
        
        # Create a camera and lidar sensors
        config_multirotor.graphical_sensors = [MonocularCamera("cameraa", config={"update_rate": 60.0}), Lidar("rtxlidar", config={})]
        
        Multirotor(
            "/World/quadrotor",
            ROBOTS['Iris'],
            0,
            [0.0, 0.0, 0.07],
            Rotation.from_euler("XYZ", [0.0, 0.0, 0.0], degrees=True).as_quat(),
            config=config_multirotor,
        )

        # Reset the simulation environment so that all articulations (aka robots) are initialized
        self.world.reset()

        # Auxiliar variable for the timeline callback example
       
        self.stop_sim = False
    # Inside the PegasusApp class in camera_lidar_px4_vehicle.py

    # Inside the PegasusApp class in camera_lidar_px4_vehicle.py
# (Ensure you still have 'import omni.graph.core as og' and 'import omni.isaac.core.utils.prims as prims_utils')

    # Inside the PegasusApp class in camera_lidar_px4_vehicle.py

    # Inside the PegasusApp class in camera_lidar_px4_vehicle.py

    def setup_ros2_clock(self):
        import time
        import carb
        import omni.graph.core as og
        from omni.isaac.core.utils.extensions import enable_extension

        graph_path = "/World/ROS_Clock_Graph"

        # Make sure the right extensions are enabled
        enable_extension("omni.graph.action")       # for OnPlaybackTick
        enable_extension("isaacsim.core.nodes")     # for IsaacReadSimulationTime
        enable_extension("isaacsim.ros2.bridge")    # for ROS2PublishClock
        time.sleep(0.5)  # let node registries populate

        og.Controller.edit(
            {"graph_path": graph_path, "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("ReadSimTime",    "isaacsim.core.nodes.IsaacReadSimulationTime"),
                    ("PublishClock",   "isaacsim.ros2.bridge.ROS2PublishClock"),
                ],
                og.Controller.Keys.CONNECT: [
                    # Exec: tick drives the publisher
                    ("OnPlaybackTick.outputs:tick", "PublishClock.inputs:execIn"),
                    # Time value: simulation time into publisher
                    ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"),
                ],
            },
        )



    def run(self):
        """
        Method that implements the application main loop, where the physics steps are executed.
        """
        self.setup_ros2_clock()

        # Start the simulation
        self.timeline.play()
        
        for _ in range(5):
            self.world.step(render=True)

        # The "infinite" loop
        while simulation_app.is_running() and not self.stop_sim:
            # Update the UI of the app and perform the physics step
            self.world.step(render=True)

        # Cleanup and stop
        carb.log_warn("PegasusApp Simulation App is closing.")
        self.timeline.stop()
        simulation_app.close()

def main():

    # Instantiate the template app
    pg_app = PegasusApp()

    # Run the application loop
    pg_app.run()

if __name__ == "__main__":
    main()
