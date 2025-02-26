# RedRumRunner Implementation Plan - Python & tcod

## Phase 1: Project Foundation

### Prompt 1: Project Setup and Architecture

```
You are implementing a roguelike game called RedRumRunner with the following characteristics:
- Pirate-themed roguelike with procedurally-generated worlds
- Turn-based gameplay on a hexagonal grid
- Focus on building a fleet to defeat an armada
- JSON-based content storage for modding support

Create the initial project structure with the following:
1. A suitable folder structure with:
   - src/ directory for Python source code
   - assets/ directory for game assets
   - data/ directory for JSON files
   - docs/ directory for documentation
2. Basic project files including:
   - main.py as entry point
   - config.py for configuration
   - requirements.txt with dependencies (tcod, numpy)
   - README.md with project overview
3. Core game loop with:
   - Game initialization
   - Update loop
   - Render loop
   - Input handling

Use Python with the tcod library for rendering. Prioritize a clean, modular architecture that follows OOP principles and will support extending the game through later prompts. Include detailed comments to explain the architecture choices.
```

### Prompt 2: Basic Rendering System

```
Building on our RedRumRunner project structure, implement a basic rendering system using tcod with:
1. A console-based renderer that can display characters in a grid
   - Initialize a tcod console with appropriate dimensions
   - Create functions for clearing, rendering, and presenting the console
   - Support for different colors and styles
2. A basic camera system for positioning the view
   - Camera class that handles view positioning
   - Functions for converting world coordinates to screen coordinates
3. Utility functions for drawing text, rectangles, and other shapes
   - Text rendering with color options
   - Box drawing using tcod's built-in functions
   - Line drawing
4. Input handling
   - Keyboard event processing
   - Command mapping system

The rendering should be flexible enough to later support both the strategic world map and the tactical combat view. Use the main.py entry point created in the previous step and ensure the game can render a simple test screen with text and shapes.
```

### Prompt 3: Hexagonal Grid System

```
For our RedRumRunner game, implement a hexagonal grid system with:
1. A HexCoord class with appropriate methods for:
   - Storing and converting between different hex coordinate systems (axial, cube, offset)
   - Calculating distances between hexes
   - Finding neighbors of a hex
   - Converting between hex coordinates and screen coordinates
   - Line-of-sight calculations
2. A HexGrid class that can:
   - Store and retrieve hex cells
   - Handle different hex grid layouts (pointy-top vs flat-top)
   - Support serialization to/from JSON
3. Basic visualization of the hex grid using our tcod renderer
   - Draw hex grid with coordinates
   - Highlight selected hex
   - Display simple terrain types

Test the implementation by creating a small grid and rendering it to the screen. Include utility functions for pathfinding on the hex grid using tcod's pathfinding algorithm as we'll need this for ship movement.
```

### Prompt 4: Game State Management

```
For our RedRumRunner game, implement a robust game state management system:
1. Create a GameState class that will store:
   - The current world state
   - Player fleet and resources
   - Game time and turn information
   - Authority awareness level
2. Implement serialization/deserialization using Python's pickle or JSON for save/load functionality
3. Create a state machine for transitions between game modes:
   - Main menu
   - World map
   - Combat
   - Port interface
   - Fleet management
4. Add basic error handling and state validation

The state machine should follow the State pattern where each state (e.g., MainMenuState, WorldMapState) handles its own rendering and input processing. Integrate with our existing tcod rendering system to demonstrate state transitions between at least two game modes. Add appropriate logging using Python's logging module.
```

### Prompt 5: Game Clock and Turn System

```
For our RedRumRunner game, implement the game clock and turn system:
1. Create a Calendar class that tracks:
   - Days, months, and years in the game world
   - Season effects
   - Special events tied to specific dates
2. Implement a turn-based system where:
   - Each player action consumes a specific amount of time
   - NPCs and world events update based on elapsed time
   - Time advances only when the player takes actions
3. Create a simple UI element using tcod to show the current date and time
4. Implement a system for scheduling future events

The system should integrate with our GameState and support the concept that authorities will gather forces over approximately one year of game time. Add a simple test function that advances time and shows the changes in the UI. Use appropriate Python data structures like deque from collections for the event queue.
```

## Phase 2: World Generation

### Prompt 6: Basic Map Generation

```
For our RedRumRunner game, implement the procedural world generation system:
1. Create a WorldGenerator class that produces:
   - A world map of approximately 100 locations on our hex grid
   - Basic terrain types (ocean, land, coastline)
   - Rivers and mountain ranges
2. Implement noise-based generation using NumPy and tcod's noise functions for natural-looking terrain
   - Use multiple noise layers for different features
   - Apply appropriate thresholds for terrain type determination
3. Add parameters to control generation (world size, land percentage, etc.)
4. Ensure the world wraps appropriately (either as a globe or with edges)

Integrate with our existing tcod renderer to display the generated world with different colors for terrain types. The system should be consistent enough that similar seed values produce similar worlds, but with enough variation to be interesting. Add logging for the generation process.
```

