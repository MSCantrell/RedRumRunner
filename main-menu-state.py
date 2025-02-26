import tcod
import tcod.event as event
from src.states.state import State

class MainMenuState(State):
    """
    Main menu state.
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.menu_items = [
            "New Game",
            "Load Game",
            "Options",
            "Quit"
        ]
        self.selected_item = 0
    
    def enter(self):
        super().enter()
        self.logger.info("Entered main menu")
    
    def exit(self):
        super().exit()
        self.logger.info("Exited main menu")
    
    def update(self, delta_time):
        # Any animation or background updates
        pass
    
    def render(self, console):
        # Clear console
        console.clear()
        
        # Draw title
        title = "RedRumRunner"
        version = f"v{self.game_state.game_version}"
        
        console.print(
            console.width // 2,
            console.height // 4,
            title,
            fg=(255, 0, 0),
            bg=None,
            alignment=tcod.CENTER
        )
        
        console.print(
            console.width // 2,
            console.height // 4 + 2,
            version,
            fg=(200, 200, 200),
            bg=None,
            alignment=tcod.CENTER
        )
        
        # Draw menu items
        for i, item in enumerate(self.menu_items):
            fg = (255, 255, 255) if i == self.selected_item else (150, 150, 150)
            console.print(
                console.width // 2,
                console.height // 2 + i * 2,
                item,
                fg=fg,
                bg=None,
                alignment=tcod.CENTER
            )
        
        # Draw footer
        console.print(
            console.width // 2,
            console.height - 3,
            "Up/Down: Select | Enter: Confirm | Esc: Quit",
            fg=(150, 150, 150),
            bg=None,
            alignment=tcod.CENTER
        )
    
    def handle_event(self, evt):
        # Process input
        if isinstance(evt, event.KeyDown):
            # Menu navigation
            if evt.sym == event.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                return True
                
            elif evt.sym == event.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                return True
                
            # Selection
            elif evt.sym == event.K_RETURN:
                self._handle_selection()
                return True
                
            # Quit
            elif evt.sym == event.K_ESCAPE:
                raise SystemExit()
                
        return False
    
    def _handle_selection(self):
        """Handle menu item selection."""
        selection = self.menu_items[self.selected_item]
        
        if selection == "New Game":
            # Create a new game
            self.game_state.create_new_game()
            self.transition_to("world_map")
            
        elif selection == "Load Game":
            # Would normally show a load game screen
            # For testing just try to load "save1"
            loaded_state = self.game_state.load_game("save1")
            if loaded_state:
                self.game_state = loaded_state
                self.transition_to("world_map")
            else:
                self.logger.warning("Failed to load game")
                
        elif selection == "Options":
            # Would normally transition to options screen
            self.logger.info("Options selected (not implemented)")
            
        elif selection == "Quit":
            raise SystemExit()
