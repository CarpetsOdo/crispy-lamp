import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# -----------------------------
# CONFIG
# -----------------------------
GROUPS = {
    "Alfacinhas FC": "https://www.kicktipp.pt/alfacinhas-fc/ranking",
    "Os Magmáticos": "https://www.kicktipp.pt/os-magmaticos/ranking",
    "Treinadores de Bancada": "https://www.kicktipp.pt/treinadores-de-bancada/ranking"
}

TEAM_COLORS = {
    "Alfacinhas FC": "#1f77b4",
    "Os Magmáticos": "#d62728",
    "Treinadores de Bancada": "#2ca02c"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}


# -----------------------------
# SCRAPER
# -----------------------------
def get_group_data(url, team_name):
    players = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select("table tr")

        for row in rows:
            cols = row.find_all("td")

            if len(cols) >= 4:
                try:
                    name = cols[1].text.strip()
                    
                    if name.lower() == "admin":
                        continue
                        
                    pts_str = cols[-1].text.strip().replace(".", "").replace(",", "")
                    pts = int(pts_str)

                    players.append({
                        "Team": team_name,
                        "Player": name,
                        "Points": pts
                    })
                except Exception as e:
                    pass

        return players
    except:
        return []


# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(page_title="Kicktipp Team Battle", layout="wide")

st.title("🏆 Kicktipp Team Battle")

if st.button("🔄 Refresh"):
    st.rerun()


# -----------------------------
# GET DATA
# -----------------------------
all_players_list = []
team_results = []
leader_results = []

for team, url in GROUPS.items():
    group_players = get_group_data(url, team)
    
    if group_players:
        all_players_list.extend(group_players)
        
        total_pts = sum(p["Points"] for p in group_players)
        team_results.append({
            "Team": team,
            "Points": total_pts
        })
        
        leader = group_players[0]
        leader_results.append({
            "Team": team,
            "Leader": leader["Player"],
            "Points": leader["Points"]
        })
    else:
        team_results.append({"Team": team, "Points": 0})
        leader_results.append({"Team": team, "Leader": "Error", "Points": 0})

df = pd.DataFrame(team_results)
leaders_df = pd.DataFrame(leader_results)
all_players_df = pd.DataFrame(all_players_list)

if len(df) == 0:
    st.error("No data available")
    st.stop()

# Sort DataFrames
df_chart = df.sort_values(by="Points", ascending=True)

# Process Leaderboards
leaders_table = leaders_df.sort_values(by="Points", ascending=False).reset_index(drop=True)
leaders_table.index += 1

if not all_players_df.empty:
    all_players_table = all_players_df.sort_values(by="Points", ascending=False).reset_index(drop=True)
    all_players_table.index += 1
else:
    all_players_table = pd.DataFrame()


# Helper function to highlight the top 2 elements
def highlight_winners(row):
    # row.name holds the dataframe index integer
    if row.name in [1, 2]:
        return ['background-color: #fff3cd; font-weight: bold; border: 1px solid #ffeeba;'] * len(row)
    return [''] * len(row)


# -----------------------------
# DISPLAY: 1. BEST PLAYERS (FIRST)
# -----------------------------
st.subheader("🥇 Best Player per Team")
styled_leaders = leaders_table.style.apply(highlight_winners, axis=1)
st.dataframe(styled_leaders, use_container_width=True, height=180)

st.markdown("---")

# -----------------------------
# DISPLAY: 2. SMALLER CHART
# -----------------------------
st.subheader("📊 Team Scores")

# Determine overall leader for coloring rules
top_team = df.sort_values(by="Points", ascending=False).iloc[0]["Team"]

# Scaled down sizes for a significantly more compact graph image footprint
fig, ax = plt.subplots(figsize=(5, 2.2))

colors = []
for team in df_chart["Team"]:
    if team == top_team:
        colors.append("#FFD700")  # Gold for winner
    else:
        colors.append(TEAM_COLORS.get(team, "#cccccc"))

bars = ax.barh(df_chart["Team"], df_chart["Points"], color=colors, height=0.45)

ax.set_xlabel("")
ax.set_ylabel("")
ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
ax.tick_params(left=False, bottom=False, labelsize=9)

max_val = df_chart["Points"].max()

for bar in bars:
    width = bar.get_width()
    ax.text(
        width + max_val * 0.01,
        bar.get_y() + bar.get_height() / 2,
        f"{int(width)}",
        va='center',
        fontsize=9,
        weight='bold'
    )

plt.tight_layout()
# Control display width on screen using streamlits' width configuration parameters
st.pyplot(fig, use_container_width=False)


# -----------------------------
# DISPLAY: 3. ALL PLAYERS RANKING
# -----------------------------
st.markdown("---")
st.subheader("👥 All Players Ranking")
if not all_players_table.empty:
    st.table(all_players_table)
else:
    st.warning("No player data could be retrieved.")


# -----------------------------
# FOOTER
# -----------------------------
st.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")

# -----------------------------
# AUTO REFRESH
# -----------------------------
st.markdown(
    '<meta http-equiv="refresh" content="60">',
    unsafe_allow_html=True
)
