from math import pi
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
#from tf_transformations import quaternion_from_euler

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import AnyLaunchDescriptionSource


from scipy.spatial.transform import Rotation as R


def generate_launch_description():

    # ==============================
    # Static TFs
    # ==============================

    # tftree (intended):
    # map -> map_ned -> base_link_frd -> altax_center_frd -> velodyne -> camera_body_frd -> gimbal_link


    # 1) base_link_frd → altax_center_frd
    # PX4 module center is 45 mm RIGHT of Alta-X center (FRD: +X fwd, +Y right, +Z down)
    # "45 mm LEFT → -Y", so we publish -0.095 on Y.
    px4_to_altax = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="px4_to_altax_center",
        output="screen",
        arguments=[
            "--frame-id", "base_link_frd",
            "--child-frame-id", "altax_center_frd",
            "--x", "0.0", "--y", "-0.095", "--z", "0.0",
            "--roll", "0", "--pitch", "0", "--yaw", "0",
        ],
    )

    # 2) altax_center_frd → velodyne
    # Forward 0.075 m, Right 0.24 m (FRD right is +Y, but need negative Y;
    # vx=0.075, vy=0.24 right, vz=0.075 down)
    deg2rad = pi / 180.0
    vx = 0.13
    vy = 0.24
    vz = 0.11
    roll = 0 * deg2rad
    pitch = -90 * deg2rad  # nose down
    yaw = 0 * deg2rad
    #qx, qy, qz, qw = quaternion_from_euler(roll, pitch, yaw) #expects RPY radian, returns normalized quat with magnitude 1
    qx, qy, qz, qw = R.from_euler("zxy", [yaw, roll, pitch]).as_quat()

    altax_to_velodyne = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="altax_to_velodyne",
        output="screen",
        arguments=[
            "--frame-id", "altax_center_frd",
            "--child-frame-id", "velodyne",
            "--x", f"{vx:.3f}", "--y", f"{vy:.3f}", "--z", f"{vz:.3f}",
            "--qx", f"{qx:.6f}", "--qy", f"{qy:.6f}",
            "--qz", f"{qz:.6f}", "--qw", f"{qw:.6f}",
        ],
    )

    # 3) altax_center_frd → camera_body_frd (20 cm down)
    altax_to_camera_body = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="altax_to_camera_body",
        output="screen",
        arguments=[
            "--frame-id", "altax_center_frd",
            "--child-frame-id", "camera_body_frd",
            "--x", "0.0", "--y", "0.0", "--z", "0.20",
            "--roll", "0", "--pitch", "0", "--yaw", "0",
        ],
    )

    # 4) camera_body_frd → gimbal_link
    camera_body_to_gimbal = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="camera_body_to_gimbal",
        output="screen",
        arguments=[
            "--frame-id", "camera_body_frd",
            "--child-frame-id", "gimbal_link",
            "--x", "0", "--y", "0", "--z", "0",
            "--roll", "0", "--pitch", "0", "--yaw", "0",
        ],
    )
    # 5) test
    deg2rad = pi / 180.0
    vx = 0.13
    vy = 0.24
    vz = 0.11
    roll = 0 * deg2rad
    pitch = -90 * deg2rad  # nose down
    yaw = 0 * deg2rad
    #qx, qy, qz, qw = quaternion_from_euler(roll, pitch, yaw) #expects RPY radian, returns normalized quat with magnitude 1
    # qx, qy, qz, qw = R.from_euler("zxy", [yaw, roll, pitch]).as_quat()
    qx, qy, qz, qw = R.from_euler("xyz", [roll, pitch, yaw]).as_quat()

    map_ned_to_velodyne = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="map_ned_to_velodyne",
        output="screen",
        arguments=[
            "--frame-id", "map_ned",
            "--child-frame-id", "velodyne",
            "--x", f"{vx:.3f}", "--y", f"{vy:.3f}", "--z", f"{vz:.3f}",
            "--qx", f"{qx:.6f}", "--qy", f"{qy:.6f}",
            "--qz", f"{qz:.6f}", "--qw", f"{qw:.6f}",
        ],
    )

    return LaunchDescription([  
                                # px4_to_altax,
                                # altax_to_velodyne,
                                # altax_to_camera_body,
                                # camera_body_to_gimbal,
                                map_ned_to_velodyne
    ])
