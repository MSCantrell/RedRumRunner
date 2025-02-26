import tcod
import tcod.event as event
import random
from src.states.state import State

class CombatState(State):
    """
    Combat state - handles ship-to-ship combat.
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.enemy_ships = []
        self.player_ships = []
        self.current_ship_index = 0
        self.current_action = None
        self.combat_log = []
        self.turn = 0
        self.phase = "player"  # "player" or "enemy"
        self.selected_target = 0
        self.camera_offset = [0, 0]
    
    def enter(self):
        super().enter()
        self.logger.info("Entered combat state")
        
        # Set up combat
        self._initialize_combat()
    
    def exit(self):
        super().exit()
        self.logger.info("Exited combat state")
    
    def _initialize_combat(self):
        """Initialize the combat scenario."""
        # Reset combat state
        self.combat_log = []
        self.turn = 1
        self.phase = "player"
        self.selected_target = 0
        self.camera_offset = [0, 0]
        
        # Create player ships from fleet
        self.player_ships = []
        for ship in self.game_state.player_fleet:
            combat_ship = {
                "name": ship["name"],
                "type": ship["type"],
                "condition": ship["condition"],
                "crew": ship["crew"],
                "hull": 100,
                "sails": 100,
                "position": (0, 0),  # Will be set properly
                "orientation": 0,    # 0-5 for hex directions
                "has_acted": False
            }
            self.player_ships.append(combat_ship)
        
        # Create enemy ships (placeholder for now)
        self.enemy_ships = []
        enemy_types = ["Sloop", "Brigantine", "Frigate"]
        enemy_names = ["Bounty Hunter", "Royal Guard", "Sea Serpent", "Thunder"]
        
        num_enemies = min(len(self.game_state.player_fleet) + random.randint(0, 1), 3)
        
        for i in range(num_enemies):
            ship_type = random.choice(enemy_types)
            name = f"The {random.choice(enemy_names)}"
            
            enemy_ship = {
                "name": name,
                "type": ship_type,
                "condition": "Good",
                "crew": 15 + random.randint(0, 10),
                "hull": 100,
                "sails": 100,
                "position": (10, i * 3),  # Will be adjusted
                "orientation": 3,         # Facing player
                "has_acted": False
            }
            self.enemy_ships.append(enemy_ship)
        
        # Position player ships
        for i, ship in enumerate(self.player_ships):
            ship["position"] = (2, i * 3)
        
        # Log combat start
        self._add_to_log(f"Combat begins! {len(self.player_ships)} ships vs {len(self.enemy_ships)} enemy vessels.")
        self._add_to_log("Player's turn. Select a ship and action.")
    
    def update(self, delta_time):
        # Handle any automatic updates
        pass
    
    def render(self, console):
        # Clear console
        console.clear()
        
        # Draw combat header
        turn_text = f"Turn: {self.turn} - {self.phase.capitalize()} Phase"
        console.print(
            console.width // 2,
            1,
            turn_text,
            fg=(255, 255, 0),
            bg=None,
            alignment=tcod.CENTER
        )
        
        # Draw tactical grid (placeholder)
        grid_width = 60
        grid_height = 30
        grid_x = (console.width - grid_width) // 2
        grid_y = 5
        
        # Draw grid outline
        for x in range(grid_width):
            console.print(grid_x + x, grid_y, "─", fg=(50, 50, 100))
            console.print(grid_x + x, grid_y + grid_height, "─", fg=(50, 50, 100))
        
        for y in range(grid_height):
            console.print(grid_x, grid_y + y, "│", fg=(50, 50, 100))
            console.print(grid_x + grid_width, grid_y + y, "│", fg=(50, 50, 100))
        
        # Draw corners
        console.print(grid_x, grid_y, "┌", fg=(50, 50, 100))
        console.print(grid_x + grid_width, grid_y, "┐", fg=(50, 50, 100))
        console.print(grid_x, grid_y + grid_height, "└", fg=(50, 50, 100))
        console.print(grid_x + grid_width, grid_y + grid_height, "┘", fg=(50, 50, 100))
        
        # Draw player ships
        for i, ship in enumerate(self.player_ships):
            x = grid_x + 5 + ship["position"][0] - self.camera_offset[0]
            y = grid_y + 5 + ship["position"][1] - self.camera_offset[1]
            
            # Ship representation depends on type and orientation
            ship_char = "P"  # Placeholder
            fg_color = (0, 0, 255)  # Blue for player
            
            # Highlight current ship
            if self.phase == "player" and i == self.current_ship_index:
                fg_color = (100, 200, 255)
                
            # Show damaged ships differently
            if ship["hull"] < 50:
                fg_color = (100, 100, 200)
            
            console.print(
                x,
                y,
                ship_char,
                fg=fg_color,
                bg=None
            )
            
            # Show ship name
            if self.phase == "player" and i == self.current_ship_index:
                console.print(
                    x,
                    y - 1,
                    ship["name"],
                    fg=(100, 200, 255),
                    bg=None
                )
        
        # Draw enemy ships
        for i, ship in enumerate(self.enemy_ships):
            x = grid_x + 5 + ship["position"][0] - self.camera_offset[0]
            y = grid_y + 5 + ship["position"][1] - self.camera_offset[1]
            
            # Ship representation
            ship_char = "E"  # Placeholder
            fg_color = (255, 0, 0)  # Red for enemy
            
            # Highlight targeted enemy
            if self.phase == "player" and i == self.selected_target:
                fg_color = (255, 200, 100)
                
            # Show damaged ships differently
            if ship["hull"] < 50:
                fg_color = (200, 100, 100)
            
            console.print(
                x,
                y,
                ship_char,
                fg=fg_color,
                bg=None
            )
            
            # Show ship name for targeted enemy
            if self.phase == "player" and i == self.selected_target:
                console.print(
                    x,
                    y - 1,
                    ship["name"],
                    fg=(255, 200, 100),
                    bg=None
                )
        
        # Draw wind indicator (placeholder)
        wind_dir = "→"  # Placeholder
        console.print(
            grid_x + grid_width - 10,
            grid_y + 2,
            f"Wind: {wind_dir}",
            fg=(150, 150, 255),
            bg=None
        )
        
        # Draw combat log
        log_x = 5
        log_y = grid_y + grid_height + 2
        log_width = console.width - 10
        log_height = 7
        
        # Draw log border
        for x in range(log_width):
            console.print(log_x + x, log_y, "─", fg=(100, 100, 100))
            console.print(log_x + x, log_y + log_height, "─", fg=(100, 100, 100))
        
        for y in range(log_height):
            console.print(log_x, log_y + y, "│", fg=(100, 100, 100))
            console.print(log_x + log_width, log_y + y, "│", fg=(100, 100, 100))
        
        # Draw corners
        console.print(log_x, log_y, "┌", fg=(100, 100, 100))
        console.print(log_x + log_width, log_y, "┐", fg=(100, 100, 100))
        console.print(log_x, log_y + log_height, "└", fg=(100, 100, 100))
        console.print(log_x + log_width, log_y + log_height, "┘", fg=(100, 100, 100))
        
        # Draw log title
        console.print(
            log_x + 2,
            log_y,
            "Combat Log",
            fg=(200, 200, 100),
            bg=None
        )
        
        # Draw log entries (most recent first)
        visible_log = self.combat_log[-log_height+1:] if len(self.combat_log) > log_height-1 else self.combat_log
        for i, entry in enumerate(visible_log):
            console.print(
                log_x + 2,
                log_y + i + 1,
                entry,
                fg=(200, 200, 200),
                bg=None
            )
        
        # Draw actions menu if it's player's turn
        if self.phase == "player":
            actions_x = grid_x + grid_width + 2
            actions_y = grid_y
            actions_width = console.width - actions_x - 2
            
            console.print(
                actions_x,
                actions_y,
                "Actions",
                fg=(255, 255, 0),
                bg=None
            )
            
            actions = [
                "Move",
                "Fire Cannons",
                "Prepare to Board",
                "Evasive Maneuvers",
                "Intimidate",
                "End Turn"
            ]
            
            for i, action in enumerate(actions):
                fg = (255, 255, 255) if action == self.current_action else (150, 150, 150)
                
                console.print(
                    actions_x,
                    actions_y + i + 2,
                    action,
                    fg=fg,
                    bg=None
                )
            
            # Draw current ship stats
            if self.player_ships:
                ship = self.player_ships[self.current_ship_index]
                stats_y = actions_y + len(actions) + 5
                
                console.print(
                    actions_x,
                    stats_y,
                    "Ship Info",
                    fg=(255, 255, 0),
                    bg=None
                )
                
                console.print(
                    actions_x,
                    stats_y + 2,
                    ship["name"],
                    fg=(200, 200, 255),
                    bg=None
                )
                
                console.print(
                    actions_x,
                    stats_y + 3,
                    f"Type: {ship['type']}",
                    fg=(200, 200, 200),
                    bg=None
                )
                
                console.print(
                    actions_x,
                    stats_y + 4,
                    f"Hull: {ship['hull']}%",
                    fg=(200, 200, 200),
                    bg=None
                )
                
                console.print(
                    actions_x,
                    stats_y + 5,
                    f"Sails: {ship['sails']}%",
                    fg=(200, 200, 200),
                    bg=None
                )
                
                console.print(
                    actions_x,
                    stats_y + 6,
                    f"Crew: {ship['crew']}",
                    fg=(200, 200, 200),
                    bg=None
                )
        
        # Draw commands
        commands_text = "Space: Select Action | Tab: Next Ship | T: Select Target | Esc: Retreat"
        console.print(
            console.width // 2,
            console.height - 2,
            commands_text,
            fg=(150, 150, 150),
            bg=None,
            alignment=tcod.CENTER
        )
    
    def handle_event(self, evt):
        # Process input
        if isinstance(evt, event.KeyDown):
            # Navigation
            if evt.sym == event.K_UP:
                self.camera_offset[1] -= 1
                return True
                
            elif evt.sym == event.K_DOWN:
                self.camera_offset[1] += 1
                return True
                
            elif evt.sym == event.K_LEFT:
                self.camera_offset[0] -= 1
                return True
                
            elif evt.sym == event.K_RIGHT:
                self.camera_offset[0] += 1
                return True
            
            # Combat controls
            if self.phase == "player":
                # Next ship
                if evt.sym == event.K_TAB:
                    self._cycle_ship()
                    return True
                
                # Select target
                elif evt.sym == event.K_t:
                    if self.enemy_ships:
                        self.selected_target = (self.selected_target + 1) % len(self.enemy_ships)
                    return True
                
                # Select/execute action
                elif evt.sym == event.K_SPACE:
                    if self.current_action:
                        self._execute_action()
                    else:
                        self.current_action = "Move"  # Default action
                    return True
                
                # Cycle through actions
                elif evt.sym == event.K_a:
                    self._cycle_action()
                    return True
            
            # End turn
            elif evt.sym == event.K_e:
                if self.phase == "player":
                    self._end_player_turn()
                return True
            
            # Retreat/exit combat
            elif evt.sym == event.K_ESCAPE:
                self._attempt_retreat()
                return True
                
        return False
    
    def _cycle_ship(self):
        """Cycle to the next player ship that hasn't acted."""
        if not self.player_ships:
            return
        
        start_index = self.current_ship_index
        while True:
            self.current_ship_index = (self.current_ship_index + 1) % len(self.player_ships)
            
            # If we've checked all ships, break
            if self.current_ship_index == start_index:
                break
                
            # If this ship hasn't acted, select it
            if not self.player_ships[self.current_ship_index]["has_acted"]:
                break
        
        # Reset current action when switching ships
        self.current_action = None
    
    def _cycle_action(self):
        """Cycle through available actions."""
        actions = [
            "Move",
            "Fire Cannons",
            "Prepare to Board",
            "Evasive Maneuvers",
            "Intimidate",
            "End Turn"
        ]
        
        if self.current_action is None:
            self.current_action = actions[0]
        else:
            current_index = actions.index(self.current_action)
            self.current_action = actions[(current_index + 1) % len(actions)]
    
    def _execute_action(self):
        """Execute the currently selected action."""
        if not self.player_ships or not self.current_action:
            return
        
        ship = self.player_ships[self.current_ship_index]
        
        if ship["has_acted"]:
            self._add_to_log(f"{ship['name']} has already acted this turn.")
            return
        
        # Handle different actions
        if self.current_action == "Move":
            self._add_to_log(f"{ship['name']} moves.")
            ship["position"] = (ship["position"][0] + 2, ship["position"][1])
            
        elif self.current_action == "Fire Cannons":
            if not self.enemy_ships:
                self._add_to_log("No enemy ships to target!")
                return
                
            target = self.enemy_ships[self.selected_target]
            damage = random.randint(5, 20)
            target["hull"] -= damage
            
            self._add_to_log(f"{ship['name']} fires cannons at {target['name']}!")
            self._add_to_log(f"  Dealt {damage} damage to {target['name']}'s hull.")
            
            # Check if target is destroyed
            if target["hull"] <= 0:
                self._add_to_log(f"{target['name']} has been sunk!")
                self.enemy_ships.pop(self.selected_target)
                self.selected_target = min(self.selected_target, len(self.enemy_ships) - 1) if self.enemy_ships else 0
                
                # Check for victory
                if not self.enemy_ships:
                    self._combat_victory()
                    return
            
        elif self.current_action == "Prepare to Board":
            self._add_to_log(f"{ship['name']} prepares to board.")
            
        elif self.current_action == "Evasive Maneuvers":
            self._add_to_log(f"{ship['name']} performs evasive maneuvers.")
            
        elif self.current_action == "Intimidate":
            if not self.enemy_ships:
                self._add_to_log("No enemy ships to intimidate!")
                return
                
            target = self.enemy_ships[self.selected_target]
            success = random.random() < 0.3  # 30% chance
            
            self._add_to_log(f"{ship['name']} attempts to intimidate {target['name']}!")
            
            if success:
                self._add_to_log(f"  {target['name']} is intimidated and surrenders!")
                self.enemy_ships.pop(self.selected_target)
                self.selected_target = min(self.selected_target, len(self.enemy_ships) - 1) if self.enemy_ships else 0
                
                # Add to player fleet
                self.game_state.player_fleet.append({
                    "name": target["name"],
                    "type": target["type"],
                    "condition": "Damaged",
                    "crew": target["crew"] // 2  # Reduced crew for captured ship
                })
                
                # Check for victory
                if not self.enemy_ships:
                    self._combat_victory()
                    return
            else:
                self._add_to_log(f"  {target['name']} stands firm!")
            
        elif self.current_action == "End Turn":
            self._end_player_turn()
            return
        
        # Mark ship as having acted
        ship["has_acted"] = True
        
        # Reset current action
        self.current_action = None
        
        # Move to next ship that hasn't acted
        all_acted = True
        for s in self.player_ships:
            if not s["has_acted"]:
                all_acted = False
                break
                
        if all_acted:
            self._end_player_turn()
        else:
            self._cycle_ship()
    
    def _end_player_turn(self):
        """End the player's turn and start enemy turn."""
        self._add_to_log("Player turn ends. Enemy turn begins.")
        self.phase = "enemy"
        
        # Reset player ships acted status for next turn
        for ship in self.player_ships:
            ship["has_acted"] = False
        
        # Process enemy turn (simplified)
        self._process_enemy_turn()
    
    def _process_enemy_turn(self):
        """Process the enemy turn."""
        if not self.enemy_ships or not self.player_ships:
            self._end_enemy_turn()
            return
            
        for enemy in self.enemy_ships:
            # Simple AI: move toward player and attack
            self._add_to_log(f"{enemy['name']} moves closer.")
            enemy["position"] = (enemy["position"][0] - 1, enemy["position"][1])
            
            # Attack if in range
            if enemy["position"][0] - self.player_ships[0]["position"][0] < 5:
                target_index = random.randint(0, len(self.player_ships) - 1)
                target = self.player_ships[target_index]
                
                damage = random.randint(5, 15)
                target["hull"] -= damage
                
                self._add_to_log(f"{enemy['name']} fires at {target['name']}!")
                self._add_to_log(f"  Dealt {damage} damage to {target['name']}'s hull.")
                
                # Check if target is destroyed
                if target["hull"] <= 0:
                    self._add_to_log(f"{target['name']} has been sunk!")
                    self.player_ships.pop(target_index)
                    self.current_ship_index = min(self.current_ship_index, len(self.player_ships) - 1) if self.player_ships else 0
                    
                    # Check for defeat
                    if not self.player_ships:
                        self._combat_defeat()
                        return
        
        # End enemy turn
        self._end_enemy_turn()
    
    def _end_enemy_turn(self):
        """End the enemy turn and start a new player turn."""
        self.turn += 1
        self.phase = "player"
        self._add_to_log(f"Turn {self.turn} begins. Player's turn.")
    
    def _combat_victory(self):
        """Handle combat victory."""
        self._add_to_log("Victory! All enemy ships have been defeated or captured.")
        
        # Calculate rewards
        gold_reward = random.randint(50, 200)
        self.game_state.player_resources["gold"] = self.game_state.player_resources.get("gold", 0) + gold_reward
        
        self._add_to_log(f"Gained {gold_reward} gold from the battle.")
        self._add_to_log("Press ESC to return to the world map.")
    
    def _combat_defeat(self):
        """Handle combat defeat."""
        self._add_to_log("Defeat! All your ships have been lost.")
        
        # In a real game, this might lead to game over or special handling
        self._add_to_log("Press ESC to return to the world map.")
    
    def _attempt_retreat(self):
        """Attempt to retreat from combat."""
        # In a full implementation, this would have a chance to fail
        # and might incur penalties
        
        self._add_to_log("Retreating from combat...")
        
        # Return to world map
        self.transition_to("world_map")
    
    def _add_to_log(self, message):
        """Add a message to the combat log."""
        self.combat_log.append(message)
        self.logger.debug(f"Combat log: {message}")
