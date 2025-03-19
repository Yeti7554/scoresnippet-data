import requests
import pandas as pd
from tabulate import tabulate

def get_fpl_data():
    # Base URL for FPL API
    base_url = "https://fantasy.premierleague.com/api/"
    
    # Get basic player data
    players_url = base_url + "bootstrap-static/"
    response = requests.get(players_url)
    data = response.json()
    
    # Get the latest gameweek
    current_gw = next(gw for gw in data['events'] if gw['is_current'])['id']
    
    # Create a DataFrame with player information
    players_df = pd.DataFrame(data['elements'])
    
    # Select relevant columns and rename them
    selected_columns = {
        'web_name': 'Player',
        'now_cost': 'Cost',
        'form': 'Form',
        'total_points': 'Total Points',
        'team': 'Team',
        'team_code': 'Team_Code',  # We'll need this temporarily
        'next_opponent_team': 'Next_Opponent'  # Add next opponent
    }
    
    df = players_df[selected_columns.keys()].rename(columns=selected_columns)
    
    # Convert cost to actual value (divide by 10)
    df['Cost'] = df['Cost'] / 10
    
    # Convert form to float
    df['Form'] = df['Form'].astype(float)
    
    # Get team names
    teams = pd.DataFrame(data['teams'])
    team_names = dict(zip(teams['id'], teams['name']))
    
    # Map both team and next opponent to their actual names
    df['Team'] = df['Team'].map(team_names)
    df['Next_Opponent'] = df['Next_Opponent'].map(team_names)
    
    # Drop the temporary Team_Code column
    df = df.drop('Team_Code', axis=1)
    
    # Sort by form (descending)
    df = df.sort_values('Form', ascending=False)
    
    return df, current_gw

def main():
    try:
        # Get the data
        df, current_gw = get_fpl_data()
        
        # Print the table
        print(f"\nLatest FPL Data - Gameweek {current_gw}")
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 