import tcod
import tcod.event as event
from src.states.state import State

class WorldMapState(State):
    """
    World map state - shows the strategic world view.
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.camera_offset = [0, 0]
        self.cursor_position = [0, 0]
    
    def enter(self):
        super().enter()
        self.logger.info("Entered world map")
    
    def exit(self):
        super().exit()
        self.logger.info("Exited world map")
    
    def update(self, delta_time):
        # Update world entities
        pass
    
    def render(self, console):
        # Clear console
        console.clear()
        
        # Draw world map
        if self.game_state.world_grid:
            # This would use a proper hex renderer
            # For now, just a placeholder
            console.print(
                console.width // 2,
                console.height // 2,
                "WORLD MAP",
                fg=(0, 200, 200),
                bg=None,
                alignment=tcod.CENTER
            )
        else:
            console.print(
                console.width // 2,
                console.height // 2,
                "World Map (placeholder)",
                fg=(0, 200, 200),
                bg=None,
                alignment=tcod.CENTER
            )
        
        # Draw UI elements
        
        # Draw calendar (placeholder for now)
        calendar_text = "Day: 1, Month: 1, Year: 1"
        console.print(
            5,
            5,
            calendar_text,
            fg=(200, 200, 100),
            bg=None
        )
        
        # Draw authority awareness
        awareness_text = f"Authority Awareness: {self.game_state.authority_awareness * 100:.1f}%"
        console.print(
            5,
            7,
            awareness_text,
            fg=(200, 100, 100),
            bg=None
        )
        
        # Draw resources
        resources_text = "Resources: "
        for resource, amount in self.game_state.player_resources.items():
            resources_text += f"{resource}: {amount} | "
        
        console.print(
            5,
            9,
            resources_text[:-3],  # Remove last " | "
            fg=(100, 200, 100),
            bg=None
        )
        
        # Draw ship info
        if self.game_state.player_fleet:
            ship = self.game_state.player_fleet[0]
            ship_text = f"Ship: {ship['name']} ({ship['type']}) - Crew: {ship['crew']}"
            console.print(
                5,
                11,
                ship_text,
                fg=(100, 100, 200),
                bg=None
            )
        
        # Draw available commands
        console.print(
            5,
            console.height - 3,
            "P: Port | F: Fleet | M: Main Menu | S: Save | Esc: Quit",
            fg=(150, 150, 150),
            bg=None
        )
    
    def handle_event(self, evt):
        # Process input
        if isinstance(evt, event.KeyDown):
            # Navigation
            if evt.sym == event.K_UP:
                self.camera_offset[1] -= 10
                return True
                
            elif evt.sym == event.K_DOWN:
                self.camera_offset[1] += 10
                return True
                
            elif evt.sym == event.K_LEFT:
                self.camera_offset[0] -= 10
                return True
                
            elif evt.sym == event.K_RIGHT:
                self.camera_offset[0] += 10
                return True
            
            # State transitions
            elif evt.sym == event.K_p:
                self.transition_to("port_interface")
                return True
                
            elif evt.sym == event.K_f:
                self.transition_to("fleet_management")
                return True
                
            elif evt.sym == event.K_m:
                self.transition_to("main_menu")
                return True
                
            # Game commands
            elif evt.sym == event.K_s:
                self.game_state.save_game("save1")
                return True
                
            # Quit
            elif evt.sym == event.K_ESCAPE:
                raise SystemExit()
                
        return False
