import json
import pickle
import logging
from datetime import datetime
import os

# This will be imported once implemented
# from src.engine.hex_grid import HexGrid
# from src.engine.calendar import Calendar

class GameState:
    """
    Stores the entire game state, including the world, player, time, etc.
    """
    def __init__(self):
        self.world_grid = None  # HexGrid instance for the world
        self.player_fleet = []  # List of ships in the player's fleet
        self.player_resources = {}  # Dictionary of player resources
        self.calendar = None  # Game time tracking (will be Calendar instance)
        self.authority_awareness = 0.0  # Authority awareness level (0.0 - 1.0)
        self.discovered_locations = set()  # Set of discovered location coordinates
        self.quests = []  # List of active quests
        self.game_version = "0.1.0"  # Version for save compatibility
        self.seed = None  # World generation seed
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def create_new_game(self, seed=None):
        """
        Initialize a new game state with a fresh world.
        
        Args:
            seed (int, optional): Seed for world generation.
        """
        import random
        self.seed = seed if seed is not None else random.randint(0, 999999)
        
        # Initialize empty world (will be filled by world generator)
        # self.world_grid = HexGrid()
        
        # Initialize player resources
        self.player_resources = {
            "gold": 100,
            "food": 50,
            "water": 50,
            "rum": 10,
            "ammunition": 20
        }
        
        # Create a test fleet for development
        self.player_fleet = [
            {"name": "The Dreadnought", "type": "Sloop", "condition": "Good", "crew": 15},
        ]
        
        # Reset calendar (will implement Calendar class later)
        # self.calendar = Calendar()
        # self.calendar.reset()
        
        # Reset authority awareness
        self.authority_awareness = 0.05  # Start with a small amount
        
        self.logger.info(f"Created new game with seed {self.seed}")
        
    def update(self, delta_time):
        """
        Update the game state.
        
        Args:
            delta_time (float): Time since last update.
        """
        # Update any time-based events, NPCs, etc.
        pass
        
    def validate(self):
        """
        Validate the game state for consistency.
        
        Returns:
            bool: True if state is valid, False otherwise.
        """
        is_valid = True
        
        # Check world grid exists
        if self.world_grid is None:
            self.logger.warning("World grid is None")
            
        # Check player has at least one ship
        if not self.player_fleet:
            self.logger.warning("Player has no ships")
            
        # Check calendar is initialized
        if self.calendar is None:
            self.logger.warning("Calendar is None")
            
        return is_valid
        
    def save_game(self, filename):
        """
        Save the game state to a file.
        
        Args:
            filename (str): Name of the save file.
            
        Returns:
            bool: True if save was successful, False otherwise.
        """
        save_dir = os.path.join(os.getcwd(), 'saves')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{filename}.save")
        
        try:
            # Create a backup if file exists
            if os.path.exists(save_path):
                backup_path = f"{save_path}.bak"
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(save_path, backup_path)
            
            # Add save metadata
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "game_version": self.game_version,
                "seed": self.seed
            }
            
            with open(save_path, 'wb') as f:
                pickle.dump((save_data, self), f)
                
            self.logger.info(f"Game saved to {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving game: {e}")
            return False
    
    @staticmethod
    def load_game(filename):
        """
        Load a game state from a file.
        
        Args:
            filename (str): Name of the save file.
            
        Returns:
            GameState: Loaded game state or None if load failed.
        """
        logger = logging.getLogger(__name__)
        save_dir = os.path.join(os.getcwd(), 'saves')
        save_path = os.path.join(save_dir, f"{filename}.save")
        
        if not os.path.exists(save_path):
            logger.error(f"Save file {save_path} does not exist")
            return None
            
        try:
            with open(save_path, 'rb') as f:
                save_data, game_state = pickle.load(f)
                
            logger.info(f"Game loaded from {save_path}, version {save_data['game_version']}")
            
            # Perform version compatibility check if needed
            current_version = "0.1.0"
            if save_data["game_version"] != current_version:
                logger.warning(f"Save version mismatch: {save_data['game_version']} vs {current_version}")
                
            if not game_state.validate():
                logger.warning("Loaded game state validation failed")
                
            return game_state
            
        except Exception as e:
            logger.error(f"Error loading game: {e}")
            
            # Try to load backup if it exists
            backup_path = f"{save_path}.bak"
            if os.path.exists(backup_path):
                logger.info("Attempting to load backup save")
                try:
                    with open(backup_path, 'rb') as f:
                        save_data, game_state = pickle.load(f)
                    return game_state
                except Exception as backup_e:
                    logger.error(f"Error loading backup: {backup_e}")
                    
            return None
    
    def to_json(self):
        """
        Convert game state to JSON for easier debugging or modding.
        
        Returns:
            str: JSON representation of the game state.
        """
        try:
            # Create a dictionary of serializable data
            state_dict = {
                "game_version": self.game_version,
                "seed": self.seed,
                "player_resources": self.player_resources,
                "authority_awareness": self.authority_awareness,
                "discovered_locations": list(self.discovered_locations),
                # Add other serializable properties
            }
            
            # Convert calendar to dict
            if self.calendar:
                state_dict["calendar"] = self.calendar.to_dict()
                
            # Complex objects require custom serialization
            # For example, world grid would need a to_dict method
            
            return json.dumps(state_dict, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error converting game state to JSON: {e}")
            return "{}"
    
    @staticmethod
    def from_json(json_str):
        """
        Create a game state from JSON.
        
        Args:
            json_str (str): JSON representation of the game state.
            
        Returns:
            GameState: Game state from JSON or None if conversion failed.
        """
        logger = logging.getLogger(__name__)
        try:
            state_dict = json.loads(json_str)
            
            game_state = GameState()
            game_state.game_version = state_dict.get("game_version", "0.1.0")
            game_state.seed = state_dict.get("seed")
            game_state.player_resources = state_dict.get("player_resources", {})
            game_state.authority_awareness = state_dict.get("authority_awareness", 0.0)
            game_state.discovered_locations = set(state_dict.get("discovered_locations", []))
            
            # Recreate calendar
            if "calendar" in state_dict:
                game_state.calendar = Calendar.from_dict(state_dict["calendar"])
                
            # Complex objects require custom deserialization
                
            return game_state
            
        except Exception as e:
            logger.error(f"Error creating game state from JSON: {e}")
            return None
