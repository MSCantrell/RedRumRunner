import tcod
import tcod.event as event
from src.states.state import State

class PortInterfaceState(State):
    """
    Port interface state - for trading and port interactions.
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.port_name = "Test Port"  # Would come from actual port data
        self.selected_tab = "Trade"
        self.tabs = ["Trade", "Shipyard", "Tavern", "Warehouse"]
    
    def enter(self):
        super().enter()
        self.logger.info(f"Entered port interface at {self.port_name}")
    
    def exit(self):
        super().exit()
        self.logger.info("Exited port interface")
    
    def update(self, delta_time):
        # Update port-related entities
        pass
    
    def render(self, console):
        # Clear console
        console.clear()
        
        # Draw port name
        console.print(
            console.width // 2,
            2,
            f"Port: {self.port_name}",
            fg=(255, 255, 0),
            bg=None,
            alignment=tcod.CENTER
        )
        
        # Draw tabs
        for i, tab in enumerate(self.tabs):
            x = console.width // len(self.tabs) * i + console.width // (len(self.tabs) * 2)
            y = 5
            fg = (255, 255, 255) if tab == self.selected_tab else (150, 150, 150)
            
            console.print(
                x,
                y,
                tab,
                fg=fg,
                bg=None,
                alignment=tcod.CENTER
            )
        
        # Draw tab content
        if self.selected_tab == "Trade":
            self._render_trade_tab(console)
        elif self.selected_tab == "Shipyard":
            self._render_shipyard_tab(console)
        elif self.selected_tab == "Tavern":
            self._render_tavern_tab(console)
        elif self.selected_tab == "Warehouse":
            self._render_warehouse_tab(console)
        
        # Draw resources
        resources_text = "Your Resources: "
        for resource, amount in self.game_state.player_resources.items():
            resources_text += f"{resource}: {amount} | "
        
        console.print(
            console.width // 2,
            console.height - 5,
            resources_text[:-3],  # Remove last " | "
            fg=(100, 200, 100),
            bg=None,
            alignment=tcod.CENTER
        )
        
        # Draw available commands
        console.print(
            console.width // 2,
            console.height - 3,
            "Tab: Switch Tab | W: World Map | Esc: Back",
            fg=(150, 150, 150),
            bg=None,
            alignment=tcod.CENTER
        )
    
    def _render_trade_tab(self, console):
        """Render the trade tab content."""
        console.print(
            console.width // 2,
            10,
            "Available Goods for Trade",
            fg=(200, 200, 200),
            bg=None,
            alignment=tcod.CENTER
        )
        
        # List of goods (would be actual port inventory)
        goods = [
            {"name": "Food", "price": 10, "available": 100},
            {"name": "Water", "price": 5, "available": 200},
            {"name": "Rum", "price": 20, "available": 50},
            {"name": "Ammunition", "price": 15, "available": 30},
        ]
        
        for i, good in enumerate(goods):
            y = 12 + i * 2
            console.print(
                console.width // 4,
                y,
                good["name"],
                fg=(255, 255, 255),
                bg=None
            )
            
            console.print(
                console.width // 2,
                y,
                f"Price: {good['price']} gold",
                fg=(255, 255, 0),
                bg=None
            )
            
            console.print(
                3 * console.width // 4,
                y,
                f"Available: {good['available']}",
                fg=(150, 150, 150),
                bg=None
            )
    
    def _render_shipyard_tab(self, console):
        """Render the shipyard tab content."""
        console.print(
            console.width // 2,
            10,
            "Available Ships",
            fg=(200, 200, 200),
            bg=None,
            alignment=tcod.CENTER
        )
        
        # List of ships (would be actual shipyard inventory)
        ships = [
            {"name": "Sloop", "price": 1000, "speed": "Fast", "cargo": "Small"},
            {"name": "Brigantine", "price": 2500, "speed": "Medium", "cargo": "Medium"},
            {"name": "Galleon", "price": 5000, "speed": "Slow", "cargo": "Large"},
        ]
        
        for i, ship in enumerate(ships):
            y = 12 + i * 3
            console.print(
                console.width // 4,
                y,
                ship["name"],
                fg=(255, 255, 255),
                bg=None
            )
            
            console.print(
                console.width // 2,
                y,
                f"Price: {ship['price']} gold",
                fg=(255, 255, 0),
                bg=None
            )
            
            console.print(
                console.width // 4,
                y + 1,
                f"Speed: {ship['speed']} | Cargo: {ship['cargo']}",
                fg=(150, 150, 150),
                bg=None
            )
    
    def _render_tavern_tab(self, console):
        """Render the tavern tab content."""
        console.print(
            console.width // 2,
            10,
            "Tavern - Hire Crew & Gather Rumors",
            fg=(200, 200, 200),
            bg=None,
            alignment=tcod.CENTER
        )
        
        console.print(
            console.width // 2,
            15,
            "Available Crew Members",
            fg=(200, 200, 100),
            bg=None,
            alignment=tcod.CENTER
        )
        
        console.print(
            console.width // 2,
            20,
            "Current Rumors",
            fg=(200, 100, 200),
            bg=None,
            alignment=tcod.CENTER
        )
        
        console.print(
            console.width // 2,
            22,
            "\"There's talk of a merchant fleet heading east...\"",
            fg=(150, 150, 150),
            bg=None,
            alignment=tcod.CENTER
        )
    
    def _render_warehouse_tab(self, console):
        """Render the warehouse tab content."""
        console.print(
            console.width // 2,
            10,
            "Warehouse - Stored Goods",
            fg=(200, 200, 200),
            bg=None,
            alignment=tcod.CENTER
        )
        
        console.print(
            console.width // 2,
            15,
            "You have no goods stored at this port.",
            fg=(150, 150, 150),
            bg=None,
            alignment=tcod.CENTER
        )
    
    def handle_event(self, evt):
        # Process input
        if isinstance(evt, event.KeyDown):
            # Tab switching
            if evt.sym == event.K_TAB:
                current_index = self.tabs.index(self.selected_tab)
                next_index = (current_index + 1) % len(self.tabs)
                self.selected_tab = self.tabs[next_index]
                return True
            
            # Return to world map
            elif evt.sym == event.K_w:
                self.transition_to("world_map")
                return True
                
            # Back/Escape
            elif evt.sym == event.K_ESCAPE:
                self.transition_to("world_map")
                return True
                
        return False
