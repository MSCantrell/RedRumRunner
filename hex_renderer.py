"""
Renderer for hexagonal grids in RedRumRunner.
Handles converting between hex coordinates and screen coordinates for rendering.
"""
import math
from typing import Dict, Tuple, List

from tcod.console import Console
import numpy as np

from src.engine.hex_grid import HexCoord, HexGrid, HexOrientation, HexCell


class HexRenderer:
    """
    Renders a hexagonal grid to a tcod console.
    Supports different grid orientations and styles.
    """
    
    def __init__(self, grid: HexGrid):
        """
        Initialize the hex renderer.
        
        Args:
            grid: The HexGrid to render
        """
        self.grid = grid
        self.selected_hex = None
        
        # Terrain colors: (foreground, background)
        self.terrain_colors = {
            "ocean": ((100, 100, 255), (0, 0, 100)),
            "land": ((100, 255, 100), (0, 100, 0)),
            "mountain": ((255, 255, 255), (100, 100, 100)),
            "forest": ((0, 180, 0), (0, 100, 0)),
            "desert": ((255, 255, 150), (180, 180, 0)),
            "river": ((150, 150, 255), (0, 0, 180)),
            "reef": ((0, 255, 255), (0, 100, 100)),
            "port": ((255, 150, 0), (100, 50, 0))
        }
        
        # Default to blue for any undefined terrain types
        self.default_colors = ((150, 150, 255), (0, 0, 100))
    
    def set_selected_hex(self, coord: HexCoord) -> None:
        """
        Set the currently selected hex.
        
        Args:
            coord: The coordinates of the selected hex, or None to clear selection
        """
        self.selected_hex = coord
    
    def get_hex_at_pixel(self, x: int, y: int) -> HexCoord:
        """
        Get the hex coordinates at the given pixel coordinates.
        
        Args:
            x: Pixel x-coordinate
            y: Pixel y-coordinate
            
        Returns:
            The HexCoord at the pixel location
        """
        return HexCoord.from_pixel(
            x, y, 
            self.grid.orientation, 
            self.grid.hex_size, 
            self.grid.origin
        )
    
    def render(self, console: Console, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """
        Render the hex grid to the console.
        
        Args:
            console: The tcod Console to render to
            camera_offset: Offset for camera position (x, y)
        """
        # Adjust the grid origin for camera position
        adjusted_origin = (
            self.grid.origin[0] - camera_offset[0],
            self.grid.origin[1] - camera_offset[1]
        )
        
        # Calculate the visible area in hex coordinates
        # This is an approximation that ensures we render all visible hexes
        top_left = HexCoord.from_pixel(
            0, 0, 
            self.grid.orientation, 
            self.grid.hex_size, 
            adjusted_origin
        )
        bottom_right = HexCoord.from_pixel(
            console.width, console.height, 
            self.grid.orientation, 
            self.grid.hex_size, 
            adjusted_origin
        )
        
        # Add a buffer to ensure we render hexes that might be partially visible
        buffer = 2
        visible_area = []
        
        for x in range(top_left.x - buffer, bottom_right.x + buffer + 1):
            for y in range(top_left.y - buffer, bottom_right.y + buffer + 1):
                for z in range(top_left.z - buffer, bottom_right.z + buffer + 1):
                    # Skip invalid cube coordinates
                    if x + y + z != 0:
                        continue
                    
                    coord = HexCoord(x, y, z)
                    visible_area.append(coord)
        
        # Render all visible hexes
        for coord in visible_area:
            cell = self.grid.get_cell(coord)
            if cell:
                self._render_hex(console, coord, cell, adjusted_origin)
        
        # Render the selected hex highlight
        if self.selected_hex and self.grid.get_cell(self.selected_hex):
            self._render_hex_outline(
                console, 
                self.selected_hex, 
                (255, 255, 0),  # Yellow highlight
                adjusted_origin
            )
    
    def _render_hex(self, console: Console, coord: HexCoord, 
                   cell: HexCell, origin: Tuple[float, float]) -> None:
        """
        Render a single hex to the console.
        
        Args:
            console: The tcod Console to render to
            coord: The hex coordinates
            cell: The hex cell data
            origin: Adjusted origin for camera position
        """
        # Get hex center in pixel coordinates
        center = coord.to_pixel(
            self.grid.orientation, 
            self.grid.hex_size, 
            origin
        )
        
        # Get corners in pixel coordinates
        corners = coord.get_all_corners_pixel(
            self.grid.orientation, 
            self.grid.hex_size, 
            origin
        )
        
        # Check if the hex is on screen
        if (0 <= center[0] < console.width and 
            0 <= center[1] < console.height):
            
            # Get colors for this terrain type
            colors = self.terrain_colors.get(
                cell.terrain_type, 
                self.default_colors
            )
            
            # Convert center to integer coordinates
            center_x, center_y = int(center[0]), int(center[1])
            
            # Draw basic character and background for the hex
            bg_color = colors[1]
            fg_color = colors[0]
            
            # Set the background color for this cell
            if 0 <= center_x < console.width and 0 <= center_y < console.height:
                console.bg[center_y, center_x] = bg_color
                console.fg[center_y, center_x] = fg_color
                
                # Print a character representing the terrain
                terrain_chars = {
                    "ocean": '~',
                    "land": '.',
                    "mountain": '^',
                    "forest": 'f',
                    "desert": 'd',
                    "river": '~',
                    "reef": '*',
                    "port": 'P'
                }
                char = terrain_chars.get(cell.terrain_type, '.')
                console.print(center_x, center_y, char, fg=fg_color, bg=bg_color)
            
            # Draw the hex outline
            self._render_hex_outline(console, coord, fg_color, origin)
            
            # Draw coordinate text in the center
            text = f"{coord.x},{coord.z}"
            console.print(
                center_x, center_y,
                text,
                fg=fg_color,
                bg=bg_color
            )
    
    def _render_hex_outline(self, console: Console, coord: HexCoord, 
                           color: Tuple[int, int, int], 
                           origin: Tuple[float, float]) -> None:
        """
        Render the outline of a hex.
        
        Args:
            console: The tcod Console to render to
            coord: The hex coordinates
            color: RGB color tuple for the outline
            origin: Adjusted origin for camera position
        """
        corners = coord.get_all_corners_pixel(
            self.grid.orientation, 
            self.grid.hex_size, 
            origin
        )
        
        # Convert to integer coordinates
        int_corners = [(int(x), int(y)) for x, y in corners]
        
        # Draw the outline by connecting each corner to the next
        for i in range(len(int_corners)):
            j = (i + 1) % len(int_corners)
            self._draw_line(console, 
                         int_corners[i][0], int_corners[i][1],
                         int_corners[j][0], int_corners[j][1],
                         color)
    
    def _draw_line(self, console: Console, x1: int, y1: int, x2: int, y2: int, color: Tuple[int, int, int]) -> None:
        """
        Draw a line between two points.
        Using Bresenham's line algorithm.
        
        Args:
            console: The console to draw on
            x1, y1: Starting point coordinates
            x2, y2: Ending point coordinates
            color: RGB color tuple
        """
        # Bresenham's line algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            # Draw the point if it's within the console bounds
            if 0 <= x1 < console.width and 0 <= y1 < console.height:
                console.fg[y1, x1] = color
                console.ch[y1, x1] = ord('.')  # Using a simple ASCII dot for the line
            
            if x1 == x2 and y1 == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy