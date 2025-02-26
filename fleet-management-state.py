import tcod
import tcod.event as event
from src.states.state import State

class FleetManagementState(State):
    """
    Fleet management state - for managing ships and crews.
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.selected_ship_index = 0
        self.selected_tab = "Ships"
        self.tabs = ["Ships", "Crew", "Cargo", "Repairs"]
    
    def enter(self):
        super().enter()
        self.logger.info("Entered fleet management")
        # Ensure we have a valid selected ship
        if self.game_state.player_fleet:
            self.selected_ship_index = min(self.selected_ship_index, len(self.game_state.player_fleet) - 1)
        else:
            self.selected_ship_index = 0
    
    def exit(self):
        super().exit()
        self.logger.info("Exited fleet management")
    
    def update(self, delta_time):
        # Update fleet-related entities
        pass
    
    def render(self, console):
        # Clear console
        console.clear()
        
        # Draw header
        console.print(
            console.width // 2,
            2,
            "Fleet Management",
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
        if self.selected_tab == "Ships":
            self._render_ships_tab(console)
        elif self.selected_tab == "Crew":
            self._render_crew_tab(console)
        elif self.selected_tab == "Cargo":
            self._render_cargo_tab(console)
        elif self.selected_tab == "Repairs":
            self._render_repairs_tab(console)
        
        # Draw footer with available commands
        console.print(
            console.width // 2,
            console.height - 3,
            "Tab: Switch Tab | Up/Down: Select Ship | W: World Map | Esc: Back",
            fg=(150, 150, 150),
            bg=None,
            alignment=tcod.CENTER
        )
    
    def _render_ships_tab(self, console):
        """Render the ships tab content."""
        if not self.game_state.player_fleet:
            console.print(
                console.width // 2,
                15,
                "No ships in your fleet.",
                fg=(150, 150, 150),
                bg=None,
                alignment=tcod.CENTER
            )
            return
        
        # Draw ship list header
        console.print(
            10,
            8,
            "Ship Name",
            fg=(200, 200, 200),
            bg=None
        )
        
        console.print(
            30,
            8,
            "Type",
            fg=(200, 200, 200),
            bg=None
        )
        
        console.print(
            45,
            8,
            "Condition",
            fg=(200, 200, 200),
            bg=None
        )
        
        console.print(
            60,
            8,
            "Crew",
            fg=(200, 200, 200),
            bg=None
        )
        
        # Draw divider
        for x in range(5, console.width - 5):
            console.print(x, 9, "─", fg=(100, 100, 100))
        
        # Draw ships
        for i, ship in enumerate(self.game_state.player_fleet):
            y = 10 + i * 2
            
            # Highlight selected ship
            fg = (255, 255, 255) if i == self.selected_ship_index else (150, 150, 150)
            bg = (30, 30, 50) if i == self.selected_ship_index else None
            
            console.print(
                10,
                y,
                ship["name"],
                fg=fg,
                bg=bg
            )
            
            console.print(
                30,
                y,
                ship["type"],
                fg=fg,
                bg=bg
            )
            
            # Color condition based on status
            condition_color = fg
            if ship["condition"] == "Good":
                condition_color = (100, 255, 100) if i == self.selected_ship_index else (0, 200, 0)
            elif ship["condition"] == "Damaged":
                condition_color = (255, 255, 100) if i == self.selected_ship_index else (200, 200, 0)
            elif ship["condition"] == "Critical":
                condition_color = (255, 100, 100) if i == self.selected_ship_index else (200, 0, 0)
                
            console.print(
                45,
                y,
                ship["condition"],
                fg=condition_color,
                bg=bg
            )
            
            console.print(
                60,
                y,
                str(ship["crew"]),
                fg=fg,
                bg=bg
            )
        
        # Draw selected ship details
        if self.game_state.player_fleet:
            ship = self.game_state.player_fleet[self.selected_ship_index]
            
            # Draw box for ship details
            box_y = 20
            box_height = 10
            
            # Draw top border
            console.print(5, box_y, "┌" + "─" * (console.width - 12) + "┐", fg=(100, 100, 100))
            
            # Draw sides
            for y in range(box_y + 1, box_y + box_height):
                console.print(5, y, "│", fg=(100, 100, 100))
                console.print(console.width - 6, y, "│", fg=(100, 100, 100))
            
            # Draw bottom border
            console.print(5, box_y + box_height, "└" + "─" * (console.width - 12) + "┘", fg=(100, 100, 100))
            
            # Draw ship details
            console.print(
                console.width // 2,
                box_y + 1,
                f"Ship Details: {ship['name']}",
                fg=(255, 255, 0),
                bg=None,
                alignment=tcod.CENTER
            )
            
            details = [
                f"Type: {ship['type']}",
                f"Condition: {ship['condition']}",
                f"Crew: {ship['crew']} sailors",
                f"Hull Strength: 85%",  # Placeholder stats
                f"Sail Condition: 90%",
                f"Speed: Medium",
                f"Firepower: Low"
            ]
            
            for i, detail in enumerate(details):
                console.print(
                    10,
                    box_y + 3 + i,
                    detail,
                    fg=(200, 200, 200),
                    bg=None
                )
    
    def _render_crew_tab(self, console):
        """Render the crew tab content."""
        if not self.game_state.player_fleet:
            console.print(
                console.width // 2,
                15,
                "No ships in your fleet.",
                fg=(150, 150, 150),
                bg=None,
                alignment=tcod.CENTER
            )
            return
        
        ship = self.game_state.player_fleet[self.selected_ship_index]
        
        console.print(
            console.width // 2,
            10,
            f"Crew Management - {ship['name']}",
            fg=(200, 200, 200),
            bg=None,
            alignment=tcod.CENTER
        )
        
        console.print(
            console.width // 2,
            12,
            f"Current Crew: {ship['crew']} sailors",
            fg=(255, 255, 255),
            bg=None,
            alignment=tcod.CENTER
        )
        
        console.print(
            console.width // 2,
            14,
            f"Morale: Good",  # Placeholder
            fg=(100, 255, 100),
            bg=None,
            alignment=tcod.CENTER
        )
        
        console.print(
            console.width // 2,
            16,
            f"Pay Rate: 2 gold per sailor per week",  # Placeholder
            fg=(255, 255, 100),
            bg=None,
            alignment=tcod.CENTER
        )
        
        # Draw officer list (placeholders)
        console.print(
            console.width // 2,
            19,
            "Officers",
            fg=(255, 255, 0),
            bg=None,
            alignment=tcod.CENTER
        )
        
        officers = [
            {"name": "Jack Sparrow", "role": "Captain", "skill": "Expert"},
            {"name": "William Turner", "role": "First Mate", "skill": "Skilled"},
            {"name": "Joshamee Gibbs", "role": "Quartermaster", "skill": "Experienced"}
        ]
        
        for i, officer in enumerate(officers):
            y = 21 + i * 2
            
            console.print(
                20,
                y,
                officer["name"],
                fg=(200, 200, 200),
                bg=None
            )
            
            console.print(
                40,
                y,
                officer["role"],
                fg=(200, 200, 150),
                bg=None
            )
            
            console.print(
                60,
                y,
                officer["skill"],
                fg=(150, 200, 200),
                bg=None
            )
    
    def _render_cargo_tab(self, console):
        """Render the cargo tab content."""
        if not self.game_state.player_fleet:
            console.print(
                console.width // 2,
                15,
                "No ships in your fleet.",
                fg=(150, 150, 150),
                bg=None,
                alignment=tcod.CENTER
            )
            return
        
        ship = self.game_state.player_fleet[self.selected_ship_index]
        
        console.print(
            console.width // 2,
            10,
            f"Cargo - {ship['name']}",
            fg=(200, 200, 200),
            bg=None,
            alignment=tcod.CENTER
        )
        
        console.print(
            console.width // 2,
            12,
            f"Cargo Capacity: 50 tons",  # Placeholder
            fg=(255, 255, 255),
            bg=None,
            alignment=tcod.CENTER
        )
        
        console.print(
            console.width // 2,
            14,
            f"Current Load: 35 tons",  # Placeholder
            fg=(255, 255, 100),
            bg=None,
            alignment=tcod.CENTER
        )
        
        # Draw cargo list (using player resources as placeholder)
        cargo_items = [
            {"name": "Food", "amount": self.game_state.player_resources.get("food", 0), "unit": "barrels"},
            {"name": "Water", "amount": self.game_state.player_resources.get("water", 0), "unit": "barrels"},
            {"name": "Rum", "amount": self.game_state.player_resources.get("rum", 0), "unit": "casks"},
            {"name": "Ammunition", "amount": self.game_state.player_resources.get("ammunition", 0), "unit": "crates"}
        ]
        
        console.print(
            15,
            18,
            "Cargo Item",
            fg=(200, 200, 200),
            bg=None
        )
        
        console.print(
            40,
            18,
            "Amount",
            fg=(200, 200, 200),
            bg=None
        )
        
        console.print(
            55,
            18,
            "Weight",
            fg=(200, 200, 200),
            bg=None
        )
        
        # Draw divider
        for x in range(10, console.width - 10):
            console.print(x, 19, "─", fg=(100, 100, 100))
        
        for i, item in enumerate(cargo_items):
            y = 21 + i * 2
            
            console.print(
                15,
                y,
                item["name"],
                fg=(200, 200, 200),
                bg=None
            )
            
            console.print(
                40,
                y,
                f"{item['amount']} {item['unit']}",
                fg=(200, 200, 150),
                bg=None
            )
            
            # Placeholder weights
            weights = {"Food": 2, "Water": 3, "Rum": 1, "Ammunition": 2}
            weight = weights.get(item["name"], 1) * item["amount"]
            
            console.print(
                55,
                y,
                f"{weight} tons",
                fg=(150, 200, 200),
                bg=None
            )
    
    def _render_repairs_tab(self, console):
        """Render the repairs tab content."""
        if not self.game_state.player_fleet:
            console.print(
                console.width // 2,
                15,
                "No ships in your fleet.",
                fg=(150, 150, 150),
                bg=None,
                alignment=tcod.CENTER
            )
            return
        
        ship = self.game_state.player_fleet[self.selected_ship_index]
        
        console.print(
            console.width // 2,
            10,
            f"Repairs - {ship['name']}",
            fg=(200, 200, 200),
            bg=None,
            alignment=tcod.CENTER
        )
        
        # Condition affects available repairs
        if ship["condition"] == "Good":
            console.print(
                console.width // 2,
                15,
                "This ship is in good condition and doesn't need repairs.",
                fg=(100, 255, 100),
                bg=None,
                alignment=tcod.CENTER
            )
        else:
            console.print(
                console.width // 2,
                15,
                f"Ship Condition: {ship['condition']}",
                fg=(255, 200, 100),
                bg=None,
                alignment=tcod.CENTER
            )
            
            repairs = [
                {"name": "Hull Repairs", "cost": 50, "time": 2, "effect": "+20% Hull Integrity"},
                {"name": "Sail Replacement", "cost": 30, "time": 1, "effect": "+15% Speed"},
                {"name": "Cannon Maintenance", "cost": 40, "time": 1, "effect": "+10% Firepower"}
            ]
            
            for i, repair in enumerate(repairs):
                y = 18 + i * 3
                
                console.print(
                    20,
                    y,
                    repair["name"],
                    fg=(255, 255, 255),
                    bg=None
                )
                
                console.print(
                    20,
                    y + 1,
                    f"Cost: {repair['cost']} gold | Time: {repair['time']} days | Effect: {repair['effect']}",
                    fg=(150, 150, 150),
                    bg=None
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
            
            # Ship selection
            elif evt.sym == event.K_UP:
                if self.game_state.player_fleet:
                    self.selected_ship_index = (self.selected_ship_index - 1) % len(self.game_state.player_fleet)
                return True
                
            elif evt.sym == event.K_DOWN:
                if self.game_state.player_fleet:
                    self.selected_ship_index = (self.selected_ship_index + 1) % len(self.game_state.player_fleet)
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
