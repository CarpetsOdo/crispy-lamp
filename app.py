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

# Process Group Leaderboards
leaders_table = leaders_df.sort_values(by="Points", ascending=False).reset_index(drop=True)

# Process Global Rankings
if not all_players_df.empty:
    all_players_table = all_players_df.sort_values(by="Points", ascending=False).reset_index(drop=True)
    all_players_table.index += 1
    top_3_overall = all_players_table.head(3).copy()
else:
    all_players_table = pd.DataFrame()
    top_3_overall = pd.DataFrame()


# -----------------------------
# MOBILE-OPTIMIZED PODIUM (1st, 2nd, 3rd)
# -----------------------------
if not top_3_overall.empty and len(top_3_overall) == 3:
    st.subheader("🏆 Top 3 Podium")
    
    p1 = top_3_overall.iloc[0]
    p2 = top_3_overall.iloc[1]
    p3 = top_3_overall.iloc[2]
    
    pod_col1, pod_col2, pod_col3 = st.columns([1, 1, 1])
    
    # 1st Place
    with pod_col1:
        st.markdown(f"## 👑 **{p1['Player'].upper()}**")
        with st.container(border=True):
            st.metric(label="🥇 1st Place", value=f"{p1['Points']} pts")
            st.caption(f"**_{p1['Team']}_**")
            
    # 2nd Place
    with pod_col2:
        st.write("")  
        st.write("")
        st.markdown(f"### **{p2['Player'].upper()}**")
        with st.container(border=True):
            st.metric(label="🥈 2nd Place", value=f"{p2['Points']} pts")
            st.caption(f"_{p2['Team']}_")
            
    # 3rd Place
    with pod_col3:
        st.write("")  
        st.write("")
        st.write("")
        st.write("")
        st.markdown(f"#### **{p3['Player'].upper()}**")
        with st.container(border=True):
            st.metric(label="🥉 3rd Place", value=f"{p3['Points']} pts")
            st.caption(f"_{p3['Team']}_")


# -----------------------------
# VERTICAL MOBILE STACK
# -----------------------------
st.markdown("---")

# SECTION A: BEST PLAYER PER TEAM (No index numbers)
st.subheader("🏆 Best Player per Team")
# Using data_editor with hide_index=True completely drops the numbers on the left
st.data_editor(leaders_table, use_container_width=True, hide_index=True, disabled=True)

st.markdown("---")

# SECTION B: TEAM SCORES GRAPH
st.subheader("📊 Team Scores")

top_team = df.sort_values(by="Points", ascending=False).iloc[0]["Team"]

fig, ax = plt.subplots(figsize=(6, 3)) # Slightly wider aspect ratio for vertical blocks

colors = []
for team in df_chart["Team"]:
    if team == top_team:
        colors.append("#FFD700")
    else:
        colors.append(TEAM_COLORS.get(team, "#cccccc"))

bars = ax.barh(df_chart["Team"], df_chart["Points"], color=colors, height=0.45)

ax.set_xlabel("")
ax.set_ylabel("")
ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
ax.tick_params(left=False, bottom=False, labelsize=10)

max_val = df_chart["Points"].max()

for bar in bars:
    width = bar.get_width()
    ax.text(
        width + max_val * 0.01,
        bar.get_y() + bar.get_height() / 2,
        f"{int(width)}",
        va='center',
        fontsize=10,
        weight='bold'
    )

plt.tight_layout()
st.pyplot(fig, use_container_width=True, dpi=300)
plt.close(fig)


# -----------------------------
# DISPLAY: ALL PLAYERS RANKING
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
