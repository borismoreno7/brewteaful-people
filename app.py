import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime


st.set_page_config(
    page_title="Brewteaful People - Tea League",
    page_icon="🍵",
    layout="wide"
)

def get_teas():
    with sqlite3.connect("tea_league.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM teas ORDER BY name")
        return [row[0] for row in cursor.fetchall()]

st.title("🍵 Brewteaful People")
st.caption("THE OFFICIAL TEA LEAGUE")

def get_standings():
    with sqlite3.connect("tea_league.db") as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT id, name FROM teas ORDER BY name")
        teas = cursor.fetchall()

        cursor.execute("""
            SELECT tea1_id, tea2_id, tea1_votes, tea2_votes
            FROM matches
        """)
        all_matches = cursor.fetchall()

    standings = []

    for tea_id, tea_name in teas:
        wins = 0
        losses = 0
        ties = 0
        votes_for = 0
        votes_against = 0

        for tea1_id, tea2_id, votes1, votes2 in all_matches:
            if tea_id == tea1_id:
                my_votes = votes1
                opponent_votes = votes2
            elif tea_id == tea2_id:
                my_votes = votes2
                opponent_votes = votes1
            else:
                continue

            votes_for += my_votes
            votes_against += opponent_votes

            if my_votes > opponent_votes:
                wins += 1
            elif my_votes < opponent_votes:
                losses += 1
            else:
                ties += 1

        total_matches = wins + losses + ties
        points = wins * 3 + ties
        vote_difference = votes_for - votes_against

        if total_matches > 0:
            win_percentage = wins / total_matches * 100
        else:
            win_percentage = 0

        standings.append({
            "Tea": tea_name,
            "Matches": total_matches,
            "W": wins,
            "L": losses,
            "T": ties,
            "PTS": points,
            "Votes For": votes_for,
            "Votes Against": votes_against,
            "+/-": vote_difference,
            "Win %": round(win_percentage, 1)
        })

    standings.sort(
        key=lambda tea: (
            tea["PTS"],
            tea["+/-"],
            tea["Votes For"]
        ),
        reverse=True
    )

    for position, tea in enumerate(standings, start=1):
        tea["Pos"] = position

    return standings

def get_match_history():
    with sqlite3.connect("tea_league.db") as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                m.date,
                t1.name,
                m.tea1_votes,
                t2.name,
                m.tea2_votes
            FROM matches m
            JOIN teas t1 ON m.tea1_id = t1.id
            JOIN teas t2 ON m.tea2_id = t2.id
            ORDER BY m.date DESC, m.rowid DESC
        """)

        matches = cursor.fetchall()

    history = []

    for number, (date, tea1, votes1, tea2, votes2) in enumerate(matches, start=1):

        if votes1 > votes2:
            winner = tea1
        elif votes2 > votes1:
            winner = tea2
        else:
            winner = "TIE"

        match_date = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = match_date.strftime("%Y-%m-%d %a")

        history.append({
            "No.": number,
            "Date / Day": formatted_date,
            "Tea 1": tea1,
            "Votes 1": votes1,
            "Tea 2": tea2,
            "Votes 2": votes2,
            "Winner": winner
        })

    return history

def get_head_to_head(tea1, tea2):
    with sqlite3.connect("tea_league.db") as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                m.date,
                t1.name,
                m.tea1_votes,
                t2.name,
                m.tea2_votes
            FROM matches m
            JOIN teas t1 ON m.tea1_id = t1.id
            JOIN teas t2 ON m.tea2_id = t2.id
            WHERE
                (t1.name = ? AND t2.name = ?)
                OR
                (t1.name = ? AND t2.name = ?)
            ORDER BY m.date DESC, m.rowid DESC
        """, (tea1, tea2, tea2, tea1))

        matches = cursor.fetchall()

    history = []
    tea1_wins = 0
    tea2_wins = 0
    ties = 0
    tea1_votes = 0
    tea2_votes = 0

    for date, name1, votes1, name2, votes2 in matches:

        if name1 == tea1:
            first_votes = votes1
            second_votes = votes2
        else:
            first_votes = votes2
            second_votes = votes1

        tea1_votes += first_votes
        tea2_votes += second_votes

        if first_votes > second_votes:
            tea1_wins += 1
            winner = tea1
        elif second_votes > first_votes:
            tea2_wins += 1
            winner = tea2
        else:
            ties += 1
            winner = "TIE"

        match_date = datetime.strptime(date, "%Y-%m-%d")

        history.append({
            "Date / Day": match_date.strftime("%Y-%m-%d %a"),
            tea1: first_votes,
            tea2: second_votes,
            "Winner": winner
        })

    return {
        "matches": len(matches),
        "tea1_wins": tea1_wins,
        "tea2_wins": tea2_wins,
        "ties": ties,
        "tea1_votes": tea1_votes,
        "tea2_votes": tea2_votes,
        "history": history
    }

