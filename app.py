import requests
import csv
from datetime import datetime  # For date formatting


# Fetch general player data
base_url = "https://fantasy.premierleague.com/api/"
response = requests.get(base_url + "bootstrap-static/")
data = response.json()

# Extract player list
players = data['elements']
teams = {team['id']: team['name'] for team in data['teams']}
positions = {pos['id']: pos['singular_name'] for pos in data['element_types']}

# CSV file setup
headers = [
    "player_id", "first_name", "second_name", "team", "position", "cost", "game_week",
    "date", "points", "goals_scored", "assists", "minutes", "clean_sheets"
]
with open("data.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    # Loop through each player
    for player in players:
        player_id = player['id']
        first_name = player['first_name']
        second_name = player['second_name']
        team = teams[player['team']]
        position = positions[player['element_type']]
        cost = player['now_cost'] / 10  # Convert cost to millions

        # Fetch player-specific data
        player_response = requests.get(base_url + f"element-summary/{player_id}/")
        player_data = player_response.json()
        
        # Extract game week history
        for history in player_data['history']:
            # Convert the date format
            original_date = history['kickoff_time']  # Example: 2024-08-11T12:30:00Z
            formatted_date = datetime.strptime(original_date[:10], "%Y-%m-%d").strftime("%d/%m/%Y")

            writer.writerow([
                player_id,
                first_name,
                second_name,
                team,
                position,
                cost,
                history['round'],  # Game week
                formatted_date,  # Date of the game
                history['total_points'],
                history['goals_scored'],
                history['assists'],
                history['minutes'],
                history['clean_sheets']
            ])

# Define the cost bins for each position
bins = {
    "Defender": {"low": (3.9, 4.9), "medium": (4.9, 5.9), "high": (5.9, 6.9)},
    "Forward": {"low": (4.5, 8.03), "medium": (8.03, 11.57), "high": (11.57, 15.1)},
    "Goalkeeper": {"low": (3.9, 4.43), "medium": (4.43, 4.97), "high": (4.97, 5.5)},
    "Midfielder": {"low": (4.4, 7.3), "medium": (7.3, 10.2), "high": (10.2, 13.1)},
}

# Function to classify cost into bins
def classify_cost(row):
    position = row["position"]
    cost = row["cost"]
    if position in bins:
        if bins[position]["low"][0] <= cost <= bins[position]["low"][1]:
            return "Low"
        elif bins[position]["medium"][0] < cost <= bins[position]["medium"][1]:
            return "Medium"
        elif bins[position]["high"][0] < cost <= bins[position]["high"][1]:
            return "High"
    return "Unknown"  # Default for positions not in the bins

import pandas as pd
df = pd.read_csv('data.csv')

df["cost_bin"] = df.apply(classify_cost, axis=1)

df.to_csv('data.csv', index=False)