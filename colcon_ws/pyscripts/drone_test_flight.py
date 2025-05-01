import numpy as np
from omni.isaac.kit import SimulationApp

# Initialize SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid, VisualCuboid, VisualSphere
from isaacsim.core.utils.viewports import set_camera_view  # Updated import
from isaacsim.core.utils.prims import get_prim_at_path  # Updated import
from omni.isaac.sensor import RotatingLidarPhysX
from pxr import UsdGeom, Gf
import carb
import rclpy
from sensor_msgs.msg import PointCloud2
from omni.isaac.ros2_bridge import Ros2Publisher  # Correct import for Isaac Sim 4.5

# Constants
DRONE_PRIM_PATH = "/World/Drone"
LIDAR_PRIM_PATH = f"{DRONE_PRIM_PATH}/rtx_lidar"
AREA_SIZE = 100.0  # meters
DRONE_ALTITUDE = 10.0  # meters
LIDAR_OFFSET = Gf.Vec3f(0.0, 0.0, -0.1)  # 10 cm below drone
LIDAR_ROTATION = Gf.Rotation(Gf.Vec3d(1, 0, 0), 90)  # Face downward

def create_environment(num_blocks=50, num_spheres=5):
    """Create the 100x100 m environment with blocks, spheres, and landing zone."""
    my_world = World(stage_units_in_meters=1.0)
    my_world.scene.add_default_ground_plane()

    # Define parameters
    area_size = 100.0  # meters
    min_spacing = 2.0
    max_spacing = 10.0
    min_block_size = 0.5
    max_block_size = 5.0

    # Calculate grid size for blocks
    grid_size = int(np.ceil(np.sqrt(num_blocks)))
    cell_size = area_size / grid_size

    # Add blocks
    block_positions = []
    for i in range(grid_size):
        for j in range(grid_size):
            if len(block_positions) >= num_blocks:
                break
            block_size = np.random.uniform(min_block_size, max_block_size, 3)
            spacing_x = np.random.uniform(min_spacing, max_spacing)
            spacing_y = np.random.uniform(min_spacing, max_spacing)
            x = (i + 0.5) * cell_size - area_size / 2 + spacing_x
            y = (j + 0.5) * cell_size - area_size / 2 + spacing_y
            z = block_size[2] / 2
            position = np.array([x, y, z])

            block = my_world.scene.add(
                DynamicCuboid(
                    prim_path=f"/World/Block_{len(block_positions)}",
                    name=f"block_{len(block_positions)}",
                    position=position,
                    scale=block_size,
                    size=1.0,
                    color=np.array([1.0, 0.0, 0.0])  # Red
                )
            )
            print(f"Added block_{len(block_positions)} at position: {position}, size: {block_size}")
            block_positions.append(position)

    # Add spheres
    for i in range(num_spheres):
        sphere = my_world.scene.add(
            VisualSphere(
                prim_path=f"/World/Sphere_{i}",
                name=f"sphere_{i}",
                position=np.array([area_size / 2 + i * 2.0, area_size / 2 + 2.0, 0.5]),
                radius=0.5,
                color=np.array([0.0, 1.0, 0.0])  # Green
            )
        )
        print(f"Added sphere_{i} at position: {sphere.get_world_pose()[0]}")

    # Add landing zone
    landing_zone = my_world.scene.add(
        VisualCuboid(
            prim_path="/World/LandingZone",
            name="landing_zone",
            position=np.array([0.0, area_size / 2 + 5.0, 0.05]),
            scale=np.array([5.0, 5.0, 0.1]),
            size=1.0,
            color=np.array([1.0, 1.0, 1.0])  # White
        )
    )
    print(f"Added landing_zone at position: {landing_zone.get_world_pose()[0]}")

    # Set camera
    set_camera_view(
        eye=np.array([0.0, 0.0, 50.0]),
        target=np.array([0.0, 0.0, 0.0]),
        camera_prim_path="/OmniverseKit_Persp"
    )

    my_world.reset()
    return my_world

def create_drone():
    """Create a pink placeholder drone (VisualCuboid)."""
    my_world = World(stage_units_in_meters=1.0)
    drone = my_world.scene.add(
        VisualCuboid(
            prim_path=DRONE_PRIM_PATH,
            name="drone",
            position=np.array([0.0, 0.0, DRONE_ALTITUDE]),
            scale=np.array([0.5, 0.5, 0.2]),
            size=1.0,
            color=np.array([1.0, 0.0, 1.0])  # Pink
        )
    )
    carb.log_info(f"Created drone at {DRONE_PRIM_PATH}")
    return drone

def configure_rtx_lidar():
    """Configure the RTX LiDAR with 360° HFOV, 45° VFOV, ~300k points/sec, facing downward."""
    stage = omni.usd.get_context().get_stage()
    if not get_prim_at_path(LIDAR_PRIM_PATH):
        stage.DefinePrim(LIDAR_PRIM_PATH, "Xform")

    lidar_prim = stage.GetPrimAtPath(LIDAR_PRIM_PATH)
    if not lidar_prim:
        carb.log_error(f"Failed to create LiDAR prim at {LIDAR_PRIM_PATH}")
        return None

    # Configure LiDAR
    lidar = RotatingLidarPhysX(LIDAR_PRIM_PATH)
    lidar.set_resolution(0.5)  # 0.5° resolution (~720 points per rotation)
    lidar.set_horizontal_fov(360.0)
    lidar.set_vertical_fov(45.0)
    lidar.set_min_range(0.1)
    lidar.set_max_range(100.0)
    lidar.set_rotation_rate(20.0)  # 20 Hz for ~300k points/sec
    lidar.enable_semantics(True)

    # Set transform (downward-facing)
    xform = UsdGeom.Xformable(lidar_prim)
    xform.ClearXformOpOrder()
    translate_op = xform.AddTranslateOp()
    rotate_op = xform.AddRotateXYZOp()
    translate_op.Set(LIDAR_OFFSET)
    rotate_op.Set(Gf.Vec3f(90.0, 0.0, 0.0))  # 90° around X

    # Configure ROS2 publisher
    publisher = Ros2Publisher(
        prim_path=LIDAR_PRIM_PATH,
        topic_name="/pointcloud",
        message_type=PointCloud2
    )
    lidar.add_point_cloud_data_to_publish()
    carb.log_info(f"ROS2 point cloud publisher set up on topic /pointcloud")

    return lidar

def generate_lawnmower_waypoints():
    """Generate waypoints for a lawnmower pattern over the 100x100 m area."""
    step_size = 5.0  # Distance between parallel paths
    waypoints = []
    y = -AREA_SIZE / 2
    while y <= AREA_SIZE / 2:
        waypoints.append([AREA_SIZE / 2, y, DRONE_ALTITUDE])
        waypoints.append([-AREA_SIZE / 2, y, DRONE_ALTITUDE])
        y += step_size
        if y <= AREA_SIZE / 2:
            waypoints.append([-AREA_SIZE / 2, y, DRONE_ALTITUDE])
            waypoints.append([AREA_SIZE / 2, y, DRONE_ALTITUDE])
            y += step_size
    return np.array(waypoints)

def move_drone_to_waypoint(drone, target_pos, speed=2.0, delta_time=0.016):
    """Move the drone toward the target waypoint with smooth interpolation."""
    current_pos = np.array(drone.get_world_pose()[0])
    direction = target_pos - current_pos
    distance = np.linalg.norm(direction)
    if distance < 0.1:  # Close enough to waypoint
        return True

    step = speed * delta_time
    if step > distance:
        step = distance
    new_pos = current_pos + (direction / distance) * step
    drone.set_world_pose(position=new_pos)
    return False

def main():
    """Main function to set up the environment, drone, LiDAR, and navigation."""
    # Initialize ROS2
    rclpy.init()
    carb.log_info("ROS2 initialized")

    # Create environment
    world = create_environment(num_blocks=50, num_spheres=5)

    # Create drone
    drone = create_drone()
    if not drone:
        carb.log_error("Failed to create drone")
        rclpy.shutdown()
        simulation_app.close()
        return

    # Configure LiDAR
    lidar = configure_rtx_lidar()
    if not lidar:
        carb.log_error("Failed to configure LiDAR")
        rclpy.shutdown()
        simulation_app.close()
        return

    # Generate waypoints
    waypoints = generate_lawnmower_waypoints()
    carb.log_info(f"Generated {len(waypoints)} waypoints")

    # Navigation loop
    waypoint_index = 0
    speed = 2.0  # m/s
    while simulation_app.is_running() and waypoint_index < len(waypoints):
        target_pos = waypoints[waypoint_index]
        reached = move_drone_to_waypoint(drone, target_pos, speed)
        if reached:
            waypoint_index += 1
            carb.log_info(f"Reached waypoint {waypoint_index}/{len(waypoints)}: {target_pos}")

        # Step the simulation
        world.step(render=True)

    # Cleanup
    carb.log_info("Simulation complete. Shutting down...")
    rclpy.shutdown()
    simulation_app.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        carb.log_info("Simulation terminated by user")
        rclpy.shutdown()
        simulation_app.close()
    except Exception as e:
        carb.log_error(f"Unexpected error: {e}")
        rclpy.shutdown()
        simulation_app.close()