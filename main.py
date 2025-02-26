import tcod
import tcod.event as event
import logging
import sys
import os
import time
import traceback

from src.engine.game_state import GameState
from src.engine.state_machine import StateMachine
from src.engine.calendar import Calendar
from src.states.main_menu_state import MainMenuState
from src.states.world_map_state import WorldMapState
from src.states.port_interface_state import PortInterfaceState
from src.states.fleet_management_state import FleetManagementState
from src.states.combat_state import CombatState
from src.utils.error_handler import ErrorHandler
from src.utils.state_validator import StateValidator
from src.config import Config

def setup_logging():
    """Setup logging configuration."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "game.log")),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function."""
    setup_logging()
    logger = logging.getLogger("main")
    
    logger.info("Starting RedRumRunner")
    
    # Set up error handling
    error_handler = ErrorHandler()
    error_handler.install_global_handler()
    
    # Create default schemas
    try:
        StateValidator.create_default_schemas()
    except Exception as e:
        logger.warning(f"Could not create default schemas: {e}")
    
    # Set up the font
    try:
        tcod.console_set_custom_font(
            Config.FONT_PATH,
            Config.FONT_FLAGS
        )
    except Exception as e:
        logger.error(f"Error loading font: {e}")
        logger.info("Using default font")
    
    # Create a context (window)
    width = Config.SCREEN_WIDTH
    height = Config.SCREEN_HEIGHT
    
    try:
        with tcod.context.new_terminal(
            width,
            height,
            tileset=None,
            title=Config.WINDOW_TITLE,
            vsync=True
        ) as context:
            # Create main console for rendering
            console = tcod.Console(width, height)
            
            # Create game state
            game_state = GameState()
            
            # Initialize calendar
            game_state.calendar = Calendar()
            
            # Create state machine
            state_machine = StateMachine()
            
            # Wrap state machine with error handling
            error_handler.wrap_state_functions(state_machine)
            
            # Add states
            state_machine.add_state("main_menu", MainMenuState(game_state))
            state_machine.add_state("world_map", WorldMapState(game_state))
            state_machine.add_state("port_interface", PortInterfaceState(game_state))
            state_machine.add_state("fleet_management", FleetManagementState(game_state))
            state_machine.add_state("combat", CombatState(game_state))
            
            # Validate game state before starting
            validator = StateValidator()
            valid, errors = validator.validate_game_state(game_state)
            if not valid:
                logger.warning(f"Initial game state validation failed: {errors}")
            
            # Set initial state
            state_machine.set_state("main_menu")
            
            # Game loop
            previous_time = time.time()
            running = True
            
            while running:
                # Calculate delta time
                current_time = time.time()
                delta_time = current_time - previous_time
                previous_time = current_time
                
                # Limit delta time to prevent huge jumps
                delta_time = min(delta_time, 0.1)
                
                # Process input
                for evt in tcod.event.wait():
                    # Exit check
                    if isinstance(evt, tcod.event.Quit):
                        running = False
                        break
                    
                    # Forward events to state machine for handling
                    try:
                        if state_machine.handle_event(evt):
                            continue
                    except SystemExit:
                        running = False
                        break
                    
                if not running:
                    break
                
                # Update state
                state_machine.update(delta_time)
                
                # Render
                console.clear()
                state_machine.render(console)
                context.present(console)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        logger.critical(f"Stack trace: {traceback.format_exc()}")
        # In a real game, we would show an error dialog to the user
        
    logger.info("Exiting RedRumRunner")

if __name__ == "__main__":
    main()
