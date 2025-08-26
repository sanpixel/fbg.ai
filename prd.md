# Fantasy Team Optimizer - Product Requirements Document

## Overview
Create a web-based application that helps users build optimal fantasy sports teams within a specified budget constraint.

## Core Requirements

### Functional Requirements
1. **Player Data Management**
   - Read player information from a data source (CSV file)
   - Display player names, positions, and prices
   - Support multiple player positions (QB, RB, WR, TE, K, DEF)

2. **Team Optimization**
   - Find optimal team combination within $200 budget
   - Never exceed the budget constraint
   - Optimize for best value/performance ratio
   - Support lineup requirements:
     - 1 QB (Quarterback)
     - 1 RB (Running Back)
     - 2 WR (Wide Receivers) 
     - 1 TE (Tight End)
     - 1 K (Kicker)
     - 1 DEF (Defense)
     - 2 FLEX (RB/WR/TE)
     - 1 BENCH (any position)
     - **Total: 10 players**

3. **User Interface**
   - Clean, intuitive web interface using Streamlit
   - Display current team selection by position
   - Show remaining budget
   - Display total projected points
   - Allow budget adjustment
   - Show optimization results

### Technical Requirements
1. **Technology Stack**
   - Python 3.8+
   - Streamlit for web interface
   - Pandas for data manipulation
   - Optimization algorithm (greedy or linear programming)

2. **Data Format**
   - CSV file with columns: Name, Position, Price, ProjectedPoints
   - Price should be numeric values (dollars)
   - Position should use standard abbreviations (QB, RB, WR, TE, K, DEF)
   - ProjectedPoints for optimization scoring

3. **Performance**
   - Fast optimization (< 2 seconds for team selection)
   - Responsive UI updates
   - Handle 500+ players efficiently

## Success Criteria
- Successfully generate optimal teams within budget
- User-friendly interface for team management
- Accurate budget tracking and constraints
- Local deployment capability with Streamlit

## Lineup Structure
- **Starting Lineup (9 players):**
  - 1 QB
  - 1 RB
  - 2 WR
  - 1 TE
  - 1 K
  - 1 DEF
  - 2 FLEX (RB/WR/TE eligible)

- **Bench (1 player):**
  - Any position allowed

**Total Budget:** $200 maximum
