
import streamlit as st
import requests
import pandas as pd
import datetime

API_KEY = "your_api_key"  # Replace this with your actual API key
SPORT = "baseball_mlb"
REGION = "us"
MARKETS = ["batter_home_runs", "batter_total_bases", "batter_strikeouts"]

st.set_page_config(page_title="⚾ MLB Prop Line Tracker", layout="wide")
st.title("🔍 MLB Batter Prop Bet Line Tracker")

@st.cache_data(ttl=300)
def get_props(market):
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "regions": REGION,
        "markets": market,
        "apiKey": API_KEY
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        return None, f"API error {res.status_code}: {res.text}"
    return res.json(), None

def extract_props(data, market_name):
    rows = []
    for game in data:
        teams = game.get('teams', ["Unknown", "Unknown"])
        commence = game.get('commence_time', "")
        game_time = datetime.datetime.fromisoformat(commence.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d %I:%M %p") if commence else "N/A"
        for bookmaker in game.get('bookmakers', []):
            for m in bookmaker.get('markets', []):
                if m.get('key') == market_name:
                    for outcome in m.get('outcomes', []):
                        rows.append({
                            "Market": market_name,
                            "Game": " vs ".join(teams),
                            "Game Time": game_time,
                            "Player": outcome.get('name', "N/A"),
                            "Line": outcome.get('point', "N/A"),
                            "Odds": outcome.get('price', "N/A"),
                            "Bookmaker": bookmaker.get('title', "N/A")
                        })
    return pd.DataFrame(rows)

all_frames = []
errors = []
for market in MARKETS:
    data, err = get_props(market)
    if err:
        errors.append(f"{market}: {err}")
    else:
        df = extract_props(data, market)
        if not df.empty:
            all_frames.append(df)

if errors:
    for e in errors:
        st.error(e)

if all_frames:
    full_df = pd.concat(all_frames, ignore_index=True)
    full_df = full_df.sort_values(by="Odds", ascending=False).reset_index(drop=True)
    st.dataframe(full_df, use_container_width=True)

    # High odds alert logic
    st.subheader("🔔 High-Odds Alerts")
    alert_df = full_df[
        ((full_df["Market"] == "batter_home_runs") & (full_df["Odds"] >= 300)) |
        ((full_df["Market"] == "batter_total_bases") & (full_df["Odds"] >= 150)) |
        ((full_df["Market"] == "batter_strikeouts") & (full_df["Odds"] >= 130))
    ]
    if not alert_df.empty:
        st.warning("🚨 High-value props detected:")
        st.dataframe(alert_df, use_container_width=True)
    else:
        st.info("No high-value props at the moment.")
else:
    if not errors:
        st.warning("No props available for selected markets.")
