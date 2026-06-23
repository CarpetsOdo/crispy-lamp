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
leaders_table.index += 1

# Add 1st and 2nd place emojis to Group Leader names
for idx in leaders_table.index:
    if idx == 1:
        leaders_table.at[idx, "Leader"] = f"🥇 {leaders_table.at[idx, 'Leader']}"
    elif idx == 2:
        leaders_table.at[idx, "Leader"] = f"🥈 {leaders_table.at[idx, 'Leader']}"

# Process Global Rankings
if not all_players_df.empty:
    all_players_table = all_players_df.sort_values(by="Points", ascending=False).reset_index(drop=True)
    all_players_table.index += 1
    top_3_overall = all_players_table.head(3).copy()
else:
    all_players_table = pd.DataFrame()
    top_3_overall = pd.DataFrame()


# -----------------------------
# DYNAMIC PODIUM GENERATOR
# -----------------------------
if not top_3_overall.empty and len(top_3_overall) == 3:
    st.subheader("🏆 Overall Top 3 Podium")
    
    p1 = top_3_overall.iloc[0]
    p2 = top_3_overall.iloc[1]
    p3 = top_3_overall.iloc[2]
    
    fig_pod, ax_pod = plt.subplots(figsize=(8, 2.5))
    
    x_positions = [1, 2, 3]
    heights = [0.8, 1.4, 1.1]
    podium_colors = ["#cd7f32", "#FFD700", "#c0c0c0"]
    
    bars = ax_pod.bar(x_positions, heights, color=podium_colors, width=0.7, edgecolor='#222222', linewidth=1.2)
    
    ax_pod.set_xlim(0.4, 3.6)
    ax_pod.set_ylim(0, 2.3)
    ax_pod.axis('off')
    
    # 1st Place (Center - X=2)
    ax_pod.text(2, 1.45, r"$\bigstar$", fontsize=16, color="#D4AF37", ha='center')
    ax_pod.text(2, 1.62, p1['Player'].upper(), fontsize=13, weight='black', color='#111111', ha='center')
    ax_pod.text(2, 1.80, f"{p1['Points']} pts", fontsize=10, weight='bold', color='#444444', ha='center')
    ax_pod.text(2, 0.75, "1st", fontsize=16, color='#222222', weight='bold', ha='center')
    # Team Name centered inside the 1st place block (Y around 0.3)
    ax_pod.text(2, 0.25, f"{p1['Team']}", fontsize=8.5, color='#ffffff', weight='bold', style='italic', ha='center')

    # 2nd Place (Right - X=3)
    ax_pod.text(3, 1.15, r"$\bigstar$", fontsize=13, color="#999999", ha='center')
    ax_pod.text(3, 1.32, p2['Player'].upper(), fontsize=11, weight='black', color='#111111', ha='center')
    ax_pod.text(3, 1.50, f"{p2['Points']} pts", fontsize=9, weight='bold', color='#444444', ha='center')
    ax_pod.text(3, 0.60, "2nd", fontsize=14, color='#222222', weight='bold', ha='center')
    # Team Name centered inside the 2nd place block (Y around 0.2)
    ax_pod.text(3, 0.20, f"{p2['Team']}", fontsize=8, color='#ffffff', weight='bold', style='italic', ha='center')

    # 3rd Place (Left - X=1)
    ax_pod.text(1, 0.85, r"$\bigstar$", fontsize=13, color="#a05a2c", ha='center')
    ax_pod.text(1, 1.02, p3['Player'].upper(), fontsize=11, weight='black', color='#111111', ha='center')
    ax_pod.text(1, 1.20, f"{p3['Points']} pts", fontsize=9, weight='bold', color='#444444', ha='center')
    ax_pod.text(1, 0.45, "3rd", fontsize=14, color='#222222', weight='bold', ha='center')
    # Team Name centered inside the 3rd place block (Y around 0.15)
    ax_pod.text(1, 0.15, f"{p3['Team']}", fontsize=8, color='#ffffff', weight='bold', style='italic', ha='center')

    plt.tight_layout()
    # High DPI (300) removes all blurriness
    st.pyplot(fig_pod, use_container_width=True, dpi=300)
    plt.close(fig_pod)


# Helper function to inject progressively larger font sizes for ranking tables
def apply_progressive_fonts(row):
    if row.name == 1:
        return ['font-size: 18px; font-weight: bold;'] * len(row)
    elif row.name == 2:
        return ['font-size: 15px; font-weight: bold;'] * len(row)
    return [''] * len(row)


# -----------------------------
# SIDE-BY-SIDE DISPLAY
# -----------------------------
st.markdown("---")
col1, col2 = st.columns([1, 1])

# LEFT SIDE: BEST PLAYER PER TEAM
with col1:
    st.subheader("🥇 Best Player per Team")
    styled_leaders = leaders_table.style.apply(apply_progressive_fonts, axis=1)
    st.dataframe(styled_leaders, use_container_width=True, height=180)

# RIGHT SIDE: COMPACT CHART
with col2:
    st.subheader("📊 Team Scores")

    top_team = df.sort_values(by="Points", ascending=False).iloc[0]["Team"]

    fig, ax = plt.subplots(figsize=(5, 2.5))

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
