# File: main.py
"""
RedRumRunner - Main entry point
A pirate-themed roguelike with fleet management and procedurally generated worlds.
"""
import tcod
import time
import sys
from src.engine.game_engine import GameEngine
from src.config import Config

def main():
    """Main function that initializes the game and runs the main loop."""
    # Initialize game engine
    engine = GameEngine()
    engine.initialize()
    
    # Track time for frame rate control
    last_frame_time = time.time()
    
    # Main game loop
    while engine.is_running:
        # Calculate delta time
        current_time = time.time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time
        
        # Process input
        engine.handle_input()
        
        # Update game state
        engine.update(delta_time)
        
        # Render the game
        engine.render()
        
    # Clean up resources when exiting
    engine.cleanup()
    sys.exit()

if __name__ == "__main__":
    main()

# File: config.py
"""
Configuration settings for RedRumRunner.
Centralizes game parameters and settings.
"""
import tcod

class Config:
    """Configuration class holding game parameters."""
    # Display settings
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 50
    WINDOW_TITLE = "RedRumRunner"
    FPS_LIMIT = 60
    FULLSCREEN = False
    
    # Font settings
    FONT_PATH = "assets/fonts/dejavu10x10_gs_tc.png"
    FONT_FLAGS = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
    
    # Game settings
    TURN_BASED = True
    
    # Debug settings
    DEBUG_MODE = True
    SHOW_FPS = True

# File: requirements.txt
tcod>=13.0.0
numpy>=1.20.0
pytest>=7.0.0  # For testing

# File: README.md
# RedRumRunner

A pirate-themed roguelike with procedurally-generated worlds, turn-based gameplay on a hexagonal grid, and a focus on building a fleet to defeat an armada.

## Game Overview

In RedRumRunner, you play as a sea captain who starts with one ship and must build a fleet capable of defeating (or capturing) the authorities' armada. The game features:

- Procedurally-generated worlds with approximately 100 locations
- Turn-based gameplay on a hexagonal grid
- Ship-to-ship combat focused on boarding and capturing
- Economic system with trading, smuggling, and resource management
- Fleet and crew management
- Escalating authority response system
- Modding support through JSON-based content files

## Development

