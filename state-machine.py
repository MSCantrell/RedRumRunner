import logging

class StateMachine:
    """
    Manages game state transitions between different modes (main menu, world map, combat, etc.)
    """
    def __init__(self, initial_state=None):
        self.states = {}  # Dictionary of available states
        self.current_state = None
        self.logger = logging.getLogger(__name__)
        
        if initial_state:
            self.set_state(initial_state)
    
    def add_state(self, state_name, state_instance):
        """
        Add a state to the state machine.
        
        Args:
            state_name (str): Name of the state.
            state_instance (State): Instance of the state.
        """
        self.states[state_name] = state_instance
        state_instance.state_machine = self
        self.logger.debug(f"Added state: {state_name}")
    
    def set_state(self, state_name):
        """
        Change to a new state.
        
        Args:
            state_name (str): Name of the state to change to.
            
        Returns:
            bool: True if state change was successful, False otherwise.
        """
        if state_name not in self.states:
            self.logger.error(f"Attempted to set unknown state: {state_name}")
            return False
            
        if self.current_state:
            self.current_state.exit()
            
        prev_state = self.current_state.__class__.__name__ if self.current_state else "None"
        self.current_state = self.states[state_name]
        self.logger.info(f"State changed: {prev_state} -> {state_name}")
        
        self.current_state.enter()
        return True
    
    def update(self, delta_time):
        """
        Update the current state.
        
        Args:
            delta_time (float): Time since last update.
        """
        if self.current_state:
            self.current_state.update(delta_time)
    
    def render(self, console):
        """
        Render the current state.
        
        Args:
            console (Console): tcod console to render to.
        """
        if self.current_state:
            self.current_state.render(console)
    
    def handle_event(self, event):
        """
        Handle an input event with the current state.
        
        Args:
            event: Input event to handle.
            
        Returns:
            bool: True if the event was handled, False otherwise.
        """
        if self.current_state:
            return self.current_state.handle_event(event)
        return False
