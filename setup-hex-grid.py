#!/usr/bin/env python3
"""
Setup script for RedRumRunner hex grid system.
This script creates the project structure and files needed to run the hex grid test.
"""
import os
import sys
import urllib.request
import shutil
import subprocess
import textwrap

# Ensure we're using Python 3.6+
if sys.version_info < (3, 6):
    print("This script requires Python 3.6 or newer.")
    sys.exit(1)

# Check for dependencies
try:
    import tcod
    import numpy
except ImportError:
    print("Installing required dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "tcod", "numpy"])
    try:
        import tcod
        import numpy
        print("Dependencies installed successfully.")
    except ImportError:
        print("Failed to install dependencies. Please install them manually:")
        print("pip install tcod numpy")
        sys.exit(1)

# Project structure
PROJECT_ROOT = "redrum_runner"
DIRECTORIES = [
    "",
    "assets",
    "assets/fonts",
    "data",
    "docs",
    "src",
    "src/engine",
    "src/game",
    "src/examples"
]

# Font URL
FONT_URL = "https://raw.githubusercontent.com/libtcod/python-tcod/master/fonts/dejavu10x10_gs_tc.png"
FONT_PATH = os.path.join(PROJECT_ROOT, "assets/fonts/dejavu10x10_gs_tc.png")

def create_directories():
    """Create the project directory structure."""
    print("Creating project directories...")
    for directory in DIRECTORIES:
        path = os.path.join(PROJECT_ROOT, directory)
        os.makedirs(path, exist_ok=True)

def download_font():
    """Download the tcod font file."""
    print("Downloading font file...")
    try:
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        print(f"Font downloaded to {FONT_PATH}")
    except Exception as e:
        print(f"Failed to download font: {e}")
        print("You'll need to provide your own tcod-compatible font.")

def create_init_files():
    """Create __init__.py files in Python package directories."""
    init_dirs = ["src", "src/engine", "src/game", "src/examples"]
    for directory in init_dirs:
        path = os.path.join(PROJECT_ROOT, directory, "__init__.py")
        with open(path, "w") as f:
            f.write('"""RedRumRunner package."""\n')

def write_file(path, content):
    """Write content to a file."""
    with open(path, "w") as f:
        f.write(content)

def create_config_file():
    """Create the config.py file."""
    path = os.path.join(PROJECT_ROOT, "src/config.py")
    content = '''"""
Configuration settings for RedRumRunner.
Centralizes game parameters and settings.
"""
from tcod import libtcodpy

class Config:
    """Configuration class holding game parameters."""
    # Display settings
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 50
    WINDOW_TITLE = "RedRumRunner - Hex Grid Test"
    FULLSCREEN = False
    
    # Font settings
    FONT_PATH = "assets/fonts/dejavu10x10_gs_tc.png"
    FONT_FLAGS = libtcodpy.FONT_TYPE_GREYSCALE | libtcodpy.FONT_LAYOUT_TCOD
    
    # Game settings
    TURN_BASED = True
    
    # Debug settings
    DEBUG_MODE = True
    SHOW_FPS = True
'''
    write_file(path, content)

def create_hex_grid_file():
    """Create the hex_grid.py file."""
    path = os.path.join(PROJECT_ROOT, "src/engine/hex_grid.py")
    content = '''"""
Hexagonal grid system for RedRumRunner.
Handles hex coordinates, grid management, and related calculations.
Based on the excellent reference at https://www.redblobgames.com/grids/hexagons/
"""
import math
import json
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Set, Optional, Any, Generator


class HexOrientation(Enum):
    """Orientation of hexagons in the grid."""
    POINTY_TOP = 0  # Pointy top (flat sides on left and right)
    FLAT_TOP = 1    # Flat top (pointy sides on left and right)


@dataclass
class LayoutConstants:
    """Constants for converting between hex and pixel coordinates."""
    f0: float
    f1: float
    f2: float
    f3: float
    b0: float
    b1: float
    b2: float
    b3: float
    start_angle: float  # in radians


# Constants for the two orientations
POINTY_TOP = LayoutConstants(
    f0=math.sqrt(3.0), f1=math.sqrt(3.0) / 2.0, f2=0.0, f3=3.0 / 2.0,
    b0=math.sqrt(3.0) / 3.0, b1=-1.0 / 3.0, b2=0.0, b3=2.0 / 3.0,
    start_angle=0.5
)

FLAT_TOP = LayoutConstants(
    f0=3.0 / 2.0, f1=0.0, f2=math.sqrt(3.0) / 2.0, f3=math.sqrt(3.0),
    b0=2.0 / 3.0, b1=0.0, b2=-1.0 / 3.0, b3=math.sqrt(3.0) / 3.0,
    start_angle=0.0
)


class HexCoord:
    """
    Represents a hex grid coordinate using cube coordinates (x, y, z).
    Provides methods for coordinate conversions, distance calculations, and more.
    """
    
    def __init__(self, x: int, y: int, z: int = None):
        """
        Initialize a hex coordinate with cube coordinates (x, y, z).
        If z is omitted, it's calculated from x and y (as x + y + z = 0).
        
        Args:
            x: The x-coordinate (east-west axis)
            y: The y-coordinate (northwest-southeast axis)
            z: The z-coordinate (northeast-southwest axis), calculated if None
        """
        self.x = x
        self.y = y
        
        # In cube coordinates, x + y + z must equal 0
        if z is None:
            self.z = -x - y
        else:
            self.z = z
            # Validate that x + y + z = 0 (allowing for floating point imprecision)
            if abs(x + y + z) > 0.0001:
                raise ValueError(f"Invalid cube coordinates: {x}, {y}, {z}. Must satisfy x + y + z = 0")
    
    def __eq__(self, other):
        """Check if two HexCoord objects are equal."""
        if not isinstance(other, HexCoord):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z
    
    def __hash__(self):
        """Generate a hash for the HexCoord for use in dictionaries and sets."""
        return hash((self.x, self.y, self.z))
    
    def __repr__(self):
        """String representation of the HexCoord."""
        return f"HexCoord({self.x}, {self.y}, {self.z})"
    
    def __add__(self, other):
        """Add two hex coordinates."""
        return HexCoord(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        """Subtract one hex coordinate from another."""
        return HexCoord(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        """Multiply a hex coordinate by a scalar."""
        return HexCoord(self.x * scalar, self.y * scalar, self.z * scalar)
    
    # Coordinate conversions
    
    @classmethod
    def from_axial(cls, q: int, r: int) -> 'HexCoord':
        """
        Create a HexCoord from axial coordinates (q, r).
        
        Args:
            q: The q-coordinate (same as x in cube)
            r: The r-coordinate (same as z in cube)
            
        Returns:
            A new HexCoord object
        """
        x = q
        z = r
        y = -x - z
        return cls(x, y, z)
    
    @classmethod
    def from_offset(cls, col: int, row: int, orientation: HexOrientation = HexOrientation.POINTY_TOP) -> 'HexCoord':
        """
        Create a HexCoord from offset coordinates (col, row).
        
        Args:
            col: The column in the offset system
            row: The row in the offset system
            orientation: The orientation of the hex grid (POINTY_TOP or FLAT_TOP)
            
        Returns:
            A new HexCoord object
        """
        if orientation == HexOrientation.POINTY_TOP:
            # Odd-r offset
            x = col - (row - (row & 1)) // 2
            z = row
            y = -x - z
        else:  # FLAT_TOP
            # Odd-q offset
            x = col
            z = row - (col - (col & 1)) // 2
            y = -x - z
        
        return cls(x, y, z)
    
    def to_axial(self) -> Tuple[int, int]:
        """
        Convert to axial coordinates (q, r).
        
        Returns:
            A tuple of (q, r)
        """
        return (self.x, self.z)
    
    def to_offset(self, orientation: HexOrientation = HexOrientation.POINTY_TOP) -> Tuple[int, int]:
        """
        Convert to offset coordinates (col, row).
        
        Args:
            orientation: The orientation of the hex grid (POINTY_TOP or FLAT_TOP)
            
        Returns:
            A tuple of (col, row)
        """
        if orientation == HexOrientation.POINTY_TOP:
            # Odd-r offset
            col = self.x + (self.z - (self.z & 1)) // 2
            row = self.z
        else:  # FLAT_TOP
            # Odd-q offset
            col = self.x
            row = self.z + (self.x - (self.x & 1)) // 2
        
        return (col, row)
    
    # Distance and neighbor calculations
    
    def distance(self, other: 'HexCoord') -> int:
        """
        Calculate the distance between this hex and another in terms of hex steps.
        
        Args:
            other: The other HexCoord
            
        Returns:
            The distance in hex steps
        """
        return (abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)) // 2
    
    def get_neighbors(self) -> List['HexCoord']:
        """
        Get the six neighboring hexes.
        
        Returns:
            A list of the six adjacent HexCoord objects
        """
        # Directions in cube coordinates: (x, y, z)
        directions = [
            HexCoord(1, -1, 0), HexCoord(1, 0, -1), HexCoord(0, 1, -1),
            HexCoord(-1, 1, 0), HexCoord(-1, 0, 1), HexCoord(0, -1, 1)
        ]
        
        return [self + direction for direction in directions]
    
    def get_neighbor(self, direction: int) -> 'HexCoord':
        """
        Get a specific neighboring hex by direction (0-5).
        For pointy-top: 0=E, 1=SE, 2=SW, 3=W, 4=NW, 5=NE
        For flat-top: 0=NE, 1=E, 2=SE, 3=SW, 4=W, 5=NW
        
        Args:
            direction: Integer from 0-5 representing direction
            
        Returns:
            The neighboring HexCoord in the specified direction
        """
        directions = [
            HexCoord(1, -1, 0), HexCoord(1, 0, -1), HexCoord(0, 1, -1),
            HexCoord(-1, 1, 0), HexCoord(-1, 0, 1), HexCoord(0, -1, 1)
        ]
        
        return self + directions[direction % 6]
    
    def get_range(self, radius: int) -> List['HexCoord']:
        """
        Get all hexes within a certain range.
        
        Args:
            radius: The range in hex steps
            
        Returns:
            A list of all HexCoord objects within the specified radius
        """
        results = []
        
        for x in range(-radius, radius + 1):
            for y in range(max(-radius, -x - radius), min(radius, -x + radius) + 1):
                z = -x - y
                results.append(HexCoord(self.x + x, self.y + y, self.z + z))
        
        return results
    
    # Line and line of sight calculations
    
    def linedraw(self, other: 'HexCoord') -> List['HexCoord']:
        """
        Draw a line from this hex to another, including both endpoints.
        Uses the supercover line algorithm for hexagonal grids.
        
        Args:
            other: The target HexCoord
            
        Returns:
            A list of HexCoord objects along the line
        """
        N = self.distance(other)
        if N == 0:
            return [self]
        
        results = []
        step = 1.0 / max(N, 1)
        
        # Linear interpolation between the two points
        for i in range(N + 1):
            t = step * i
            x = round(self.x * (1 - t) + other.x * t)
            y = round(self.y * (1 - t) + other.y * t)
            z = round(self.z * (1 - t) + other.z * t)
            
            # Handle rounding errors
            if x + y + z != 0:
                # Find the component with the largest rounding adjustment
                abs_dx = abs(x - (self.x * (1 - t) + other.x * t))
                abs_dy = abs(y - (self.y * (1 - t) + other.y * t))
                abs_dz = abs(z - (self.z * (1 - t) + other.z * t))
                
                if abs_dx >= abs_dy and abs_dx >= abs_dz:
                    x = -y - z
                elif abs_dy >= abs_dz:
                    y = -x - z
                else:
                    z = -x - y
            
            results.append(HexCoord(x, y, z))
        
        return results
    
    def has_line_of_sight(self, other: 'HexCoord', blockers: Set['HexCoord']) -> bool:
        """
        Determine if there's a clear line of sight between this hex and another.
        
        Args:
            other: The target HexCoord
            blockers: A set of HexCoord objects that block line of sight
            
        Returns:
            True if there's a clear line of sight, False otherwise
        """
        # Get all hexes along the line
        line = self.linedraw(other)
        
        # Check if any hex along the line (excluding endpoints) is a blocker
        for hex in line[1:-1]:  # Skip the endpoints
            if hex in blockers:
                return False
        
        return True
    
    # Conversion to/from screen coordinates
    
    def to_pixel(self, orientation: HexOrientation, size: float, origin: Tuple[float, float]) -> Tuple[float, float]:
        """
        Convert hex coordinates to pixel coordinates.
        
        Args:
            orientation: POINTY_TOP or FLAT_TOP
            size: Size of a hex (distance from center to corner)
            origin: Pixel coordinates of the grid origin (0,0,0)
            
        Returns:
            A tuple of (x, y) pixel coordinates
        """
        M = POINTY_TOP if orientation == HexOrientation.POINTY_TOP else FLAT_TOP
        
        x = (M.f0 * self.x + M.f1 * self.y) * size + origin[0]
        y = (M.f2 * self.x + M.f3 * self.y) * size + origin[1]
        
        return (x, y)
    
    @classmethod
    def from_pixel(cls, x: float, y: float, orientation: HexOrientation, 
                  size: float, origin: Tuple[float, float]) -> 'HexCoord':
        """
        Convert pixel coordinates to the nearest hex coordinates.
        
        Args:
            x: Pixel x-coordinate
            y: Pixel y-coordinate
            orientation: POINTY_TOP or FLAT_TOP
            size: Size of a hex (distance from center to corner)
            origin: Pixel coordinates of the grid origin (0,0,0)
            
        Returns:
            The nearest HexCoord
        """
        M = POINTY_TOP if orientation == HexOrientation.POINTY_TOP else FLAT_TOP
        
        # Adjust for origin
        px = (x - origin[0]) / size
        py = (y - origin[1]) / size
        
        # Convert to cube coordinates (floating point)
        q = M.b0 * px + M.b1 * py
        r = M.b2 * px + M.b3 * py
        
        # Convert to rounded cube coordinates
        return cls.cube_round(q, -q-r, r)
    
    @classmethod
    def cube_round(cls, x: float, y: float, z: float) -> 'HexCoord':
        """
        Round floating point cube coordinates to the nearest hex.
        
        Args:
            x: Floating point x-coordinate
            y: Floating point y-coordinate
            z: Floating point z-coordinate
            
        Returns:
            The nearest HexCoord
        """
        rx = round(x)
        ry = round(y)
        rz = round(z)
        
        # Calculate the differences
        x_diff = abs(rx - x)
        y_diff = abs(ry - y)
        z_diff = abs(rz - z)
        
        # Adjust the rounded values if needed
        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry
        
        return cls(rx, ry, rz)
    
    def get_corner_pixel(self, orientation: HexOrientation, corner: int, 
                        size: float, origin: Tuple[float, float]) -> Tuple[float, float]:
        """
        Get the pixel coordinates of a specific corner of this hex.
        
        Args:
            orientation: POINTY_TOP or FLAT_TOP
            corner: Integer from 0-5 representing the corner (clockwise from right/top-right)
            size: Size of a hex (distance from center to corner)
            origin: Pixel coordinates of the grid origin (0,0,0)
            
        Returns:
            A tuple of (x, y) pixel coordinates for the corner
        """
        M = POINTY_TOP if orientation == HexOrientation.POINTY_TOP else FLAT_TOP
        center = self.to_pixel(orientation, size, origin)
        angle = 2.0 * math.pi * (M.start_angle + corner) / 6.0
        
        return (
            center[0] + size * math.cos(angle),
            center[1] + size * math.sin(angle)
        )
    
    def get_all_corners_pixel(self, orientation: HexOrientation, 
                             size: float, origin: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Get the pixel coordinates of all corners of this hex.
        
        Args:
            orientation: POINTY_TOP or FLAT_TOP
            size: Size of a hex (distance from center to corner)
            origin: Pixel coordinates of the grid origin (0,0,0)
            
        Returns:
            A list of (x, y) pixel coordinates for all corners
        """
        return [self.get_corner_pixel(orientation, i, size, origin) for i in range(6)]


class HexCell:
    """Represents the contents of a single hex in the grid."""
    
    def __init__(self, terrain_type: str = "ocean", 
                 movement_cost: float = 1.0,
                 blocks_sight: bool = False,
                 metadata: Dict[str, Any] = None):
        """
        Initialize a hex cell.
        
        Args:
            terrain_type: Type of terrain in this hex
            movement_cost: Cost to move through this hex (1.0 is normal)
            blocks_sight: Whether this hex blocks line of sight
            metadata: Additional metadata for this hex
        """
        self.terrain_type = terrain_type
        self.movement_cost = movement_cost
        self.blocks_sight = blocks_sight
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the cell to a dictionary for serialization."""
        return {
            "terrain_type": self.terrain_type,
            "movement_cost": self.movement_cost,
            "blocks_sight": self.blocks_sight,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HexCell':
        """Create a cell from a dictionary."""
        return cls(
            terrain_type=data.get("terrain_type", "ocean"),
            movement_cost=data.get("movement_cost", 1.0),
            blocks_sight=data.get("blocks_sight", False),
            metadata=data.get("metadata", {})
        )


class HexGrid:
    """
    Manages a hexagonal grid of cells.
    Handles storage, retrieval, and operations on the grid.
    """
    
    def __init__(self, orientation: HexOrientation = HexOrientation.POINTY_TOP, 
                 hex_size: float = 10.0,
                 origin: Tuple[float, float] = (0, 0)):
        """
        Initialize a hex grid.
        
        Args:
            orientation: POINTY_TOP or FLAT_TOP
            hex_size: Size of a hex (distance from center to corner)
            origin: Pixel coordinates of the grid origin (0,0,0)
        """
        self.orientation = orientation
        self.hex_size = hex_size
        self.origin = origin
        self.cells: Dict[HexCoord, HexCell] = {}
    
    def get_cell(self, coord: HexCoord) -> Optional[HexCell]:
        """
        Get the cell at the specified coordinates.
        
        Args:
            coord: The hex coordinates
            
        Returns:
            The HexCell at those coordinates, or None if not found
        """
        return self.cells.get(coord)
    
    def set_cell(self, coord: HexCoord, cell: HexCell) -> None:
        """
        Set the cell at the specified coordinates.
        
        Args:
            coord: The hex coordinates
            cell: The HexCell to place at those coordinates
        """
        self.cells[coord] = cell
    
    def remove_cell(self, coord: HexCoord) -> None:
        """
        Remove the cell at the specified coordinates.
        
        Args:
            coord: The hex coordinates to remove
        """
        if coord in self.cells:
            del self.cells[coord]
    
    def get_all_coords(self) -> List[HexCoord]:
        """
        Get all coordinates in the grid.
        
        Returns:
            A list of all HexCoord objects in the grid
        """
        return list(self.cells.keys())
    
    def is_in_bounds(self, coord: HexCoord) -> bool:
        """
        Check if coordinates are within the grid.
        
        Args:
            coord: The hex coordinates to check
            
        Returns:
            True if the coordinates are in the grid, False otherwise
        """
        return coord in self.cells
    
    # Pathfinding methods
    
    def get_neighbors_for_pathfinding(self, coord: HexCoord) -> List[Tuple[HexCoord, float]]:
        """
        Get neighboring coordinates and movement costs for pathfinding.
        
        Args:
            coord: The center hex coordinates
            
        Returns:
            A list of tuples (neighbor_coord, movement_cost)
        """
        neighbors = []
        
        for neighbor_coord in coord.get_neighbors():
            cell = self.get_cell(neighbor_coord)
            if cell:
                neighbors.append((neighbor_coord, cell.movement_cost))
        
        return neighbors
    
    def find_path(self, start: HexCoord, goal: HexCoord) -> List[HexCoord]:
        """
        Find a path between two coordinates using A* algorithm.
        
        Args:
            start: Starting hex coordinates
            goal: Target hex coordinates
            
        Returns:
            A list of HexCoord objects forming the path (including start and goal),
            or an empty list if no path is found
        """
        # If either start or goal is not in the grid, return empty path
        if not self.is_in_bounds(start) or not self.is_in_bounds(goal):
            return []
        
        # A* algorithm implementation
        open_set = {start}
        closed_set = set()
        
        # Came_from maps each node to its predecessor in the optimal path
        came_from = {}
        
        # g_score maps each node to its cost from the start
        g_score = {start: 0}
        
        # f_score maps each node to its estimated total cost (g_score + heuristic)
        f_score = {start: start.distance(goal)}
        
        while open_set:
            # Find the node in open_set with the lowest f_score
            current = min(open_set, key=lambda h: f_score.get(h, float('inf')))
            
            if current == goal:
                # Reconstruct the path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            open_set.remove(current)
            closed_set.add(current)
            
            for neighbor, cost in self.get_neighbors_for_pathfinding(current):
                if neighbor in closed_set:
                    continue
                
                tentative_g_score = g_score.get(current, float('inf')) + cost
                
                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                    continue
                
                # This path is the best so far
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + neighbor.distance(goal)
        
        # No path found
        return []
    
    # Serialization methods
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the grid to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the grid
        """
        cells_dict = {}
        
        for coord, cell in self.cells.items():
            # Convert HexCoord to string for JSON
            key = f"{coord.x},{coord.y},{coord.z}"
            cells_dict[key] = cell.to_dict()
        
        return {
            "orientation": self.orientation.value,
            "hex_size": self.hex_size,
            "origin": self.origin,
            "cells": cells_dict
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HexGrid':
        """
        Create a grid from a dictionary.
        
        Args:
            data: Dictionary containing grid data
            
        Returns:
            A new HexGrid object
        """
        grid = cls(
            orientation=HexOrientation(data.get("orientation", HexOrientation.POINTY_TOP.value)),
            hex_size=data.get("hex_size", 10.0),
            origin=tuple(data.get("origin", (0, 0)))
        )
        
        # Load cells
        cells_dict = data.get("cells", {})
        for coord_str, cell_data in cells_dict.items():
            # Parse coordinate string
            x, y, z = map(int, coord_str.split(","))
            coord = HexCoord(x, y, z)
            
            # Create cell and add to grid
            cell = HexCell.from_dict(cell_data)
            grid.set_cell(coord, cell)
        
        return grid
    
    def to_json(self) -> str:
        """
        Convert the grid to a JSON string.
        
        Returns:
            A JSON string representation of the grid
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'HexGrid':
        """
        Create a grid from a JSON string.
        
        Args:
            json_str: JSON string containing grid data
            
        Returns:
            A new HexGrid object
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    # Utility methods
    
    def create_rectangle(self, width: int, height: int, 
                         terrain_type: str = "ocean") -> None:
        """
        Create a rectangular grid of hexes.
        
        Args:
            width: Width of the rectangle in hexes
            height: Height of the rectangle in hexes
            terrain_type: Type of terrain for all cells
        """
        for q in range(width):
            q_offset = q // 2  # Offset for even-q coordinates
            for r in range(-q_offset, height - q_offset):
                coord = HexCoord.from_axial(q, r)
                cell = HexCell(terrain_type=terrain_type)
                self.set_cell(coord, cell)
    
    def create_hexagon(self, radius: int, center: HexCoord = None,
                       terrain_type: str = "ocean") -> None:
        """
        Create a hexagonal grid of hexes.
        
        Args:
            radius: Radius of the hexagon in hexes
            center: Center coordinates (defaults to origin)
            terrain_type: Type of terrain for all cells
        """
        center = center or HexCoord(0, 0, 0)
        
        for coord in center.get_range(radius):
            cell = HexCell(terrain_type=terrain_type)
            self.set_cell(coord, cell)
'''
    write_file(path, content)

def create_hex_renderer_file():
    """Create the hex_renderer.py file."""
    path = os.path.join(PROJECT_ROOT, "src/engine/hex_renderer.py")
    content = '''"""
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
                console.ch[y1, x1] = ord('·')  # Using a small dot for the line
            
            if x1 == x2 and y1 == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
'''
    write_file(path, content)

def create_hex_grid_test_file():
    """Create the hex_grid_test.py file."""
    path = os.path.join(PROJECT_ROOT, "src/examples/hex_grid_test.py")
    content = '''"""
Example code to test the hex grid implementation.
Creates a small grid and renders it to the screen.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tcod import libtcodpy
from tcod.context import Context
from tcod.console import Console
from tcod import event

from src.engine.hex_grid import HexCoord, HexGrid, HexOrientation, HexCell
from src.engine.hex_renderer import HexRenderer
from src.config import Config

def run_hex_grid_test():
    """Run a test of the hex grid implementation."""
    # Set up the font
    libtcodpy.console_set_custom_font(
        Config.FONT_PATH,
        Config.FONT_FLAGS
    )
    
    # Create a context (window)
    context = Context(
        columns=Config.SCREEN_WIDTH,
        rows=Config.SCREEN_HEIGHT,
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
    
    # Create the renderer
    renderer = HexRenderer(grid)
    
    # Selected hex
    selected_coord = HexCoord(0, 0, 0)
    renderer.set_selected_hex(selected_coord)
    
    # Camera position
    camera_offset = [0, 0]
    camera_speed = 10
    
    # Main loop
    running = True
    while running:
        # Clear the console
        console.clear()
        
        # Render the grid
        renderer.render(console, camera_offset)
        
        # Draw instructions
        console.print(
            2, 2,
            "Arrow keys: Move camera",
            fg=(255, 255, 255)
        )
        console.print(
            2, 3,
            "Mouse: Select hex",
            fg=(255, 255, 255)
        )
        console.print(
            2, 4,
            "P: Test pathfinding",
            fg=(255, 255, 255)
        )
        console.print(
            2, 5,
            "ESC: Quit",
            fg=(255, 255, 255)
        )
        
        # Draw selected hex info
        cell = grid.get_cell(selected_coord)
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
        
        # Handle events
        for evt in event.wait():
            # Check for window close
            if evt.type == event.QUIT:
                running = False
                break
            
            # Handle keyboard events
            elif evt.type == event.KEYDOWN:
                if evt.sym == event.K_ESCAPE:
                    running = False
                    break
                elif evt.sym == event.K_UP:
                    camera_offset[1] -= camera_speed
                elif evt.sym == event.K_DOWN:
                    camera_offset[1] += camera_speed
                elif evt.sym == event.K_LEFT:
                    camera_offset[0] -= camera_speed
                elif evt.sym == event.K_RIGHT:
                    camera_offset[0] += camera_speed
                elif evt.sym == event.K_p:
                    # Test pathfinding
                    start = selected_coord
                    goal = HexCoord.from_axial(3, -1)  # Port Royal
                    path = grid.find_path(start, goal)
                    print(f"Path from {start} to {goal}:")
                    for coord in path:
                        print(f"  {coord}")
            
            # Handle mouse movement
            elif evt.type == event.MOUSEMOTION:
                # Get hex at mouse position
                mouse_pos = event.get_mouse_state()
                hex_coord = renderer.get_hex_at_pixel(
                    mouse_pos.x + camera_offset[0], 
                    mouse_pos.y + camera_offset[1]
                )
                if grid.get_cell(hex_coord):
                    renderer.set_selected_hex(hex_coord)
                    selected_coord = hex_coord

if __name__ == "__main__":
    run_hex_grid_test()
'''
    write_file(path, content)

def create_main_runner():
    """Create a main.py file in the project root for easy running."""
    path = os.path.join(PROJECT_ROOT, "main.py")
    content = '''"""
Main entry point for RedRumRunner hex grid test.
"""
import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the test module
from src.examples.hex_grid_test import run_hex_grid_test

if __name__ == "__main__":
    print("Running RedRumRunner hex grid test...")
    run_hex_grid_test()
'''
    write_file(path, content)

def setup_project():
    """Set up the entire project."""
    print("Setting up RedRumRunner hex grid project with updated tcod API...")
    
    # Create directories
    create_directories()
    
    # Download font file
    download_font()
    
    # Create __init__.py files
    create_init_files()
    
    # Create code files
    create_config_file()
    create_hex_grid_file()
    create_hex_renderer_file()
    create_hex_grid_test_file()
    create_main_runner()
    
    print("\nProject setup complete!")
    print(f"Project created in: {os.path.abspath(PROJECT_ROOT)}")
    print("\nTo run the hex grid test:")
    print(f"cd {PROJECT_ROOT}")
    print("python main.py")

if __name__ == "__main__":
    setup_project()
