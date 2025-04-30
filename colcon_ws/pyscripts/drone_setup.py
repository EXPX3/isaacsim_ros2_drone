import numpy as np
import json
from omni.isaac.core import World
from omni.isaac.core.objects import VisualSphere
from omni.isaac.sensor import RotatingLidarPhysX
from omni.isaac.core.utils.rotations import euler_angles_to_quat
from omni.isaac.core.utils.stage import get_current_stage
from omni.isaac.core.utils.viewports import set_camera_view
from pxr import Usd
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import rclpy
from rclpy.node import Node

# Global flag for rclpy initialization
RCLPY_INITIALIZED = False

class LidarPublisher(Node):
    def __init__(self):
        super().__init__('lidar_publisher')
        self.publisher_ = self.create_publisher(PointCloud2, '/lidar', 10)

    def publish_point_cloud(self, points):
        header = Header()
        header.frame_id = "lidar_frame"
        header.stamp = self.get_clock().now().to_msg()

        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1)
        ]

        point_cloud_msg = PointCloud2()
        point_cloud_msg.header = header
        point_cloud_msg.height = 1
        point_cloud_msg.width = points.shape[0]
        point_cloud_msg.fields = fields
        point_cloud_msg.is_bigendian = False
        point_cloud_msg.point_step = 16  # 4 floats * 4 bytes
        point_cloud_msg.row_step = point_cloud_msg.point_step * point_cloud_msg.width
        point_cloud_msg.is_dense = True
        if points.shape[1] == 3:
            points = np.hstack((points, np.ones((points.shape[0], 1))))
        point_cloud_msg.data = points.astype(np.float32).tobytes()

        self.publisher_.publish(point_cloud_msg)

def add_drone_with_lidar(world, lidar_profile_path):
    global RCLPY_INITIALIZED
    lidar_publisher = LidarPublisher()

    with open(lidar_profile_path, 'r') as f:
        lidar_profile = json.load(f)

    drone = world.scene.add(
        VisualSphere(
            prim_path="/World/Drone",
            name="drone_sphere",
            position=np.array([-50.0, -50.0, 2.0]),
            radius=4.0,
            color=np.array([1.0, 0.0, 1.0])  # Pink (magenta)
        )
    )
    print(f"Added drone (pink sphere) at position: {drone.get_world_pose()[0]}")

    lidar = world.scene.add(
        RotatingLidarPhysX(
            prim_path="/World/Drone/Lidar",
            name="lidar",
            position=np.array([0.0, 0.0, -0.2]),
            orientation=euler_angles_to_quat([np.pi, 0, 0])
        )
    )
    lidar.load_lidar_profile(lidar_profile)
    print(f"Added LIDAR at position: {lidar.get_world_pose()[0]}")

    stage = get_current_stage()
    lidar_prim = stage.GetPrimAtPath("/World/Drone/Lidar")
    if lidar_prim.HasAttribute("visualizationEnabled"):
        lidar_prim.GetAttribute("visualizationEnabled").Set(True)
    else:
        print("Warning: visualizationEnabled attribute not found")
    if lidar_prim.HasAttribute("pointSize"):
        lidar_prim.GetAttribute("pointSize").Set(0.05)
    else:
        print("Warning: pointSize attribute not found")

    def lidar_callback(data):
        points = data.get("point_cloud", None)
        if points is not None:
            lidar_publisher.publish_point_cloud(points)

    lidar.add_data_callbacks({"point_cloud": lidar_callback})

    return drone, lidar, lidar_publisher

def generate_lawnmower_path(area_size=100.0, step_size=10.0, height=2.0):
    path = []
    x, y = -area_size / 2, -area_size / 2
    direction = 1
    while y <= area_size / 2:
        path.append([x, y, height])
        x += direction * area_size
        path.append([x, y, height])
        y += step_size
        if y <= area_size / 2:
            path.append([x, y, height])
            x -= direction * area_size
            path.append([x, y, height])
            y += step_size
            direction *= -1
    return np.array(path)

def move_drone(drone, waypoints, world, speed=2.0):
    current_waypoint = 0
    def step_callback(step):
        nonlocal current_waypoint
        if current_waypoint >= len(waypoints):
            return
        target = waypoints[current_waypoint]
        current_pos = drone.get_world_pose()[0]
        direction = target - current_pos
        distance = np.linalg.norm(direction)
        if distance < 0.5:
            current_waypoint += 1
            print(f"Reached waypoint {current_waypoint}: {target}")
            return
        drone.set_world_pose(position=target)
    world.add_physics_callback("drone_move", step_callback)
    return current_waypoint

def setup_drone(world, lidar_profile_path):
    drone, lidar, lidar_publisher = add_drone_with_lidar(world, lidar_profile_path)
    waypoints = generate_lawnmower_path(area_size=100.0, step_size=10.0, height=2.0)
    print(f"Generated {len(waypoints)} waypoints: {waypoints[:5]}...")
    move_drone(drone, waypoints, world)
    set_camera_view(
        eye=np.array([-50.0, -50.0, 5.0]),
        target=np.array([-50.0, -50.0, 0.0]),
        camera_prim_path="/OmniverseKit_Persp"
    )
    return drone, lidar, lidar_publisher

if __name__ == "__main__":
    global RCLPY_INITIALIZED
    if not RCLPY_INITIALIZED:
        rclpy.init()
        RCLPY_INITIALIZED = True
    world = World(stage_units_in_meters=1.0)
    lidar_profile_path = "/root/colcon_ws/pyscripts/lidar_vfov45_hfvov360.json"
    drone, lidar, lidar_publisher = setup_drone(world, lidar_profile_path)
    print("Drone setup complete. Running simulation...")
    while True:
        world.step(render=True)
        rclpy.spin_once(lidar_publisher, timeout_sec=0.0)