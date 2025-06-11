
import streamlit as st
import requests
import pandas as pd
import datetime

API_KEY = "5ef652dc32b18a607494972c929cd999"  # Replace with your actual API key
SPORT = "baseball_mlb"
REGION = "us"
MARKETS = ["player_home_runs", "player_total_bases", "player_strikeouts"]

st.set_page_config(page_title="📈 Prop Line Tracker", layout="wide")
st.title("📊 MLB Prop Bet Line Tracker")

@st.cache_data(ttl=300)
def get_odds(market):
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds?regions={REGION}&markets={market}&apiKey={API_KEY}"
    res = requests.get(url)
    if res.status_code != 200:
        return None, f"API error {res.status_code}: {res.text}"
    return res.json(), None

def extract_props(data, market_name):
    rows = []
    for game in data:
        teams = game.get('teams', ["Unknown", "Unknown"])
        home_team = game.get('home_team', "Unknown")
        commence = game.get('commence_time', "")
        commence_time = datetime.datetime.fromisoformat(commence.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d %I:%M %p") if commence else "N/A"

        for bookmaker in game.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                for outcome in market.get('outcomes', []):
                    rows.append({
                        "Prop Market": market_name,
                        "Game": " vs ".join(teams),
                        "Home Team": home_team,
                        "Player": outcome.get('name', "N/A"),
                        "Line": outcome.get('point', "N/A"),
                        "Odds": outcome.get('price', "N/A"),
                        "Bookmaker": bookmaker.get('title', "N/A"),
                        "Game Time": commence_time
                    })
    return pd.DataFrame(rows)

all_data = []
for market in MARKETS:
    data, error = get_odds(market)
    if error:
        st.error(f"{market}: {error}")
        continue
    props_df = extract_props(data, market)
    if not props_df.empty:
        all_data.append(props_df)

if all_data:
    full_df = pd.concat(all_data, ignore_index=True)
    # Sort to surface high payout lines
    full_df = full_df.sort_values(by="Odds", ascending=False).reset_index(drop=True)
    st.dataframe(full_df, use_container_width=True)

    # 💡 Simple alert logic
    st.subheader("🔔 Potential Value Alerts")
    alert_df = full_df[
        ((full_df["Prop Market"] == "player_home_runs") & (full_df["Odds"] >= 300)) |
        ((full_df["Prop Market"] == "player_total_bases") & (full_df["Odds"] >= 150)) |
        ((full_df["Prop Market"] == "player_strikeouts") & (full_df["Odds"] >= 130))
    ]
    if not alert_df.empty:
        st.warning("🚨 High-odds opportunities detected:")
        st.dataframe(alert_df, use_container_width=True)
    else:
        st.info("No high-odds props detected right now.")
else:
    st.error("No props available for selected markets.")
