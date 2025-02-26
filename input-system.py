# File: src/engine/input_handler.py
"""
Enhanced input handling system for RedRumRunner.
Processes input events and converts them to game actions with customizable mapping.
"""
import tcod.event
from enum import Enum, auto

class InputMode(Enum):
    """Enum representing different input modes for context-sensitive controls."""
    NORMAL = auto()
    MENU = auto()
    WORLD_MAP = auto()
    TACTICAL = auto()
    DIALOG = auto()
    TEXT_INPUT = auto()

class GameAction(Enum):
    """Enum representing different types of game actions."""
    NONE = auto()
    QUIT = auto()
    ESCAPE = auto()
    CONFIRM = auto()
    CANCEL = auto()
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UP_LEFT = auto()
    MOVE_UP_RIGHT = auto()
    MOVE_DOWN_LEFT = auto()
    MOVE_DOWN_RIGHT = auto()
    ROTATE_CLOCKWISE = auto()
    ROTATE_COUNTERCLOCKWISE = auto()
    SELECT = auto()
    INTERACT = auto()
    INVENTORY = auto()
    CHARACTER = auto()
    MAP = auto()
    WAIT = auto()
    ZOOM_IN = auto()
    ZOOM_OUT = auto()
    HELP = auto()
    DEBUG = auto()