### Prompt 7: Location Generation

```
Building on our world generation, implement location placement and types:
1. Create classes for different location types:
   - Ports (major and minor)
   - Resource regions for our economic triangle (plant regions, river silt, etc.)
   - Landmarks and points of interest
2. Implement an algorithm that places 20-30 major ports realistically:
   - Along coastlines
   - Near river mouths
   - With appropriate spacing
3. Place resource regions in consistent directions
4. Add a naming system for locations using procedural generation

Update the tcod renderer to display these locations on the world map with appropriate symbols and colors. Each location should have appropriate metadata stored in our GameState. Use Python's random module with a fixed seed for consistent generation.
```

### Prompt 8: Fog of War System

```
For our RedRumRunner game, implement a fog of war system:
1. Add a visibility layer to our hex grid that tracks:
   - Unexplored areas (completely hidden)
   - Previously explored areas (partially visible)
   - Currently visible areas (fully visible)
2. Create mechanics for how visibility is updated:
   - Ships have a visibility radius
   - Terrain affects visibility (e.g., mountains block line of sight)
   - Use tcod's FOV algorithms to calculate visibility efficiently
3. Implement rendering for different visibility states using tcod:
   - Unexplored areas shown as dark/black
   - Previously explored areas shown as dimmed
   - Currently visible areas shown at full brightness
4. Add a system for revealing areas through events/information

Integrate this with our existing world rendering to show how the map reveals as the player explores. Only information in visible or previously explored areas should be accessible to the player. Add utility functions for checking visibility status.
```

## Phase 3: Player and Ships

### Prompt 9: Player Entity and Starting Ship

```
For our RedRumRunner game, implement the player entity and starting ship:
1. Create a Player class that tracks:
   - Player stats and reputation
   - Inventory and resources
   - Known information (discovered locations, rumors)
2. Implement a Ship class with:
   - Multiple-hex representation (2-5 hexes based on size)
   - Orientation and facing
   - Basic stats (speed, health, cargo capacity)
   - Crew capacity
3. Create the starting scenario:
   - Player begins as a condemned pirate
   - Start with one small ship
   - Initial position at a minor port

Update the tcod renderer to display the player's ship on the world map with appropriate symbol and color. The ship should occupy multiple hexes and have a clear indication of its orientation. Add a simple player status UI element showing basic information.
```

### Prompt 10: Ship Movement

```
Building on our ship implementation, create the movement system:
1. Implement movement mechanics for ships:
   - Ships move according to their orientation
   - Movement costs time (turns)
   - Ships have momentum and can't turn instantly
2. Add wind effects on movement:
   - Create a wind direction and strength system
   - Implement effects of wind on ship speed
   - Add UI indication of current wind using tcod
3. Create path planning for ships:
   - Allow plotting a course using tcod's pathfinding
   - Calculate time estimates for journeys
   - Handle obstacles appropriately

Integrate with our existing systems to allow the player to move their ship around the world map with keyboard controls. Ensure the fog of war updates as the ship moves. Add visual feedback for planned paths and possible movement destinations.
```

## Phase 4: Economic System

### Prompt 11: Basic Resource System

```
For our RedRumRunner game, implement the core economic resources:
1. Create classes for the three main resources in our economic triangle:
   - The special plant that grows in specific regions
   - River silt (fertilizer) that enhances the plant
   - The upgraded alcoholic drink made from fertilized plants
2. Add additional common trade goods:
   - Food and supplies
   - Luxury goods
   - Ship materials
   - Weapons and ammunition
3. Implement resource generation in appropriate regions
4. Create cargo and inventory systems for storing resources

Use Python's dataclasses for clean resource definitions. Update the game state to track these resources and integrate with our existing systems. Resources should be visible in the player's inventory and should be generated in the world. Create a simple UI using tcod to display the player's current cargo.
```

### Prompt 12: Port Trading Interface

```
Building on our resource system, implement the port trading interface:
1. Create a port interaction screen using tcod that shows:
   - Available goods and their prices
   - Player's cargo and capacity
   - Buy/sell interface with keyboard controls
2. Implement basic trading mechanics:
   - Buying and selling goods
   - Price calculations based on supply/demand
   - Cargo weight/volume constraints
3. Add port services:
   - Ship repairs
   - Crew recruitment
   - Information gathering
4. Create a reputation system that affects prices and services

Integrate with our game state transitions to allow access to the port interface when a player's ship is at a port location. Use tcod's console capabilities to create an intuitive menu system for the trading interface. Add appropriate feedback messages for transactions.
```

