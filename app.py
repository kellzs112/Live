
import streamlit as st
import requests
import pandas as pd

API_KEY = "5ef652dc32b18a607494972c929cd999"  # Replace with your actual API key
SPORT = "baseball_mlb"
REGION = "us"
MARKET = "h2h"  # Safe market: moneyline (head-to-head)

st.set_page_config(page_title="Safe Line Tracker Test", layout="wide")
st.title("🧪 Safe Line Tracker Test (H2H Market)")

@st.cache_data(ttl=300)
def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds?regions={REGION}&markets={MARKET}&apiKey={API_KEY}"
    res = requests.get(url)
    if res.status_code != 200:
        st.error(f"API error: {res.status_code} - {res.text}")
        return []
    return res.json()

def display_odds(odds_data):
    rows = []
    for game in odds_data:
        for bookmaker in game['bookmakers']:
            for market in bookmaker['markets']:
                for outcome in market['outcomes']:
                    rows.append({
                        "Game": " vs ".join(game['teams']),
                        "Team": outcome['name'],
                        "Odds": outcome['price'],
                        "Bookmaker": bookmaker['title']
                    })
    return pd.DataFrame(rows)

data = get_odds()

if data:
    df = display_odds(data)
    if not df.empty:
        df = df.sort_values(by="Odds", ascending=False).reset_index(drop=True)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No odds data found.")
else:
    st.error("Failed to fetch data.")
