import logging

class State:
    """
    Base class for all game states.
    """
    def __init__(self, game_state):
        """
        Initialize the state.
        
        Args:
            game_state (GameState): The game state to use.
        """
        self.game_state = game_state
        self.state_machine = None  # Set by StateMachine.add_state
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def enter(self):
        """
        Called when this state becomes the active state.
        """
        self.logger.debug("Entered state")
    
    def exit(self):
        """
        Called when this state is no longer the active state.
        """
        self.logger.debug("Exited state")
    
    def update(self, delta_time):
        """
        Update the state.
        
        Args:
            delta_time (float): Time since last update.
        """
        pass
    
    def render(self, console):
        """
        Render the state.
        
        Args:
            console (Console): tcod console to render to.
        """
        pass
    
    def handle_event(self, event):
        """
        Handle an input event.
        
        Args:
            event: Input event to handle.
            
        Returns:
            bool: True if the event was handled, False otherwise.
        """
        return False
    
    def transition_to(self, state_name):
        """
        Transition to another state.
        
        Args:
            state_name (str): Name of the state to transition to.
            
        Returns:
            bool: True if transition was successful, False otherwise.
        """
        if self.state_machine:
            return self.state_machine.set_state(state_name)
        self.logger.error("Cannot transition: no state machine set")
        return False
