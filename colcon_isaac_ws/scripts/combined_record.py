from math import sin, cos, pi
from launch import LaunchDescription
from launch_ros.actions import Node

# tftree (intended):
# map -> map_ned -> base_link_frd -> altax_center_frd -> rtxlidar -> camera_body_frd -> gimbal_link

def generate_launch_description():
    deg2rad = pi / 180.0

    # ==============================
    # Static TFs
    # ==============================

    # 1) base_link_frd → altax_center_frd
    # PX4 module center is 45 mm RIGHT of Alta-X center (FRD: +X fwd, +Y right, +Z down)
    # Your comment says "45 mm LEFT → -Y", so we publish -0.095 on Y.
    px4_to_altax = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="px4_to_altax_center",
        output="screen",
        arguments=[
            "--frame-id", "drone_base_link_frd",
            "--child-frame-id", "altax_center_frd",
            "--x", "0.0", "--y", "-0.095", "--z", "0.0",
            "--roll", "0", "--pitch", "0", "--yaw", "0",
        ],
    )

    # 2) altax_center_frd → rtxlidar
    # Forward 0.075 m, Right 0.24 m (FRD right is +Y, but your previous comment used negative Y;
    # keeping your numeric intent exactly: vx=0.075, vy=0.24 right, vz=0.075 down)
    vx = 0.075
    vy = 0.24
    vz = 0.075
    pitch = -20.0 * deg2rad  # nose down
    # pitch = -20.0 * deg2rad  # nose down

    qx = 0.0
    qy = sin(pitch / 2.0)  # rotation about Y
    qz = 0.0
    qw = cos(pitch / 2.0)

    altax_to_rtxlidar = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="altax_to_rtxlidar",
        output="screen",
        arguments=[
            "--frame-id", "altax_center_frd",
            "--child-frame-id", "rtxlidar",
            "--x", f"{vx:.3f}", "--y", f"{vy:.3f}", "--z", f"{vz:.3f}",
            "--qx", f"{qx:.6f}", "--qy", f"{qy:.6f}",
            "--qz", f"{qz:.6f}", "--qw", f"{qw:.6f}",
        ],
    )

    # 3) altax_center_frd → camera_body_frd (20 cm down)
    altax_to_camera_body = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="altax_to_camera",
        output="screen",
        arguments=[
            "--frame-id", "altax_center_frd",
            "--child-frame-id", "camera",
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

    vision = Node(
        package="gesture_recognition_pkg",
        executable="recorder",
        name="vision",
        output="screen",
    )

    vio_control = Node(
        package="vio_control_pkg",
        executable="vio_control",
        name="Gremsy_VIO",
        output="screen",
    )

    return LaunchDescription([
        px4_to_altax,
        altax_to_rtxlidar,
        altax_to_camera_body,
        #camera_body_to_gimbal,
        # vision,
        # vio_control,
    ])
