import numpy as np
from omni.isaac.kit import SimulationApp

# Initialize SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid, VisualCuboid, VisualSphere
from omni.isaac.core.utils.viewports import set_camera_view

def create_environment(num_blocks=50, num_spheres=5):
    # Create a World instance
    my_world = World(stage_units_in_meters=1.0)

    # Add ground plane
    my_world.scene.add_default_ground_plane()

    # Define 100x100 m area
    area_size = 100.0  # meters
    min_spacing = 2.0  # meters
    max_spacing = 10.0  # meters
    min_block_size = 0.5  # meters
    max_block_size = 5.0  # meters

    # Calculate grid size for blocks (approximate to cover 100x100 m)
    grid_size = int(np.ceil(np.sqrt(num_blocks)))  # Square grid
    cell_size = area_size / grid_size  # Base cell size for placement

    # Add blocks (DynamicCuboid) with random sizes and spacing
    block_positions = []
    for i in range(grid_size):
        for j in range(grid_size):
            if len(block_positions) >= num_blocks:
                break
            # Random size for each block
            block_size = np.random.uniform(min_block_size, max_block_size, 3)
            # Random spacing adjustment within cell
            spacing_x = np.random.uniform(min_spacing, max_spacing)
            spacing_y = np.random.uniform(min_spacing, max_spacing)
            # Position in grid with offset to center in 100x100 m
            x = -area_size / 2 + (i + 0.5) * cell_size + spacing_x - area_size / 2
            y = -area_size / 2 + (j + 0.5) * cell_size + spacing_y - area_size / 2
            z = block_size[2] / 2  # Place bottom on ground
            position = np.array([x, y, z])

            # Add block
            block = my_world.scene.add(
                DynamicCuboid(
                    prim_path=f"/World/Block_{len(block_positions)}",
                    name=f"block_{len(block_positions)}",
                    position=position,
                    scale=block_size,  # Varying size
                    size=1.0,
                    color=np.array([1.0, 0.0, 0.0])  # Red
                )
            )
            print(f"Added block_{len(block_positions)} at position: {position}, size: {block_size}")
            block_positions.append(position)

    # Add spheres (VisualSphere) outside block area
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

    # Add landing zone (VisualCuboid) outside block area
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

    # Set camera to view the entire 100x100 m area
    set_camera_view(
        eye=np.array([0.0, 0.0, 50.0]),  # High above center
        target=np.array([0.0, 0.0, 0.0]),  # Look at center
        camera_prim_path="/OmniverseKit_Persp"
    )

    # Reset the world to initialize physics
    my_world.reset()

    return my_world

if __name__ == "__main__":
    # Create environment
    print("Creating environment with 100x100 m block area")
    world = create_environment(num_blocks=50, num_spheres=5)

    # Keep the simulation running and rendering
    print("Environment setup complete. Keeping simulation app open...")
    while simulation_app.is_running():
        world.step(render=True)