st.markdown("Eric’s Legacy, now a Tea League")

total_teas = len(get_teas())
total_matches = len(get_match_history())

col1, col2 = st.columns(2)

with col1:
    st.metric("🍵 Teas Competing", total_teas)

with col2:
    st.metric("🏆 Matches Played", total_matches)

st.divider()

st.header("League Standings")

standings = get_standings()

st.dataframe(
    standings,
    column_order=[
        "Pos",
        "Tea",
        "Matches",
        "W",
        "L",
        "T",
        "PTS",
        "Votes For",
        "Votes Against",
        "+/-",
        "Win %"
    ],
    hide_index=True,
    width="stretch"
)

st.header("Match History")

match_history = get_match_history()

if match_history:
    st.dataframe(
        match_history,
        column_order=[
            "No.",
            "Date / Day",
            "Tea 1",
            "Votes 1",
            "Tea 2",
            "Votes 2",
            "Winner"
        ],
        hide_index=True,
        width="stretch"
    )
else:
    st.info("No matches have been registered yet.")

st.header("Head-to-Head")
col1, col2 = st.columns(2)
teas = get_teas()

with col1:
    tea1 = st.selectbox(
        "Select Tea 1",
        teas,
        index=0
    )

with col2:
    tea2 = st.selectbox(
        "Select Tea 2",
        teas,
        index=1
    )

if tea1 == tea2:
    st.warning("Please select two different teas.")

else:
    results = get_head_to_head(tea1, tea2)

    st.subheader(f"{tea1} vs {tea2}")

    if results["matches"] == 0:
        st.info("These teas have not faced each other yet.")

    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                f"{tea1} Wins",
                results["tea1_wins"]
            )

        with col2:
            st.metric(
                "Ties",
                results["ties"]
            )

        with col3:
            st.metric(
                f"{tea2} Wins",
                results["tea2_wins"]
            )

        st.write(f"**Total Matches:** {results['matches']}")

        st.write(
            f"**Total Votes:** "
            f"{tea1}: {results['tea1_votes']} | "
            f"{tea2}: {results['tea2_votes']}"
        )

        st.subheader("Head-to-Head History")

        st.dataframe(
            results["history"],
            hide_index=True,
            width="stretch"
        )

st.divider()

st.divider()

st.header("Our Teas")

teas = get_teas()

st.write(f"Total registered teas: {len(teas)}")

selected_tea = st.selectbox(
    "Select a tea to explore its statistics",
    teas,
    key="tea_profile"
)

st.subheader(f"🍵 {selected_tea}")

# Find the selected tea in the league standings
tea_stats = next(
    (tea for tea in standings if tea["Tea"] == selected_tea),
    None
)

if tea_stats:

    # First row: League position, matches and points
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("League Position", f"#{tea_stats['Pos']}")

    with col2:
        st.metric("Matches Played", tea_stats["Matches"])

    with col3:
        st.metric("Points", tea_stats["PTS"])

    # Second row: Wins, losses and ties
    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Wins", tea_stats["W"])

    with col5:
        st.metric("Losses", tea_stats["L"])

    with col6:
        st.metric("Ties", tea_stats["T"])

    # Third row: Voting statistics
    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric("Votes For", tea_stats["Votes For"])

    with col8:
        st.metric("Votes Against", tea_stats["Votes Against"])

    with col9:
        st.metric("Win Rate", f"{tea_stats['Win %']}%")
    
    # Individual match history
    st.subheader("Match History")

    tea_history = [
        match for match in match_history
        if match["Tea 1"] == selected_tea
        or match["Tea 2"] == selected_tea
    ]

    if tea_history:
        st.dataframe(
            tea_history,
            column_order=[
                "Date / Day",
                "Tea 1",
                "Votes 1",
                "Tea 2",
                "Votes 2",
                "Winner"
            ],
            hide_index=True,
            width="stretch"
        )
    else:
        st.info("This tea has not played any matches yet.")