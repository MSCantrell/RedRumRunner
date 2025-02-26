"""
Example code to test the hex grid implementation with keyboard-only controls.
Creates a small grid and renders it to the screen.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tcod import libtcodpy
from tcod.context import new_terminal
from tcod.console import Console
import tcod.event as event

from src.engine.hex_grid import HexCoord, HexGrid, HexOrientation, HexCell
from src.engine.hex_renderer import HexRenderer
from src.config import Config

# Keyboard constants
K_ESCAPE = 27  # ASCII for ESC
K_UP = 1073741906  # Common value for UP arrow
K_DOWN = 1073741905  # Common value for DOWN arrow
K_LEFT = 1073741904  # Common value for LEFT arrow
K_RIGHT = 1073741903  # Common value for RIGHT arrow
K_p = 112  # ASCII for 'p'
K_TAB = 9  # Tab key for switching modes

def run_hex_grid_test():
    """Run a test of the hex grid implementation."""
    # Set up the font
    libtcodpy.console_set_custom_font(
        Config.FONT_PATH,
        Config.FONT_FLAGS
    )
    
    # Create a context (window) using the newer API
    context = new_terminal(
        Config.SCREEN_WIDTH,
        Config.SCREEN_HEIGHT,
        title=Config.WINDOW_TITLE,
        vsync=True
    )
    
    # Create main console for rendering
    console = Console(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
    
    # Create a hex grid
    grid = HexGrid(
        orientation=HexOrientation.POINTY_TOP,
        hex_size=20.0,
        origin=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2)
    )
    
    # Create a hexagonal pattern
    grid.create_hexagon(5)
    
    # Add some different terrain types
    for q in range(-2, 3):
        coord = HexCoord.from_axial(q, -q)
        cell = HexCell(terrain_type="river", movement_cost=2.0)
        grid.set_cell(coord, cell)
    
    for q in range(-4, -1):
        for r in range(2, 5):
            if q + r <= 4:
                coord = HexCoord.from_axial(q, r)
                cell = HexCell(terrain_type="mountain", movement_cost=3.0, blocks_sight=True)
                grid.set_cell(coord, cell)
    
    for q in range(1, 4):
        for r in range(-4, -1):
            if -q - r <= 4:
                coord = HexCoord.from_axial(q, r)
                cell = HexCell(terrain_type="forest", movement_cost=1.5)
                grid.set_cell(coord, cell)
    
    # Add a port
    port_coord = HexCoord.from_axial(3, -1)
    port_cell = HexCell(terrain_type="port", movement_cost=1.0, metadata={"name": "Port Royal"})
    grid.set_cell(port_coord, port_cell)
    
    # Get a list of all coordinates in the grid for cursor navigation
    all_coords = grid.get_all_coords()
    all_coords.sort(key=lambda c: (c.z, c.x))  # Sort for consistent navigation
    
    # Initialize cursor at center
    cursor_index = 0
    if all_coords:
        for i, coord in enumerate(all_coords):
            if coord.x == 0 and coord.y == 0 and coord.z == 0:
                cursor_index = i
                break
    
    # Create the renderer
    renderer = HexRenderer(grid)
    
    # Set up navigation modes
    CAMERA_MODE = 0
    CURSOR_MODE = 1
    current_mode = CAMERA_MODE
    
    # Camera position
    camera_offset = [0, 0]
    camera_speed = 10
    
    # Main loop
    running = True
    while running:
        # Clear the console
        console.clear()
        
        # Update the selected hex for rendering
        if all_coords:
            selected_coord = all_coords[cursor_index]
            renderer.set_selected_hex(selected_coord)
        
        # Render the grid
        renderer.render(console, camera_offset)
        
        # Draw instructions
        console.print(
            2, 1,
            f"MODE: {'CAMERA' if current_mode == CAMERA_MODE else 'CURSOR'}",
            fg=(255, 255, 0)
        )
        console.print(
            2, 2,
            "TAB: Switch between Camera/Cursor mode",
            fg=(255, 255, 255)
        )
        console.print(
            2, 3,
            "Arrow keys: Move camera or cursor (based on mode)",
            fg=(255, 255, 255)
        )
        console.print(
            2, 4,
            "P: Test pathfinding from cursor to port",
            fg=(255, 255, 255)
        )
        console.print(
            2, 5,
            "ESC: Quit",
            fg=(255, 255, 255)
        )
        
        # Draw selected hex info
        cell = grid.get_cell(selected_coord) if all_coords else None
        if cell:
            console.print(
                2, 7,
                f"Selected: {selected_coord}",
                fg=(255, 255, 0)
            )
            console.print(
                2, 8,
                f"Terrain: {cell.terrain_type}",
                fg=(255, 255, 0)
            )
            console.print(
                2, 9,
                f"Movement Cost: {cell.movement_cost}",
                fg=(255, 255, 0)
            )
        
        # Present the console to the screen
        context.present(console)
        
        # Process events
        for evt in event.wait():
            # Check for window close
            if isinstance(evt, event.Quit):
                running = False
                break
            
            # Handle keyboard events
            elif isinstance(evt, event.KeyDown):
                # Toggle between camera and cursor mode
                if evt.sym == K_TAB:
                    current_mode = CURSOR_MODE if current_mode == CAMERA_MODE else CAMERA_MODE
                    console.print(
                        Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2,
                        f"Switched to {('CAMERA' if current_mode == CAMERA_MODE else 'CURSOR')} mode",
                        fg=(255, 255, 0),
                        alignment=libtcodpy.CENTER
                    )
                    context.present(console)
                
                # ESC to quit
                elif evt.sym == K_ESCAPE:
                    running = False
                    break
                
                # Arrow keys - behavior depends on mode
                elif evt.sym in (K_UP, K_DOWN, K_LEFT, K_RIGHT):
                    if current_mode == CAMERA_MODE:
                        # Camera mode - move the view
                        if evt.sym == K_UP:
                            camera_offset[1] -= camera_speed
                        elif evt.sym == K_DOWN:
                            camera_offset[1] += camera_speed
                        elif evt.sym == K_LEFT:
                            camera_offset[0] -= camera_speed
                        elif evt.sym == K_RIGHT:
                            camera_offset[0] += camera_speed
                    else:
                        # Cursor mode - move the cursor
                        if not all_coords:
                            continue
                            
                        old_coord = all_coords[cursor_index]
                        
                        # Try to find the nearest hex in the desired direction
                        if evt.sym == K_UP:
                            # Move cursor north
                            target_coords = [
                                c for c in all_coords 
                                if c.z < old_coord.z and abs(c.x - old_coord.x) <= 1
                            ]
                        elif evt.sym == K_DOWN:
                            # Move cursor south
                            target_coords = [
                                c for c in all_coords 
                                if c.z > old_coord.z and abs(c.x - old_coord.x) <= 1
                            ]
                        elif evt.sym == K_LEFT:
                            # Move cursor west
                            target_coords = [
                                c for c in all_coords 
                                if c.x < old_coord.x and abs(c.z - old_coord.z) <= 1
                            ]
                        elif evt.sym == K_RIGHT:
                            # Move cursor east
                            target_coords = [
                                c for c in all_coords 
                                if c.x > old_coord.x and abs(c.z - old_coord.z) <= 1
                            ]
                        
                        # Find the nearest matching hex
                        if target_coords:
                            target_coords.sort(key=lambda c: old_coord.distance(c))
                            new_coord = target_coords[0]
                            # Find the index of the new coordinate
                            for i, coord in enumerate(all_coords):
                                if coord == new_coord:
                                    cursor_index = i
                                    break
                
                # Test pathfinding from cursor to port
                elif evt.sym == K_p or evt.sym == ord('p'):
                    if all_coords:
                        start = all_coords[cursor_index]
                        goal = HexCoord.from_axial(3, -1)  # Port Royal
                        path = grid.find_path(start, goal)
                        print(f"Path from {start} to {goal}:")
                        for coord in path:
                            print(f"  {coord}")
                        
                        # Highlight the path temporarily
                        for coord in path:
                            if coord != start and coord != goal:
                                # Create a visual path indicator
                                console.print(
                                    int(coord.to_pixel(grid.orientation, grid.hex_size, 
                                                       (grid.origin[0] - camera_offset[0], 
                                                        grid.origin[1] - camera_offset[1]))[0]),
                                    int(coord.to_pixel(grid.orientation, grid.hex_size, 
                                                       (grid.origin[0] - camera_offset[0], 
                                                        grid.origin[1] - camera_offset[1]))[1]),
                                    "*",
                                    fg=(255, 0, 0),
                                    bg=None
                                )
                        context.present(console)
                        # Wait for key press to continue
                        waiting = True
                        while waiting:
                            for wait_evt in event.wait():
                                if isinstance(wait_evt, event.KeyDown):
                                    waiting = False
                                    break

if __name__ == "__main__":
    run_hex_grid_test()