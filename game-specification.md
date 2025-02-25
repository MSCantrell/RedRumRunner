# RedRumRunner: Game Specification Document

## Game Overview
RedRumRunner is a pirate-themed roguelike game where players control a sea captain who starts with one ship and must build a fleet capable of defeating (or capturing) the authorities' armada that will come for them after approximately one year of game time. The game features procedurally-generated worlds, turn-based gameplay, and permanent death in the tradition of classic roguelikes.

## Core Mechanics

### World & Setting
- **Setting**: A fictional world loosely similar to the Caribbean in the 1700s
- **Economic Triangle**: Based on three main resources:
  - Plant that grows in specific regions
  - Special river silt (fertilizer) that enhances plant properties
  - Upgraded alcoholic drink brewed from fertilized plants that gives visions
- **Map Generation**:
  - Procedurally-generated world with approximately 100 locations
  - 20-30 major ports across different regions
  - Three main economic regions placed in roughly consistent directions
  - Fog of war reveals the map as the player explores

### Game Structure
- **View & Layout**: Overhead view with hexagonal grid
- **Turn System**: Turn-based gameplay for both strategic and tactical modes
- **Game Clock**: Calendar system that advances with player actions
- **Permadeath**: No save scumming; death is permanent

### Player Progression
- **Starting Point**: Player begins as a condemned pirate with a death sentence
- **Primary Progression**: Fleet expansion (more ships, larger ships)
- **Acquisition Methods**:
  - Capturing enemy ships through boarding
  - Purchasing vessels at ports
  - Commissioning builds (time-consuming)
- **Fleet Size Benchmarks**:
  - 20 ships: Challenging but possible victory
  - 50 ships: Overwhelming force, guaranteed victory

### Ship-to-Ship Combat
- **Pirate-Focused Combat System**:
  - Goal is to capture ships, not sink them
  - Emphasis on boarding and intimidation tactics
- **Ship Representation**:
  - Each ship occupies multiple hexes (2-5 depending on size)
  - Ships have orientation affecting movement and firing arcs
  - Different ship sections can be targeted independently
- **Combat Flow**:
  - Approach Phase: Maneuvering for boarding position
  - Intimidation Phase: Attempts to force surrender
  - Boarding Phase: Crew vs. crew combat if necessary
- **Environmental Factors**:
  - Wind direction and strength impact movement
  - Terrain features (reefs, islands) provide tactical options
- **Damage System**:
  - Targeted damage to disable rather than destroy
  - Hull, sail, and crew damage types
  - Special ammunition for specific tactical goals

### Crew Management
- **Leadership Roles** (individually modeled):
  - Ship Captains
  - First Mates
  - Navigators
  - Other specialist officers
- **General Crew** (resource-based):
  - Tracked as total numbers per ship
  - Require supplies (food, water, pay)
  - Affect ship performance
  - Transferable between vessels
- **Acquisition**:
  - Recruiting at ports
  - Capturing from enemy ships
  - Rescuing castaways

### Economy & Trade
- **Dynamic Economy**:
  - Fluctuating prices based on events and supply/demand
  - Local events impact resource availability
  - Distance affects price differences
  - Legal vs. contraband goods (higher risk, higher reward)
- **Player Activities**:
  - Trading between ports
  - Smuggling contraband
  - Raiding settlements or ships
  - Time-investment activities (building, training)

### Authority & Awareness System
- **Clock Mechanism**:
  - Authorities gather forces over approximately one year
  - Final confrontation occurs after this period
- **Authority Awareness**:
  - Increases with notorious actions
  - Can be temporarily reduced through bribes or misdirection
  - Affects patrol frequency and bounty hunters
- **Escalating Responses**:
  - Increased patrols
  - Bounty hunters
  - Trade embargoes
  - Strategic blockades
  - Small task forces
  - Final armada

### Victory Conditions
- **Standard Victory**: Defeat the authorities' fleet
- **Challenge Victory**: Capture the flagship and force surrender

## Technical Requirements

### Architecture
- **Core Game Logic**: Implement core mechanics in a modular fashion
- **Content Storage**: Extensive use of JSON files for game content to support modding
- **Rendering**: Traditional roguelike ASCII/tile-based rendering

### User Interface
- **Strategic Map (Over Map)**:
  - World overview with fog of war
  - Ship/fleet positions
  - Known ports and landmarks
  - Wind direction indicator
  - Time/calendar display
  - Authority awareness meter
- **Economy/Trading Screen**:
  - Cargo manifests
  - Price lists
  - Trends and rumors
- **Combat Tactical Map**:
  - Hex-based view
  - Ship positioning
  - Crew allocation interface
  - Targeting controls
- **Port Interface**:
  - Menu-based location services
  - Quick navigation between facilities
- **Fleet Management Screen**:
  - Ship stats and condition
  - Crew assignment
  - Repair needs
- **Captain's Log**:
  - Quest tracking
  - Rumor collection
  - Historical events

### Data Structure
- **World Data**:
  - Map configuration (JSON)
  - Location information (JSON)
  - Economic relationships (JSON)
- **Ship Templates**:
  - Ship types and attributes (JSON)
  - Weapon configurations (JSON)
- **Character Data**:
  - Officer templates and abilities (JSON)
  - Crew statistics (JSON)
- **Event System**:
  - Random events and consequences (JSON)
  - Rumor generation rules (JSON)

### Modding Support
- **Content Replacement**: All game content stored in accessible JSON files
- **Core/Content Separation**: Clean architecture separating mechanics from content
- **Documentation**: Thorough documentation of data formats and relationships
- **Example Mods**: Include sample alternate settings (e.g., submarine, airship)

## Implementation Plan

### Phase 1: Core Systems
- World generation
- Basic movement
- Time system
- Initial UI framework

### Phase 2: Economic Systems
- Trade mechanics
- Port interactions
- Resource management
- Price fluctuations

### Phase 3: Combat
- Ship representation
- Movement and positioning
- Boarding mechanics
- Damage system

### Phase 4: Progression
- Ship acquisition
- Fleet management
- Crew systems
- Authority response

### Phase 5: Content & Balancing
- World content
- Events and rumors
- Difficulty tuning
- End-game scenarios

### Phase 6: Polish & Modding
- Help system
- UI improvements
- Modding documentation
- Example mods

## Error Handling & Stability

### Critical Systems
- Save backup system to mitigate corruption
- Validation of JSON data on load
- Graceful handling of missing or corrupted resources
- Extensive logging for debugging

### Testing Strategy
- Unit tests for core mechanics
- Integration tests for system interactions
- Play-testing focused on balance and progression
- Specific testing for edge cases (maximum fleet size, unusual economic conditions)

## Appendix: Game Lore

### Economic Triangle
In this world, a special plant grows natively in specific regions. When fertilized with the silt from rivers flowing through certain mountains, the plant develops unique properties. These enhanced plants can be brewed into a superior alcoholic drink that not only has less severe hangovers but also gives drinkers vision-like experiences. This creates a three-part trade cycle that drives the economy.

### Setting Context
Players are already condemned pirates at the start of the game, with authorities determined to bring them to justice. The game world is rich with rumors (some true, some false) that create an atmosphere of mystery and discovery as players explore.

### Final Confrontation
The authorities will assemble a substantial fleet (30-40 ships) to hunt down the player after approximately one year. This fleet has fixed elements but randomized variations to ensure replayability. The player must decide whether to simply defeat this armada or attempt the more challenging goal of capturing it.
