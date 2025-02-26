import os
import sys
import unittest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.engine.game_state import GameState
from src.engine.calendar import Calendar
from src.utils.state_validator import StateValidator

class TestGameState(unittest.TestCase):
    """Test cases for GameState class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game_state = GameState()
        self.game_state.calendar = Calendar()
        self.validator = StateValidator()
    
    def test_create_new_game(self):
        """Test creating a new game."""
        self.game_state.create_new_game(seed=12345)
        
        self.assertEqual(self.game_state.seed, 12345)
        self.assertGreater(len(self.game_state.player_fleet), 0)
        self.assertGreater(self.game_state.player_resources.get("gold", 0), 0)
        self.assertGreater(self.game_state.authority_awareness, 0)
    
    def test_validation_valid_state(self):
        """Test validation with a valid state."""
        self.game_state.create_new_game(seed=12345)
        
        # Create schemas first
        StateValidator.create_default_schemas()
        
        # Validate
        valid, errors = self.validator.validate_game_state(self.game_state)
        self.assertTrue(valid, f"Validation failed with errors: {errors}")
    
    def test_validation_invalid_state(self):
        """Test validation with an invalid state."""
        self.game_state.create_new_game(seed=12345)
        
        # Create schemas first
        StateValidator.create_default_schemas()
        
        # Introduce an error - invalid authority awareness
        self.game_state.authority_awareness = -0.5  # Invalid value
        
        # Validate
        valid, errors = self.validator.validate_game_state(self.game_state)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_serialization(self):
        """Test saving and loading game state."""
        self.game_state.create_new_game(seed=12345)
        
        # Save to a test file
        saved = self.game_state.save_game("test_save")
        self.assertTrue(saved)
        
        # Load the saved file
        loaded_state = GameState.load_game("test_save")
        self.assertIsNotNone(loaded_state)
        
        # Check some values
        self.assertEqual(loaded_state.seed, self.game_state.seed)
        self.assertEqual(len(loaded_state.player_fleet), len(self.game_state.player_fleet))
        self.assertEqual(loaded_state.authority_awareness, self.game_state.authority_awareness)
        
        # Clean up
        save_path = os.path.join(os.getcwd(), 'saves', 'test_save.save')
        if os.path.exists(save_path):
            os.remove(save_path)
        backup_path = f"{save_path}.bak"
        if os.path.exists(backup_path):
            os.remove(backup_path)
    
    def test_backup_restore(self):
        """Test backup and restore functionality."""
        self.game_state.create_new_game(seed=12345)
        
        # Save to a test file
        self.game_state.save_game("test_backup")
        
        # Create a modified version
        modified_state = GameState()
        modified_state.calendar = Calendar()
        modified_state.create_new_game(seed=67890)
        modified_state.authority_awareness = 0.75
        
        # Save the modified version, creating a backup
        modified_state.save_game("test_backup")
        
        # Corrupt the save file to trigger backup restoration
        save_path = os.path.join(os.getcwd(), 'saves', 'test_backup.save')
        with open(save_path, 'w') as f:
            f.write("CORRUPTED FILE")
        
        # Attempt to load the corrupted file
        loaded_state = GameState.load_game("test_backup")
        
        # Should have loaded the backup
        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state.seed, self.game_state.seed)
        
        # Clean up
        if os.path.exists(save_path):
            os.remove(save_path)
        backup_path = f"{save_path}.bak"
        if os.path.exists(backup_path):
            os.remove(backup_path)

if __name__ == "__main__":
    unittest.main()