class InputHandler:
    """
    Handles input events and maps them to game actions.
    Supports different input modes for context-sensitive controls.
    """
    
    def __init__(self):
        """Initialize the input handler with default key mappings."""
        self.current_mode = InputMode.NORMAL
        self.text_input_buffer = ""
        self.text_input_callback = None
        
        # Define key mappings for different modes
        self.key_mappings = self._create_default_key_mappings()
        
        # Mouse state
        self.mouse_position = (0, 0)
        self.mouse_button_state = {
            tcod.event.BUTTON_LEFT: False,
            tcod.event.BUTTON_RIGHT: False,
            tcod.event.BUTTON_MIDDLE: False
        }
    
    def _create_default_key_mappings(self):
        """Create the default key mappings for different input modes."""
        mappings = {}
        
        # Normal mode mappings
        normal_mode = {
            # Universal keys
            tcod.event.K_ESCAPE: GameAction.ESCAPE,
            tcod.event.K_RETURN: GameAction.CONFIRM,
            tcod.event.K_SPACE: GameAction.SELECT,
            
            # Movement keys
            tcod.event.K_UP: GameAction.MOVE_UP,
            tcod.event.K_DOWN: GameAction.MOVE_DOWN,
            tcod.event.K_LEFT: GameAction.MOVE_LEFT,
            tcod.event.K_RIGHT: GameAction.MOVE_RIGHT,
            tcod.event.K_HOME: GameAction.MOVE_UP_LEFT,
            tcod.event.K_PAGEUP: GameAction.MOVE_UP_RIGHT,
            tcod.event.K_END: GameAction.MOVE_DOWN_LEFT,
            tcod.event.K_PAGEDOWN: GameAction.MOVE_DOWN_RIGHT,
            
            # Numpad movement
            tcod.event.K_KP_8: GameAction.MOVE_UP,
            tcod.event.K_KP_2: GameAction.MOVE_DOWN,
            tcod.event.K_KP_4: GameAction.MOVE_LEFT,
            tcod.event.K_KP_6: GameAction.MOVE_RIGHT,
            tcod.event.K_KP_7: GameAction.MOVE_UP_LEFT,
            tcod.event.K_KP_9: GameAction.MOVE_UP_RIGHT,
            tcod.event.K_KP_1: GameAction.MOVE_DOWN_LEFT,
            tcod.event.K_KP_3: GameAction.MOVE_DOWN_RIGHT,
            tcod.event.K_KP_5: GameAction.WAIT,
            
            # UI keys
            tcod.event.K_i: GameAction.INVENTORY,
            tcod.event.K_c: GameAction.CHARACTER,
            tcod.event.K_m: GameAction.MAP,
            tcod.event.K_PLUS: GameAction.ZOOM_IN,
            tcod.event.K_MINUS: GameAction.ZOOM_OUT,
            tcod.event.K_h: GameAction.HELP,
            
            # Debug keys
            tcod.event.K_F12: GameAction.DEBUG
        }
        mappings[InputMode.NORMAL] = normal_mode
        
        # Menu mode mappings (simplified for menu navigation)
        menu_mode = {
            tcod.event.K_ESCAPE: GameAction.ESCAPE,
            tcod.event.K_RETURN: GameAction.CONFIRM,
            tcod.event.K_UP: GameAction.MOVE_UP,
            tcod.event.K_DOWN: GameAction.MOVE_DOWN,
            tcod.event.K_LEFT: GameAction.MOVE_LEFT,
            tcod.event.K_RIGHT: GameAction.MOVE_RIGHT
        }
        mappings[InputMode.MENU] = menu_mode
        
        # World map mode (extends normal mode with map-specific controls)
        world_map_mode = normal_mode.copy()
        world_map_mode.update({
            tcod.event.K_q: GameAction.ROTATE_COUNTERCLOCKWISE,
            tcod.event.K_e: GameAction.ROTATE_CLOCKWISE,
        })
        mappings[InputMode.WORLD_MAP] = world_map_mode
        
        # Tactical mode (similar to world map but may have combat-specific controls)
        tactical_mode = world_map_mode.copy()
        tactical_mode.update({
            tcod.event.K_TAB: GameAction.WAIT,  # End turn in tactical mode
        })
        mappings[InputMode.TACTICAL] = tactical_mode
        
        # Dialog mode (simplified for dialog navigation)
        dialog_mode = {
            tcod.event.K_ESCAPE: GameAction.CANCEL,
            tcod.event.K_RETURN: GameAction.CONFIRM,
            tcod.event.K_UP: GameAction.MOVE_UP,
            tcod.event.K_DOWN: GameAction.MOVE_DOWN,
            tcod.event.K_SPACE: GameAction.SELECT
        }
        mappings[InputMode.DIALOG] = dialog_mode
        
        # Text input mode doesn't use action mapping the same way
        # It captures actual characters
        mappings[InputMode.TEXT_INPUT] = {
            tcod.event.K_ESCAPE: GameAction.CANCEL,
            tcod.event.K_RETURN: GameAction.CONFIRM
        }
        
        return mappings
    
    def set_mode(self, mode):
        """
        Set the current input mode.
        
        Args:
            mode: The InputMode to set
        """
        self.current_mode = mode
        
        # Reset text input state if we're entering text input mode
        if mode == InputMode.TEXT_INPUT:
            self.text_input_buffer = ""
    
    def start_text_input(self, callback=None, initial_text=""):
        """
        Start text input mode.
        
        Args:
            callback: Function to call when text input is confirmed
            initial_text: Initial text to populate the buffer with
        """
        self.text_input_buffer = initial_text
        self.text_input_callback = callback
        self.set_mode(InputMode.TEXT_INPUT)
    
    def handle_event(self, event):
        """
        Process an input event and return a corresponding game action.
        
        Args:
            event: A tcod event to process
            
        Returns:
            A dict with action information or None if the event doesn't map to an action
        """
        # Handle window close event
        if event.type == tcod.event.QUIT:
            return {"action": GameAction.QUIT}
        
        # Handle key events
        elif event.type == tcod.event.KEYDOWN:
            return self._handle_key(event)
        
        # Handle mouse movement
        elif event.type == tcod.event.MOUSEMOTION:
            self.mouse_position = (event.tile.x, event.tile.y)
            return {"action": GameAction.NONE, "mouse_position": self.mouse_position}
        
        # Handle mouse button press
        elif event.type == tcod.event.MOUSEBUTTONDOWN:
            self.mouse_button_state[event.button] = True
            return {
                "action": GameAction.SELECT,
                "button": event.button,
                "position": (event.tile.x, event.tile.y)
            }
        
        # Handle mouse button release
        elif event.type == tcod.event.MOUSEBUTTONUP:
            self.mouse_button_state[event.button] = False
            return {
                "action": GameAction.NONE,
                "button": event.button,
                "position": (event.tile.x, event.tile.y)
            }
        
        return None
    
    def _handle_key(self, event):
        """
        Map key presses to game actions based on the current input mode.
        
        Args:
            event: A tcod.event.KEYDOWN event
            
        Returns:
            A dict with action information or None if the key doesn't map to an action
        """
        key = event.sym
        
        # Special handling for text input mode
        if self.current_mode == InputMode.TEXT_INPUT:
            if key == tcod.event.K_BACKSPACE:
                # Handle backspace
                if len(self.text_input_buffer) > 0:
                    self.text_input_buffer = self.text_input_buffer[:-1]
                return {
                    "action": GameAction.NONE,
                    "text_buffer": self.text_input_buffer
                }
            elif key == tcod.event.K_RETURN:
                # Confirm text input
                text = self.text_input_buffer
                self.set_mode(InputMode.NORMAL)
                if self.text_input_callback:
                    self.text_input_callback(text)
                return {
                    "action": GameAction.CONFIRM,
                    "text": text
                }
            elif key == tcod.event.K_ESCAPE:
                # Cancel text input
                self.set_mode(InputMode.NORMAL)
                return {"action": GameAction.CANCEL}
            elif key == tcod.event.K_TAB:
                # Tab key (could be used for autocomplete)
                return {
                    "action": GameAction.NONE,
                    "key": "tab",
                    "text_buffer": self.text_input_buffer
                }
            elif event.mod & tcod.event.KMOD_CTRL:
                # Ctrl key combinations
                if key == tcod.event.K_v:
                    # Implement paste functionality if needed
                    return {
                        "action": GameAction.NONE,
                        "key": "paste",
                        "text_buffer": self.text_input_buffer
                    }
            elif not (event.mod & tcod.event.KMOD_ALT) and event.ch:
                # Regular character input
                self.text_input_buffer += event.ch
                return {
                    "action": GameAction.NONE,
                    "text_buffer": self.text_input_buffer
                }
        
        # Look up the key in the current mode's mapping
        current_mapping = self.key_mappings.get(self.current_mode, {})
        
        # Check for mapped action
        if key in current_mapping:
            action = current_mapping[key]
            
            # For movement actions, include the direction
            if action in (
                GameAction.MOVE_UP, GameAction.MOVE_DOWN,
                GameAction.MOVE_LEFT, GameAction.MOVE_RIGHT,
                GameAction.MOVE_UP_LEFT, GameAction.MOVE_UP_RIGHT,
                GameAction.MOVE_DOWN_LEFT, GameAction.MOVE_DOWN_RIGHT
            ):
                direction_map = {
                    GameAction.MOVE_UP: "up",
                    GameAction.MOVE_DOWN: "down",
                    GameAction.MOVE_LEFT: "left",
                    GameAction.MOVE_RIGHT: "right",
                    GameAction.MOVE_UP_LEFT: "up_left",
                    GameAction.MOVE_UP_RIGHT: "up_right",
                    GameAction.MOVE_DOWN_LEFT: "down_left",
                    GameAction.MOVE_DOWN_RIGHT: "down_right"
                }
                direction = direction_map.get(action)
                return {"action": action, "direction": direction}
            
            # For rotation actions, include the direction
            elif action in (GameAction.ROTATE_CLOCKWISE, GameAction.ROTATE_COUNTERCLOCKWISE):
                return {
                    "action": action,
                    "direction": "clockwise" if action == GameAction.ROTATE_CLOCKWISE else "counterclockwise"
                }
            
            # For other actions, just return the action
            return {"action": action}
        
        # No mapping found
        return {"action": GameAction.NONE}
    
    def get_mouse_position(self):
        """
        Get the current mouse position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return self.mouse