"""
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
