import streamlit as st
import csv
import random
import os

# ------------------ Load Teams from CSV ------------------
@st.cache_data
def load_teams_from_csv(filename):
    teams = []
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                try:
                    team_name = row[0]
                    rating = float(row[1])
                    teams.append((team_name, rating))
                except:
                    continue
    except FileNotFoundError:
        st.error("CSV file not found. Make sure 'teams_ratings.csv' is in the same folder.")
    return teams

# ------------------ Setup Game State ------------------
def initialize_game():
    st.session_state.round = 0
    st.session_state.score = 0
    st.session_state.completed = False

# ------------------ App UI ------------------
st.set_page_config(page_title="KenPom Guessing Game", page_icon="🏀")
st.title("🏀 KenPom Guessing Game")
st.markdown("Can you guess which team has the higher KenPom rating?")

# Load CSV
teams = load_teams_from_csv("teams_ratings.csv")
if not teams:
    st.stop()

# Difficulty Selection
difficulty = st.selectbox("Select Difficulty", [
    "Extremely Hard (diff < 1)", "Hard (diff < 2.5)", 
    "Medium (diff < 4.5)", "Easy (diff < 8.5)"
])

diff_map = {
    "Extremely Hard (diff < 1)": (1, -43),
    "Hard (diff < 2.5)": (2.5, -10),
    "Medium (diff < 4.5)": (4.5, 0),
    "Easy (diff < 8.5)": (8.5, 10)
}
difference, min_rating = diff_map[difficulty]

# Round count
rounds = st.selectbox("How many rounds would you like to play?", [5, 8, 10, 15, 20])

# Filter teams by min_rating
teams = [team for team in teams if team[1] >= min_rating]
random.shuffle(teams)

# Initialize session state if needed
if "round" not in st.session_state:
    initialize_game()

# ------------------ Main Game Logic ------------------
if not st.session_state.completed:
    if st.session_state.round < rounds:
        # Pick two teams that meet difficulty criteria
        while True:
            team1, rating1 = random.choice(teams)
            team2, rating2 = random.choice(teams)
            if team1 != team2 and abs(rating1 - rating2) <= difference:
                break

        st.subheader(f"Round {st.session_state.round + 1} of {rounds}")
        choice = st.radio("Which team has the higher rating?", [team1, team2], key=f"choice_{st.session_state.round}")
        if st.button("Submit", key=f"submit_{st.session_state.round}"):
            correct_team = team1 if rating1 > rating2 else team2
            if choice == correct_team:
                st.success(f"✅ Correct! {correct_team} has the higher rating.")
                st.session_state.score += 1
            else:
                st.error(f"❌ Oops! The correct answer was {correct_team}.")
            st.session_state.round += 1
            st.experimental_rerun()
    else:
        st.session_state.completed = True
        st.balloons()

# ------------------ Game Over Section ------------------
if st.session_state.completed:
    st.header("🎉 Game Over!")
    st.write(f"You got **{st.session_state.score} / {rounds}** correct.")

    if st.button("🔁 Play Again"):
        initialize_game()
        st.experimental_rerun()