### Prompt 13: Dynamic Economy

```
Enhance our economic system with dynamic elements:
1. Implement price fluctuations based on:
   - Supply and demand
   - Distance from production regions
   - Local events and conditions
2. Create an event system that affects the economy:
   - Natural disasters affecting production
   - Trade embargoes
   - Festivals increasing demand
3. Add trade routes with NPCs that move goods between ports
4. Implement the contraband system:
   - Mark certain goods as illegal
   - Add risk/reward mechanics for smuggling
   - Create authority checks for contraband

Update our port interface to reflect these dynamic prices and conditions. The system should create interesting economic opportunities for the player to exploit. Use Python's random module with appropriate weighting for event generation.
```

## Phase 5: Fleet Management

### Prompt 14: Multiple Ship Management

```
For our RedRumRunner game, expand the player's capabilities to manage multiple ships:
1. Enhance the Player class to track a fleet of ships
2. Implement fleet movement mechanics:
   - Formation movement
   - Speed limited by slowest ship
   - Split/merge fleet operations
3. Create a fleet management interface using tcod:
   - Overview of all ships
   - Assignment of officers
   - Cargo distribution
4. Add ship acquisition methods:
   - Purchasing at ports
   - Commissioning builds (time-based)

Update our existing movement and rendering systems to handle multiple ships. The fleet should behave as a cohesive unit when moving together. Use appropriate data structures like Python lists or dictionaries to manage the fleet collection.
```

### Prompt 15: Crew and Officers System

```
Implement the crew and officers management system:
1. Create an Officer class with:
   - Individual stats and skills
   - Special abilities
   - Loyalty and morale
2. Implement crew as a resource:
   - Quantity per ship
   - Effects on ship performance
   - Morale and loyalty mechanics
3. Add crew and officer acquisition:
   - Recruiting at ports
   - Rescuing castaways
   - Training and promotion
4. Create assignment mechanics for placing officers on ships

Integrate with our fleet management to allow assigning crews and officers to ships. The system should impact ship performance based on crew and officer quality. Create a tcod-based UI for crew and officer management that shows stats and assignments.
```

## Phase 6: Combat System

### Prompt 16: Basic Combat Initiation

```
For our RedRumRunner game, implement the initial combat system:
1. Create encounter generation:
   - Random encounters based on region
   - Authority patrols based on notoriety
   - Merchant vessels for potential piracy
2. Implement combat state transition:
   - From world map to tactical combat view
   - Initialize ships in appropriate starting positions
   - Set up wind and environmental conditions
3. Create the tactical hex grid:
   - Smaller scale than world map
   - Environmental features (reefs, islands)
   - Wind representation

Integrate with our state management to transition between strategic and tactical modes. The initial combat setup should reflect the world state at the time of encounter. Render the combat grid using tcod with appropriate colors and symbols for different elements.
```

### Prompt 17: Ship Combat Movement and Actions

```
Build upon our combat system with movement and actions:
1. Implement tactical movement for ships:
   - Turn-based movement on the combat grid
   - Different movement capabilities based on ship type
   - Wind effects on tactical movement
2. Create combat actions:
   - Firing weapons (with targeting)
   - Evasive maneuvers
   - Prepare for boarding
   - Intimidation attempts
3. Add targeting mechanics:
   - Target specific ship sections
   - Different ammunition types
   - Hit probability calculations

Update the combat interface using tcod to display these options and show the results of actions. The system should support the pirate-focused goal of capturing ships rather than sinking them. Add visual feedback for actions and targeting.
```

### Prompt 18: Boarding and Ship Capture

```
Implement the boarding and capture mechanics:
1. Create the boarding system:
   - Conditions required for boarding
   - Movement of crew between ships
   - Combat resolution between crews
2. Implement the intimidation system:
   - Reputation effects
   - Ship strength comparison
   - Surrender probability
3. Add ship capture mechanics:
   - Taking control of captured vessels
   - Prisoner handling
   - Integration into player's fleet
4. Create post-combat resolution:
   - Damage assessment
   - Loot distribution
   - Return to world map

This system should integrate with our existing combat and fleet management to allow the player to grow their fleet through piracy. Use tcod to create appropriate UI elements for boarding actions and combat resolution.
```

## Phase 7: Authority and Progression

### Prompt 19: Authority Awareness System

