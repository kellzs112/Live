
import streamlit as st
import requests
import pandas as pd
import time

API_KEY = "your_api_key"  # Replace with your actual API key
SPORT = "baseball_mlb"
REGION = "us"
MARKET = "player_props"

st.set_page_config(page_title="Live HR Line Tracker", layout="wide")
st.title("💣 Live HR Prop Line Tracker")

@st.cache_data(ttl=300)
def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds?regions={REGION}&markets={MARKET}&apiKey={API_KEY}"
    res = requests.get(url)
    if res.status_code != 200:
        st.error(f"API error: {res.status_code}")
        return []
    return res.json()

def display_hr_odds(odds_data):
    rows = []
    for game in odds_data:
        for bookmaker in game['bookmakers']:
            for market in bookmaker['markets']:
                if "home_run" in market['key']:  # Filter for HR-related props
                    for outcome in market['outcomes']:
                        rows.append({
                            "Game": " vs ".join(game['teams']),
                            "Player": outcome['name'],
                            "HR Odds": outcome['price'],
                            "Bookmaker": bookmaker['title'],
                        })
    return pd.DataFrame(rows)

data = get_odds()

if data:
    df = display_hr_odds(data)
    if not df.empty:
        df = df.sort_values(by="HR Odds", ascending=False).reset_index(drop=True)
        st.dataframe(df, use_container_width=True)
        # Show top line movement if historical data were logged
        st.info("🧠 Tip: Watch for big drops in HR odds—may indicate sharp action or lineup changes.")
    else:
        st.warning("No home run props found right now.")
else:
    st.error("Failed to fetch data.")
