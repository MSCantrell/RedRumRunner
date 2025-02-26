import tcod

class Config:
    """
    Configuration settings for RedRumRunner.
    """
    # Display settings
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 50
    WINDOW_TITLE = "RedRumRunner"
    
    # Font settings
    FONT_PATH = "assets/fonts/dejavu10x10_gs_tc.png"  # Adjust to your actual font path
    FONT_FLAGS = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
    
    # Game settings
    GAME_VERSION = "0.1.0"
    
    # Performance settings
    FPS_LIMIT = 60
    
    # Game balance settings
    INITIAL_GOLD = 100
    SHIP_COST_MULTIPLIER = 1.0
    AUTHORITY_AWARENESS_INCREASE_RATE = 0.01
    AUTHORITY_AWARENESS_DECREASE_RATE = 0.001