```
For our RedRumRunner game, implement the authority awareness system:
1. Create a notoriety tracking mechanism:
   - Increases with piracy and illegal activities
   - Decays slowly over time
   - Can be modified through bribes or actions
2. Implement effects of notoriety:
   - Increased patrol frequency
   - Higher prices at legitimate ports
   - Bounty hunters targeting the player
3. Add UI elements using tcod showing current notoriety
4. Create a "wanted" system with bounties on the player

Integrate with our existing systems to have notoriety impact gameplay. This should create escalating challenges as the player engages in more piracy. Add visual feedback using tcod for notoriety changes and current level.
```

### Prompt 20: Escalating Authority Response

```
Implement the escalating authority response system:
1. Create a time-based escalation mechanism:
   - Authority gathering forces over one year
   - Progressive stages of response
   - Indicators of approaching final confrontation
2. Implement increasing responses:
   - Trade embargoes
   - Blockades of friendly ports
   - Task forces hunting the player
3. Add ways to delay or disrupt authority plans
4. Create the final armada generation:
   - Fleet composition based on game difficulty
   - Special flagship with unique properties
   - Victory conditions for defeating/capturing it

This system should provide the primary progression and end-game challenge, integrating with our existing combat and time systems. Use Python's object-oriented features to create different types of authority responses.
```

## Phase 8: UI Refinement and Content

### Prompt 21: Strategic Map UI Improvements

```
Enhance the strategic map UI for better player experience using tcod:
1. Implement information overlays showing:
   - Economic conditions
   - Authority presence
   - Wind patterns
   - Known resources
2. Create a navigation system:
   - Route planning with visual feedback
   - Travel time estimation
   - Danger indicators
3. Add filters for different map views
4. Implement zoom levels for different detail

Integrate with our existing world representation to provide these additional visualization options. The UI should help players make strategic decisions about movement and trading. Use tcod's console layering capabilities for overlays.
```

### Prompt 22: Captain's Log and Quest System

```
For our RedRumRunner game, implement the captain's log and quest system:
1. Create a journal interface using tcod that tracks:
   - Completed activities
   - Current objectives
   - Rumors and information
   - Historical events
2. Implement a basic quest system:
   - Procedurally generated objectives
   - Rewards for completion
   - Multiple quest types (delivery, hunting, etc.)
3. Add a rumor collection mechanism:
   - Information gathering at ports
   - Hints about valuable opportunities
   - Warnings about authority movements
4. Create UI for browsing and managing these elements

This system should provide additional direction and goals for the player beyond the main objective of defeating the armada. Use appropriate data structures in Python to organize quests and journal entries.
```

## Phase 9: Polish and Modding

### Prompt 23: JSON Content System

```
Implement the JSON-based content system for modding support:
1. Convert hardcoded content to load from JSON files:
   - Ship types and attributes
   - Resource definitions
   - Location types
   - Event templates
2. Create a mod loading system:
   - Folder structure for mods
   - Load order management
   - Content overriding
3. Implement validation for loaded content using Python's JSON schema
4. Add documentation for the JSON formats

Use Python's json module for loading and saving content. This system should allow the game's content to be extended or replaced without changing the core code, supporting the modding goals outlined in the specification.
```

### Prompt 24: Example Mod Implementation

```
Create an example mod for RedRumRunner to demonstrate modding capabilities:
1. Implement an alternate setting mod:
   - New theme (submarine, airship, etc.)
   - Reskinned resources and ships
   - Modified progression
2. Include complete JSON files for:
   - New ship types
   - Altered economic resources
   - Changed world generation parameters
3. Add documentation explaining the changes
4. Create a toggle in the main menu for enabling/disabling mods

This example should serve as a template for future modders and demonstrate the flexibility of our content system. Ensure the mod properly integrates with the base game using our JSON loading system.
```

### Prompt 25: Final Integration and Testing

```
For our RedRumRunner game, implement final integration and testing:
1. Create comprehensive testing using pytest:
   - Unit tests for core mechanics
   - Integration tests for system interactions
   - Test fixtures for game states
2. Implement help systems using tcod:
   - Tooltips
   - Tutorial elements
   - Reference information
3. Add quality of life features:
   - Message log
   - Configuration options
   - Performance optimizations
4. Create a final build process using PyInstaller

This step should ensure all systems work together harmoniously and the game provides a complete experience as described in the specification document. Add appropriate logging and error handling throughout the codebase.
```

## Implementation Considerations

Throughout this implementation plan, I've ensured that:

1. Each step builds incrementally on previous work
2. Core systems are established before dependent features
3. The tcod library is leveraged for rendering, input handling, and algorithmic utilities
4. Python best practices are followed (OOP, appropriate data structures, error handling)
5. The architecture supports modding from the beginning
6. Testing can be performed at each stage

The prompts are designed to be specific enough to guide implementation while allowing for technical creativity in solving each challenge. The progression follows a logical path from core systems to advanced features, ensuring that at each stage there is a functional (if limited) version of the game to test and evaluate.