from datetime import datetime
import streamlit as st
import pandas as pd
import json

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENCODING = 'utf-8'

# Load data
with open(BASE_DIR / 'euro.json', encoding=ENCODING) as f:
    euro_data = json.load(f)

with open(BASE_DIR / 'euro.groups.json', encoding=ENCODING) as f:
    groups_data = json.load(f)

team_df = pd.read_csv(BASE_DIR / 'teams.csv')

group_df = pd.read_csv(BASE_DIR / 'groups.csv')


def calculate_team_points(points_table: dict) -> dict:
    return group_df['Tier1'].map(points_table) + group_df['Tier2'].map(points_table) + group_df['Tier3'].map(points_table)


# Function to calculate points
def calculate_points(data):
    points_table = {}
    date_table = {}

    for round in data["rounds"]:
        for match in round["matches"]:
            # Ensure 'score' and 'ft' keys exist in the match
            if 'score' in match and 'ft' in match['score']:
                score1 = match['score']['ft'][0]
                score2 = match['score']['ft'][1]
                team1 = match['team1']["name"]
                team2 = match['team2']["name"]
                
                if team1 not in points_table:
                    points_table[team1] = 0
                if team2 not in points_table:
                    points_table[team2] = 0

                if score1 > score2:
                    points_table[team1] += 3
                elif score1 < score2:
                    points_table[team2] += 3
                else:
                    points_table[team1] += 1
                    points_table[team2] += 1
            else:
                print(f"Skipping match due to missing 'ft' score: {match}")
            
            date = datetime.strptime(match["date"], "%Y-%m-%d")
            date_table[date] = calculate_team_points(points_table)

    return pd.DataFrame(date_table)

# Calculate points
date_df = calculate_points(euro_data)

# Load team config and calc points
group_df['Total Points'] = date_df[date_df.columns[-1]]
group_df.sort_values(by='Total Points', ascending=False, inplace=True)


# Display results
st.title(f"Euro 2024 Points Table {datetime.today().strftime('%d-%m-%Y')}")
st.dataframe(group_df, hide_index=True)

# Flip and display
date_df['Group'] = group_df.Group
date_df.set_index('Group', inplace=True)
graph_df = date_df.transpose()
st.subheader("Points over time")
st.line_chart(graph_df)

st.subheader("Teams")
st.dataframe(team_df, hide_index=True)