### Requirements
- Python 3.8+
- tcod 13.0.0+
- numpy 1.20.0+

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python main.py`

## Folder Structure
- `src/`: Python source code
- `assets/`: Game assets (fonts, etc.)
- `data/`: JSON data files for game content
- `docs/`: Documentation

# File: src/engine/game_engine.py
"""
Core game engine for RedRumRunner.
Handles initialization, main loop management, and system coordination.
"""
import tcod
from src.config import Config
from src.engine.input_handler import InputHandler
from src.engine.renderer import Renderer
from src.engine.state_manager import StateManager

class GameEngine:
    """
    Main game engine class that coordinates all game systems.
    Acts as the central hub connecting input, rendering, and game state.
    """
    
    def __init__(self):
        """Initialize the game engine components."""
        self.is_running = False
        self.config = Config()
        self.console = None
        self.root_console = None
        self.input_handler = InputHandler()
        self.renderer = None
        self.state_manager = StateManager(self)
    
    def initialize(self):
        """Initialize tcod and set up the game window and systems."""
        # Set custom font
        tcod.console_set_custom_font(
            self.config.FONT_PATH,
            self.config.FONT_FLAGS
        )
        
        # Initialize the root console (window)
        self.root_console = tcod.console_init_root(
            self.config.SCREEN_WIDTH,
            self.config.SCREEN_HEIGHT,
            self.config.WINDOW_TITLE,
            self.config.FULLSCREEN
        )
        
        # Create main console for rendering
        self.console = tcod.Console(
            self.config.SCREEN_WIDTH,
            self.config.SCREEN_HEIGHT
        )
        
        # Initialize renderer
        self.renderer = Renderer(self.console, self.root_console)
        
        # Initialize game states and set to main menu
        self.state_manager.initialize()
        
        # Set running flag to true
        self.is_running = True
        
        print("Game initialized successfully!")
    
    def handle_input(self):
        """Process input events and dispatch to current state."""
        for event in tcod.event.get():
            # Check for window close event
            if event.type == tcod.event.QUIT:
                self.is_running = False
                return
            
            # Let the current state handle the event
            action = self.input_handler.handle_event(event)
            if action:
                self.state_manager.handle_action(action)
    
    def update(self, delta_time):
        """Update game state based on time elapsed."""
        # Update the current game state
        self.state_manager.update(delta_time)
    
    def render(self):
        """Render the current game state to the screen."""
        # Clear the console
        self.console.clear()
        
        # Let the current state render to the console
        self.state_manager.render(self.console)
        
        # Present the console to the screen
        self.renderer.render()
    
    def cleanup(self):
        """Clean up resources before exiting."""
        print("Cleaning up resources...")
        # Any cleanup code would go here

# File: src/engine/input_handler.py
"""
Input handling system for RedRumRunner.
Processes input events and converts them to game actions.
"""
import tcod.event

class InputHandler:
    """Handles input events and maps them to game actions."""
    
    def handle_event(self, event):
        """
        Process an input event and return a corresponding game action.
        
        Args:
            event: A tcod event to process
            
        Returns:
            An action dict or None if the event doesn't map to an action
        """
        if event.type == tcod.event.KEYDOWN:
            return self._handle_key(event)
        
        return None
    
    def _handle_key(self, event):
        """Map key presses to game actions."""
        key = event.sym
        
        # Common actions that might be used across different states
        if key == tcod.event.K_ESCAPE:
            return {"type": "ESCAPE"}
        elif key == tcod.event.K_UP:
            return {"type": "MOVE", "direction": "up"}
        elif key == tcod.event.K_DOWN:
            return {"type": "MOVE", "direction": "down"}
        elif key == tcod.event.K_LEFT:
            return {"type": "MOVE", "direction": "left"}
        elif key == tcod.event.K_RIGHT:
            return {"type": "MOVE", "direction": "right"}
        elif key == tcod.event.K_RETURN:
            return {"type": "CONFIRM"}
        
        return None

# File: src/engine/renderer.py
"""
Rendering system for RedRumRunner.
Handles drawing to the console and presenting to the screen.
"""
import tcod

class Renderer:
    """Handles rendering the game to the screen."""
    
    def __init__(self, console, root_console):
        """
        Initialize the renderer.
        
        Args:
            console: The main console to render to
            root_console: The root console for the window
        """
        self.console = console
        self.root_console = root_console
    
    def render(self):
        """Render the main console to the screen."""
        # Copy the main console to the root console
        self.console.blit(self.root_console, 0, 0)
        
        # Present the root console to the screen
        tcod.console_flush()

# File: src/engine/state_manager.py
"""
State management system for RedRumRunner.
Handles game states and transitions between them.
"""
from src.game.states.main_menu_state import MainMenuState

class StateManager:
    """Manages game states and transitions between them."""
    
    def __init__(self, engine):
        """
        Initialize the state manager.
        
        Args:
            engine: Reference to the game engine
        """
        self.engine = engine
        self.states = []  # Stack of states
        self.current_state = None
    
    def initialize(self):
        """Initialize with the starting state (main menu)."""
        initial_state = MainMenuState(self)
        self.push_state(initial_state)
    
    def push_state(self, state):
        """
        Add a new state to the top of the stack and make it active.
        
        Args:
            state: The state to add
        """
        # Pause the current state if one exists
        if self.current_state:
            self.current_state.pause()
        
        # Add the new state and make it current
        self.states.append(state)
        self.current_state = state
        self.current_state.enter()
    
    def pop_state(self):
        """
        Remove the top state from the stack and activate the next one.
        """
        if not self.states:
            return
        
        # Remove the current state
        old_state = self.states.pop()
        old_state.exit()
        
        # Set and resume the new current state if one exists
        if self.states:
            self.current_state = self.states[-1]
            self.current_state.resume()
        else:
            self.current_state = None
    
    def change_state(self, new_state):
        """
        Replace the current state with a new one.
        
        Args:
            new_state: The new state to transition to
        """
        # Remove all existing states
        while self.states:
            old_state = self.states.pop()
            old_state.exit()
        
        # Add and enter the new state
        self.states.append(new_state)
        self.current_state = new_state
        self.current_state.enter()
    
    def handle_action(self, action):
        """
        Pass an action to the current state for handling.
        
        Args:
            action: The action to handle
        """
        if self.current_state:
            self.current_state.handle_action(action)
    
    def update(self, delta_time):
        """
        Update the current state.
        
        Args:
            delta_time: Time elapsed since the last update
        """
        if self.current_state:
            self.current_state.update(delta_time)
    
    def render(self, console):
        """
        Render the current state.
        
        Args:
            console: The console to render to
        """
        if self.current_state:
            self.current_state.render(console)

# File: src/game/states/game_state.py
"""
Base class for game states in RedRumRunner.
"""

class GameState:
    """Base class for all game states."""
    
    def __init__(self, state_manager):
        """
        Initialize the state.
        
        Args:
            state_manager: Reference to the state manager
        """
        self.state_manager = state_manager
    
    def enter(self):
        """Called when the state becomes active."""
        pass
    
    def exit(self):
        """Called when the state is being removed."""
        pass
    
    def pause(self):
        """Called when the state is being paused (another state is pushed on top)."""
        pass
    
    def resume(self):
        """Called when the state is resumed (a state above it was popped)."""
        pass
    
    def handle_action(self, action):
        """
        Process a game action.
        
        Args:
            action: The action to process
        """
        pass
    
    def update(self, delta_time):
        """
        Update the state.
        
        Args:
            delta_time: Time elapsed since the last update
        """
        pass
    
    def render(self, console):
        """
        Render the state.
        
        Args:
            console: The console to render to
        """
        pass

# File: src/game/states/main_menu_state.py
"""
Main menu state for RedRumRunner.
"""
import tcod
from src.game.states.game_state import GameState
from src.game.states.world_map_state import WorldMapState

class MainMenuState(GameState):
    """State for the main menu screen."""
    
    def __init__(self, state_manager):
        """Initialize the main menu state."""
        super().__init__(state_manager)
        self.menu_options = ["New Game", "Continue", "Options", "Quit"]
        self.selected_index = 0
    
    def enter(self):
        """Called when entering this state."""
        print("Entering main menu")
    
    def handle_action(self, action):
        """Handle user input in the menu."""
        if action["type"] == "MOVE":
            if action["direction"] == "up":
                self.selected_index = max(0, self.selected_index - 1)
            elif action["direction"] == "down":
                self.selected_index = min(len(self.menu_options) - 1, self.selected_index + 1)
        
        elif action["type"] == "CONFIRM":
            self._select_current_option()
        
        elif action["type"] == "ESCAPE":
            # Exit the game
            self.state_manager.engine.is_running = False
    
    def render(self, console):
        """Render the main menu."""
        # Clear with a dark blue background
        console.clear(fg=(255, 255, 255), bg=(0, 0, 60))
        
        # Draw title
        title = "RedRumRunner"
        console.print(
            console.width // 2,
            console.height // 4,
            title,
            fg=(255, 215, 0),  # Gold color
            bg=None,
            alignment=tcod.CENTER
        )
        
        # Draw subtitle
        subtitle = "A Pirate's Tale of Fleet and Fortune"
        console.print(
            console.width // 2,
            console.height // 4 + 2,
            subtitle,
            fg=(200, 200, 200),
            bg=None,
            alignment=tcod.CENTER
        )
        
        # Draw menu options
        for i, option in enumerate(self.menu_options):
            y = console.height // 2 + i * 2
            
            # Highlight the selected option
            if i == self.selected_index:
                fg_color = (255, 255, 0)  # Yellow
                option_text = f"> {option} <"
            else:
                fg_color = (200, 200, 200)  # Light gray
                option_text = option
            
            console.print(
                console.width // 2,
                y,
                option_text,
                fg=fg_color,
                bg=None,
                alignment=tcod.CENTER
            )
    
    def _select_current_option(self):
        """Execute the currently selected menu option."""
        selected = self.menu_options[self.selected_index]
        
        if selected == "New Game":
            # Create and transition to the world map state
            world_state = WorldMapState(self.state_manager)
            self.state_manager.change_state(world_state)
        
        elif selected == "Continue":
            # Load game functionality (to be implemented)
            print("Load game not implemented yet")
        
        elif selected == "Options":
            # Options menu (to be implemented)
            print("Options menu not implemented yet")
        
        elif selected == "Quit":
            # Exit the game
            self.state_manager.engine.is_running = False

# File: src/game/states/world_map_state.py
"""
World map state for RedRumRunner.
Handles the strategic view of the game world.
"""
import tcod
from src.game.states.game_state import GameState

class WorldMapState(GameState):
    """State for the world map and strategic gameplay."""
    
    def __init__(self, state_manager):
        """Initialize the world map state."""
        super().__init__(state_manager)
        # Placeholder for world data that will be added later
        self.world = None
        self.player_fleet = None
    
    def enter(self):
        """Called when entering this state."""
        print("Entering world map")
        # Future: Initialize world generation here
    
    def handle_action(self, action):
        """Handle user input on the world map."""
        if action["type"] == "ESCAPE":
            # Return to main menu
            from src.game.states.main_menu_state import MainMenuState
            self.state_manager.change_state(MainMenuState(self.state_manager))
        
        # Future: Handle movement and other world map actions
    
    def update(self, delta_time):
        """Update the world map state."""
        # Future: Update world entities, time, etc.
        pass
    
    def render(self, console):
        """Render the world map."""
        # Clear with a dark blue background (ocean)
        console.clear(fg=(255, 255, 255), bg=(0, 0, 40))
        
        # Placeholder text until we implement actual world rendering
        console.print(
            console.width // 2,
            console.height // 2,
            "World Map - Coming Soon",
            fg=(255, 255, 255),
            bg=None,
            alignment=tcod.CENTER
        )
        
        # Instructions
        console.print(
            console.width // 2,
            console.height - 2,
            "Press ESC to return to main menu",
            fg=(200, 200, 200),
            bg=None,
            alignment=tcod.CENTER
        )

# Create directory structure and __init__.py files to make the package structure work

# File: src/__init__.py
"""RedRumRunner game package."""

# File: src/engine/__init__.py
"""Engine module for game core components."""

# File: src/game/__init__.py
"""Game module for game-specific logic."""

# File: src/game/states/__init__.py
"""Game states module."""
