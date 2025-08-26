import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import random

# Page config
st.set_page_config(
    page_title="Fantasy Team Optimizer",
    page_icon="🏈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS for styling
st.markdown("""
<style>
    /* Green optimize button */
    .stButton button {
        border-radius: 4px !important;
    }
    
    .stButton button:contains('🏈 Optimize Team') {
        background-color: #28a745 !important;
        color: white !important;
        border-color: #28a745 !important;
    }
    
    .stButton button:contains('🏈 Optimize Team'):hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
    }
    
    /* Limit width and center */
    .block-container {
        max-width: 1000px !important;
        margin: 0 auto !important;
    }
    
    /* Hide spinner arrows on number inputs */
    .stNumberInput button {
        display: none !important;
    }
    
    input[type=number]::-webkit-outer-spin-button,
    input[type=number]::-webkit-inner-spin-button {
        -webkit-appearance: none !important;
        margin: 0 !important;
    }
    
    input[type=number] {
        -moz-appearance: textfield !important;
    }
    
    /* Game score styling */
    .score-correct {
        background-color: #d4edda !important;
        border: 1px solid #c3e6cb !important;
        color: #155724 !important;
        padding: 0.75rem 1.25rem !important;
        border-radius: 0.25rem !important;
        margin-bottom: 1rem !important;
    }
    
    .score-incorrect {
        background-color: #f8d7da !important;
        border: 1px solid #f5c6cb !important;
        color: #721c24 !important;
        padding: 0.75rem 1.25rem !important;
        border-radius: 0.25rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Game button styling */
    .stButton button:contains('🎯 Next Player') {
        background-color: #17a2b8 !important;
        color: white !important;
        border-color: #17a2b8 !important;
    }
    
    .stButton button:contains('🎯 Next Player'):hover {
        background-color: #138496 !important;
        border-color: #117a8b !important;
    }
    
    .stButton button:contains('📊 End Game') {
        background-color: #6c757d !important;
        color: white !important;
        border-color: #6c757d !important;
    }
    
    .stButton button:contains('📊 End Game'):hover {
        background-color: #5a6268 !important;
        border-color: #545b62 !important;
    }
    
    .stButton button:contains('🎯 Guess My Tier') {
        background-color: #ffc107 !important;
        color: #212529 !important;
        border-color: #ffc107 !important;
        font-weight: bold !important;
    }
    
    .stButton button:contains('🎯 Guess My Tier'):hover {
        background-color: #e0a800 !important;
        border-color: #d39e00 !important;
    }
</style>
""", unsafe_allow_html=True)

class FantasyOptimizer:
    def __init__(self, players_df: pd.DataFrame, budget: float = 200.0):
        self.players_df = players_df
        self.budget = budget
        
        # Lineup requirements
        self.lineup_requirements = {
            'QB': 1,
            'RB': 1,  # 1 required RB + 2 FLEX (can be RB)
            'WR': 2,  # 2 required WR + 2 FLEX (can be WR)
            'TE': 1,  # 1 required TE + 2 FLEX (can be TE)
            'K': 1,
            'DEF': 1,
            'FLEX': 2,  # RB/WR/TE eligible
            'BENCH': 5  # Any position
        }
        
    def get_players_by_position(self) -> Dict[str, pd.DataFrame]:
        """Get players grouped by position"""
        return {pos: self.players_df[self.players_df['Position'] == pos] 
                for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']}
    
    def randomize_player_selection(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """Randomize player selection from top performers to create variety"""
        df_copy = df.copy().sort_values('Price', ascending=True)
        # Take top players by price efficiency but add some randomization
        if len(df_copy) > top_n:
            top_players = df_copy.head(top_n)
            return top_players.sample(frac=1).reset_index(drop=True)
        return df_copy.sample(frac=1).reset_index(drop=True)
    
    def optimize_team_greedy(self) -> Tuple[List[Dict], float]:
        """
        Simple team selection - just fill all positions and try to get close to budget
        """
        players_by_pos = self.get_players_by_position()
        
        best_team = None
        best_cost = 0
        max_attempts = 100  # Reduce attempts since logic is simpler
        
        for attempt in range(max_attempts):
            selected_players = []
            total_cost = 0.0
            selected_names = set()
            
            # Fill required positions first
            required_positions = [
                ('QB', 1), ('RB', 1), ('WR', 2), ('TE', 1), ('K', 1), ('DEF', 1)
            ]
            
            success = True
            for pos, count in required_positions:
                pos_players = players_by_pos[pos]
                available_players = pos_players[~pos_players['Name'].isin(selected_names)]
                
                if len(available_players) < count:
                    success = False
                    break
                
                # Apply top_players_count filter if set
                top_count = getattr(self, 'top_players_count', 0)
                if top_count > 0 and len(available_players) > top_count:
                    # Sort by price descending and take top N
                    available_players = available_players.sort_values('Price', ascending=False).head(top_count)
                
                # Randomize selection from available options
                chosen_players = available_players.sample(n=count, replace=False)
                
                for _, player in chosen_players.iterrows():
                    selected_players.append({
                        'Name': player['Name'],
                        'Position': player['Position'], 
                        'Role': pos,
                        'Price': player['Price']
                    })
                    total_cost += player['Price']
                    selected_names.add(player['Name'])
            
            if not success:
                continue
                
            # Fill FLEX positions (2 spots from RB/WR/TE)
            flex_eligible = pd.concat([
                players_by_pos['RB'],
                players_by_pos['WR'], 
                players_by_pos['TE']
            ])
            
            available_flex = flex_eligible[~flex_eligible['Name'].isin(selected_names)]
            if len(available_flex) < 2:
                continue
                
            # Apply top_players_count filter for FLEX
            top_count = getattr(self, 'top_players_count', 0)
            if top_count > 0 and len(available_flex) > top_count:
                available_flex = available_flex.sort_values('Price', ascending=False).head(top_count)
            
            chosen_flex = available_flex.sample(n=2, replace=False)
            for _, player in chosen_flex.iterrows():
                selected_players.append({
                    'Name': player['Name'],
                    'Position': player['Position'],
                    'Role': 'FLEX', 
                    'Price': player['Price']
                })
                total_cost += player['Price']
                selected_names.add(player['Name'])
            
            # Fill BENCH (5 spots from any position)
            all_available = self.players_df[~self.players_df['Name'].isin(selected_names)]
            if len(all_available) < 5:
                continue
                
            # Apply bench max cost filter
            bench_max = getattr(self, 'bench_max', 50)
            bench_candidates = all_available[all_available['Price'] <= bench_max]
            
            # If not enough under bench_max, use all available
            if len(bench_candidates) < 5:
                bench_candidates = all_available
                
            # Sort by price ascending (prefer cheaper for bench)
            bench_candidates = bench_candidates.sort_values('Price', ascending=True)
            
            # Take first 5 that fit
            chosen_bench = bench_candidates.head(5)
            for _, player in chosen_bench.iterrows():
                selected_players.append({
                    'Name': player['Name'],
                    'Position': player['Position'],
                    'Role': 'BENCH',
                    'Price': player['Price']
                })
                total_cost += player['Price']
                selected_names.add(player['Name'])
            
            # Check if team is complete and within budget constraints
            min_budget = getattr(self, 'min_budget', 100)
            if (len(selected_players) == 14 and 
                total_cost > min_budget and 
                total_cost < self.budget and
                total_cost > best_cost):
                
                # Verify position requirements
                position_counts = {}
                for player in selected_players:
                    pos = player['Position']
                    position_counts[pos] = position_counts.get(pos, 0) + 1
                
                if (position_counts.get('QB', 0) == 1 and
                    position_counts.get('K', 0) == 1 and 
                    position_counts.get('DEF', 0) == 1):
                    best_team = selected_players
                    best_cost = total_cost
        
        return best_team if best_team else [], best_cost

def get_player_tier(players_df, player_name, position):
    """Calculate which tier a player belongs to based on position and price rank"""
    pos_players = players_df[players_df['Position'] == position].sort_values('Price', ascending=False).reset_index(drop=True)
    player_idx = pos_players[pos_players['Name'] == player_name].index[0]
    
    # Define tier boundaries for each position
    tier_boundaries = {
        'QB': [5, 16, 28],  # Tiers: 1-5, 6-16, 17-28
        'RB': [7, 13, 35, 60],  # Tiers: 1-7, 8-13, 14-35, 36-60
        'WR': [1, 8, 13, 21, 44, 75],  # Tiers: 1, 2-8, 9-13, 14-21, 22-44, 45-75
        'TE': [5, 17, 29],  # Tiers: 1-5, 6-17, 18-29
        'K': [3, 16],  # Tiers: 1-3, 4-16
        'DEF': [3, 16]  # Tiers: 1-3, 4-16
    }
    
    boundaries = tier_boundaries.get(position, [])
    tier = 1
    for boundary in boundaries:
        if player_idx >= boundary:
            tier += 1
        else:
            break
    
    return tier

def get_tier_options(position):
    """Get available tier options for a position"""
    tier_counts = {
        'QB': 3,  # 3 tiers
        'RB': 4,  # 4 tiers  
        'WR': 6,  # 6 tiers
        'TE': 3,  # 3 tiers
        'K': 2,   # 2 tiers
        'DEF': 2  # 2 tiers
    }
    return list(range(1, tier_counts.get(position, 3) + 1))

def start_new_game(players_df):
    """Start a new guess the tier game"""
    # Pick a random player (exclude K and DEF since they're all $1)
    eligible_positions = ['QB', 'RB', 'WR', 'TE']
    eligible_players = players_df[players_df['Position'].isin(eligible_positions)]
    
    random_player = eligible_players.sample(1).iloc[0]
    
    st.session_state.current_player = {
        'name': random_player['Name'],
        'position': random_player['Position'],
        'price': random_player['Price'],
        'tier': get_player_tier(players_df, random_player['Name'], random_player['Position'])
    }
    st.session_state.show_answer = False
    st.session_state.game_active = True
    st.session_state.last_result = None  # Reset color to normal for new player

@st.cache_data
def load_player_data(file_path: str = "players.csv") -> pd.DataFrame:
    """Load player data from CSV file (fallback)"""
    try:
        df = pd.read_csv(file_path)
        # Remove ProjectedPoints if it exists
        if 'ProjectedPoints' in df.columns:
            df = df.drop('ProjectedPoints', axis=1)
        return df
    except FileNotFoundError:
        st.error(f"Player data file '{file_path}' not found. Please ensure the file exists in the current directory.")
        return pd.DataFrame()

def main():
    # Initialize session state for teams list if it doesn't exist
    if 'teams' not in st.session_state:
        st.session_state.teams = []
    
    # Initialize session state for guess game
    if 'game_active' not in st.session_state:
        st.session_state.game_active = False
    if 'current_player' not in st.session_state:
        st.session_state.current_player = None
    if 'game_score' not in st.session_state:
        st.session_state.game_score = {'correct': 0, 'total': 0}
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    
    # Initialize debug mode
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
    if 'debug_password_entered' not in st.session_state:
        st.session_state.debug_password_entered = False
    
    # Sidebar for tier minimum settings
    with st.sidebar:
        # Debug mode section at the top
        st.header("Debug Mode")
        if not st.session_state.debug_password_entered:
            debug_password = st.text_input("Enter debug password:", type="password", key="debug_password")
            if st.button("Enable Debug", key="enable_debug"):
                if debug_password == "warez":
                    st.session_state.debug_mode = True
                    st.session_state.debug_password_entered = True
                    st.success("Debug mode enabled!")
                    st.rerun()
                else:
                    st.error("Invalid password")
        else:
            if st.session_state.debug_mode:
                st.success("🐛 Debug mode is ON")
                if st.button("Disable Debug", key="disable_debug"):
                    st.session_state.debug_mode = False
                    st.session_state.debug_password_entered = False
                    st.info("Debug mode disabled")
                    st.rerun()
        
        st.divider()
        
        st.header("Tier Minimums")
        st.write("Set minimum players required from each tier (Tier 1 = most expensive). Leave at 0 for no requirement.")
        
        # Create tier minimum controls for each position
        tier_mins = {}
        
        # QB: Tiers 1(5), 2(11), 3(12)
        st.subheader("QB (5,11,12)")
        tier_mins['QB_T1'] = st.number_input("QB T1 Min", min_value=0, max_value=5, value=0, step=1, help="Min from top 5 QBs")
        tier_mins['QB_T2'] = st.number_input("QB T2 Min", min_value=0, max_value=11, value=0, step=1, help="Min from next 11 QBs")
        tier_mins['QB_T3'] = st.number_input("QB T3 Min", min_value=0, max_value=12, value=0, step=1, help="Min from remaining 12 QBs")
        
        # RB: Tiers 1(7), 2(6), 3(22), 4(25)
        st.subheader("RB (7,6,22,25)")
        tier_mins['RB_T1'] = st.number_input("RB T1 Min", min_value=0, max_value=7, value=0, step=1, help="Min from top 7 RBs")
        tier_mins['RB_T2'] = st.number_input("RB T2 Min", min_value=0, max_value=6, value=0, step=1, help="Min from next 6 RBs")
        tier_mins['RB_T3'] = st.number_input("RB T3 Min", min_value=0, max_value=22, value=0, step=1, help="Min from next 22 RBs")
        tier_mins['RB_T4'] = st.number_input("RB T4 Min", min_value=0, max_value=25, value=0, step=1, help="Min from remaining 25 RBs")
        
        # WR: Tiers 1(1), 2(7), 3(5), 4(8), 5(23), 6(31)
        st.subheader("WR (1,7,5,8,23,31)")
        tier_mins['WR_T1'] = st.number_input("WR T1 Min", min_value=0, max_value=1, value=0, step=1, help="Min from top 1 WR")
        tier_mins['WR_T2'] = st.number_input("WR T2 Min", min_value=0, max_value=7, value=0, step=1, help="Min from next 7 WRs")
        tier_mins['WR_T3'] = st.number_input("WR T3 Min", min_value=0, max_value=5, value=0, step=1, help="Min from next 5 WRs")
        tier_mins['WR_T4'] = st.number_input("WR T4 Min", min_value=0, max_value=8, value=0, step=1, help="Min from next 8 WRs")
        tier_mins['WR_T5'] = st.number_input("WR T5 Min", min_value=0, max_value=23, value=0, step=1, help="Min from next 23 WRs")
        tier_mins['WR_T6'] = st.number_input("WR T6 Min", min_value=0, max_value=31, value=0, step=1, help="Min from remaining 31 WRs")
        
        # TE: Tiers 1(5), 2(12), 3(12)
        st.subheader("TE (5,12,12)")
        tier_mins['TE_T1'] = st.number_input("TE T1 Min", min_value=0, max_value=5, value=0, step=1, help="Min from top 5 TEs")
        tier_mins['TE_T2'] = st.number_input("TE T2 Min", min_value=0, max_value=12, value=0, step=1, help="Min from next 12 TEs")
        tier_mins['TE_T3'] = st.number_input("TE T3 Min", min_value=0, max_value=12, value=0, step=1, help="Min from remaining 12 TEs")
    
    st.title("🏈 Fantasy Team Randomizer")
    st.markdown("**Build the optimal fantasy team within your budget!**")
    
    # Load player data automatically
    players_df = load_player_data()
    
    if not players_df.empty:
        # Consolidate all debug info in one line
        position_counts = players_df['Position'].value_counts()
        tier_info = {
            'QB': '5,11,12', 'RB': '7,6,22,25', 'WR': '1,7,5,8,23,31', 
            'TE': '5,12,12', 'K': '3,13', 'DEF': '3,13'
        }
        
        debug_parts = []
        for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            count = position_counts.get(pos, 0)
            debug_parts.append(f"{pos}:{count}({tier_info[pos]})")
        
        st.write(f"**Loaded {len(players_df)} players:** {' | '.join(debug_parts)}")
    else:
        st.error("Could not load player data. Please check that players.csv exists.")
    
    if players_df.empty:
        st.stop()
    
    # DEBUG: Hide settings for now
    # # Settings in main content area
    # st.subheader("Settings")
    # 
    # # Budget and basic settings
    # col1, col2, col3, col4 = st.columns(4)
    # with col1:
    #     min_budget = st.number_input("Min $", min_value=50, max_value=300, value=175, step=1)
    # with col2:
    #     max_budget = st.number_input("Max $", min_value=150, max_value=300, value=200, step=1)
    # with col3:
    #     bench_max = st.number_input(
    #         "Bench Max $", 
    #         min_value=1, 
    #         max_value=50, 
    #         value=10, 
    #         step=1,
    #         help="Maximum cost allowed for bench players"
    #     )
    # with col4:
    #     top_players_count = st.number_input(
    #         "Top Players per Position", 
    #         min_value=0, 
    #         max_value=50, 
    #         value=0, 
    #         step=1,
    #         help="Number of top players to consider for each position (0 = all players, higher = more variety)"
    #     )
    # 
    # 
    # # Use max_budget as the budget constraint
    # budget = max_budget
    # 
    # # Lineup requirements in compact format
    # st.write(f"**Lineup:** 1 QB, 1 RB, 2 WR, 1 TE, 1 K, 1 DEF, 2 FLEX, 5 BENCH (14 total) | **Budget:** ${min_budget} < cost < ${max_budget}")
    
    # DEBUG: Set default values for hidden settings
    min_budget = 175
    max_budget = 200
    bench_max = 10
    top_players_count = 0
    budget = max_budget
    
    # Buttons under lineup
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 Guess My Tier", use_container_width=True):
            start_new_game(players_df)
            st.rerun()
    with col2:
        if st.button("Clear Score", help="Reset game score", use_container_width=True):
            st.session_state.game_score = {'correct': 0, 'total': 0}
            st.session_state.game_active = False
            st.rerun()
    
    # DEBUG: Hide team generation for now
    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     if st.button("🏈 Generate 2 Teams", use_container_width=True):
    #         optimize_clicked = True
    #     else:
    #         optimize_clicked = False
    # with col3:
    #     if st.button("Clear Teams", help="Clear all generated teams", use_container_width=True):
    #         st.session_state.teams = []
    #         st.rerun()
    
    # DEBUG: Hide team generation for now
    # # Main content - full width
    # st.header("Optimal Teams")
    # 
    # # Show current team count
    # if len(st.session_state.teams) > 0:
    #     st.info(f"📊 {len(st.session_state.teams)} team(s) generated")
    # 
    # if optimize_clicked:
    #     # Pass all settings to optimizer
    #     optimizer = FantasyOptimizer(players_df, budget)
    #     optimizer.min_budget = min_budget  # Add min_budget to optimizer
    #     optimizer.top_players_count = top_players_count  # Add top players count
    #     optimizer.bench_max = bench_max  # Add bench max cost
    #     
    #     with st.spinner("Finding optimal teams..."):
    #         # Generate two teams
    #         team1_players, team1_cost = optimizer.optimize_team_greedy()
    #         team2_players, team2_cost = optimizer.optimize_team_greedy()
    #     
    #     teams_generated = []
    #     if team1_players:
    #         teams_generated.append((team1_players, team1_cost))
    #     if team2_players:
    #         teams_generated.append((team2_players, team2_cost))
    #         
    #     if teams_generated:
    #         # Add teams to session state
    #         timestamp = pd.Timestamp.now().strftime('%H:%M:%S')
    #         for players, cost in teams_generated:
    #             st.session_state.teams.append({
    #                 'players': players,
    #                 'total_cost': cost,
    #                 'timestamp': timestamp
    #             })
    #     else:
    #         st.error("Could not find valid teams within budget constraints.")
    
    optimize_clicked = False  # DEBUG: Disable team generation
    
    # Guess My Tier Game Section
    if st.session_state.game_active and st.session_state.current_player:
        st.header("🎯 Guess My Tier Game")
        
        player = st.session_state.current_player
        score = st.session_state.game_score
        
        # Display score with color coding - keep totals blue
        if score['total'] > 0:
            accuracy = (score['correct'] / score['total']) * 100
            st.info(f"🏆 **Score: {score['correct']}/{score['total']} ({accuracy:.1f}%)**")
        
        # Display player info with colored name based on last result
        if hasattr(st.session_state, 'last_result') and st.session_state.last_result is not None:
            if st.session_state.last_result:
                # Green name for correct
                st.subheader(f"What tier is :green[{player['name']}] ({player['position']})?")
            else:
                # Red name for wrong
                st.subheader(f"What tier is :red[{player['name']}] ({player['position']})?")
        else:
            # Normal color for first question
            st.subheader(f"What tier is {player['name']} ({player['position']})?")
        
        # Debug info display (when debug mode is enabled)
        if st.session_state.debug_mode:
            st.info(f"🔍 **DEBUG:** Position: {player['position']} | Price: ${player['price']} | Tier: {player['tier']}")
        
        if not st.session_state.show_answer:
            # Show tier options as buttons
            tier_options = get_tier_options(player['position'])
            
            # Create buttons for each tier option
            cols = st.columns(len(tier_options))
            for i, tier in enumerate(tier_options):
                with cols[i]:
                    if st.button(f"Tier {tier}", key=f"tier_{tier}", use_container_width=True):
                        # Check if correct and save result for next player's name color
                        if tier == player['tier']:
                            st.session_state.game_score['correct'] += 1
                            st.session_state.last_result = True  # Correct answer
                            st.success(f"✅ Correct! {player['name']} is Tier {player['tier']}")
                        else:
                            st.session_state.last_result = False  # Wrong answer
                            st.error(f"❌ Wrong! {player['name']} is Tier {player['tier']}, not Tier {tier}")
                        
                        st.session_state.game_score['total'] += 1
                        st.session_state.show_answer = True
                        st.rerun()
        else:
            # Show the answer and next game controls
            st.write(f"**Tier:** {player['tier']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎯 Next Player", use_container_width=True):
                    start_new_game(players_df)
                    st.rerun()
            with col2:
                if st.button("📊 End Game", use_container_width=True):
                    st.session_state.game_active = False
                    st.rerun()
        
        st.divider()
    
    # DEBUG: Hide team display for now
    # # Always display existing teams if any
    # if len(st.session_state.teams) > 0:
    #     # Display teams in pairs, side by side
    #     teams_list = list(reversed(st.session_state.teams))
    #     
    #     for i in range(0, len(teams_list), 2):
    #         # Get current pair of teams
    #         team1 = teams_list[i]
    #         team2 = teams_list[i + 1] if i + 1 < len(teams_list) else None
    #         
    #         if team2:  # Two teams to display side by side
    #             col1, col2 = st.columns(2)
    #             
    #             # Team 1 (left column)
    #             with col1:
    #                 team_num = len(st.session_state.teams) - i
    #                 avg_cost = team1['total_cost'] / len(team1['players']) if len(team1['players']) > 0 else 0
    #                 with st.expander(f"Team #{team_num} - ${team1['total_cost']:.0f} (${avg_cost:.1f}/player) ({team1['timestamp']})", expanded=True):
    #                     team_df = pd.DataFrame(team1['players'])
    #                     display_df = team_df[['Role', 'Name', 'Position', 'Price']].copy()
    #                     display_df.columns = ['Seat', 'Player', 'Pos', 'Cost']
    #                     display_df['Cost'] = display_df['Cost'].apply(lambda x: f"${x}")
    #                     display_df.insert(0, '#', range(1, len(display_df) + 1))
    #                     
    #                     st.dataframe(
    #                         display_df,
    #                         use_container_width=True,
    #                         hide_index=True,
    #                         height=522
    #                     )
    #             
    #             # Team 2 (right column)
    #             with col2:
    #                 team_num = len(st.session_state.teams) - i - 1
    #                 avg_cost = team2['total_cost'] / len(team2['players']) if len(team2['players']) > 0 else 0
    #                 with st.expander(f"Team #{team_num} - ${team2['total_cost']:.0f} (${avg_cost:.1f}/player) ({team2['timestamp']})", expanded=True):
    #                     team_df = pd.DataFrame(team2['players'])
    #                     display_df = team_df[['Role', 'Name', 'Position', 'Price']].copy()
    #                     display_df.columns = ['Seat', 'Player', 'Pos', 'Cost']
    #                     display_df['Cost'] = display_df['Cost'].apply(lambda x: f"${x}")
    #                     display_df.insert(0, '#', range(1, len(display_df) + 1))
    #                     
    #                     st.dataframe(
    #                         display_df,
    #                         use_container_width=True,
    #                         hide_index=True,
    #                         height=522
    #                     )
    #         else:  # Single team (full width)
    #             team_num = len(st.session_state.teams) - i
    #             avg_cost = team1['total_cost'] / len(team1['players']) if len(team1['players']) > 0 else 0
    #             with st.expander(f"Team #{team_num} - ${team1['total_cost']:.0f} (${avg_cost:.1f}/player) ({team1['timestamp']})", expanded=True):
    #                 team_df = pd.DataFrame(team1['players'])
    #                 display_df = team_df[['Role', 'Name', 'Position', 'Price']].copy()
    #                 display_df.columns = ['Seat', 'Player', 'Pos', 'Cost']
    #                 display_df['Cost'] = display_df['Cost'].apply(lambda x: f"${x}")
    #                 display_df.insert(0, '#', range(1, len(display_df) + 1))
    #                 
    #                 st.dataframe(
    #                     display_df,
    #                     use_container_width=True,
    #                     hide_index=True,
    #                     height=522
    #                 )

if __name__ == "__main__":
    main()
