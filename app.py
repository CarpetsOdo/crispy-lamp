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

# Add 1st and 2nd place emojis to Group Leader names dynamically based on sorted rank
for idx in leaders_table.index:
    if idx == 1:
        leaders_table.at[idx, "Leader"] = f"🥇 {leaders_table.at[idx, 'Leader']}"
    elif idx == 2:
        leaders_table.at[idx, "Leader"] = f"🥈 {leaders_table.at[idx, 'Leader']}"

# Process Global Rankings
if not all_players_df.empty:
    all_players_table = all_players_df.sort_values(by="Points", ascending=False).reset_index(drop=True)
    all_players_table.index += 1
    
    # Extract the top 3 overall players
    top_3_overall = all_players_table.head(3).copy()
else:
    all_players_table = pd.DataFrame()
    top_3_overall = pd.DataFrame()

# -----------------------------
# DYNAMIC PODIUM GENERATION
# -----------------------------
if not top_3_overall.empty and len(top_3_overall) == 3:
    st.subheader("🏆 Overall Top 3 Podium")
    # Reference the static podium graphic for visual style inspiration
    st.image("image_0.png", caption="Overall Podium Style Reference (Static)", use_container_width=True)
    
    # Define player details for podium places
    # We will assume a fixed visual composition inspired by the image,
    # but the text fields (Name, Points) will be dynamic.
    
    # Place 1 (Center)
    p1_name = top_3_overall.iloc[0]["Player"]
    p1_pts = str(top_3_overall.iloc[0]["Points"])
    
    # Place 2 (Right)
    p2_name = top_3_overall.iloc[1]["Player"]
    p2_pts = str(top_3_overall.iloc[1]["Points"])
    
    # Place 3 (Left)
    p3_name = top_3_overall.iloc[2]["Player"]
    p3_pts = str(top_3_overall.iloc[2]["Points"])
    
    # Textual placeholder while the dynamic image gen capability is not implemented.
    st.info(f"Dynamic Podium placeholders: \n\n"
             f"**1st (Center):** {p1_name} ({p1_pts} pts) - Blue Kit\n\n"
             f"**2nd (Right):** {p2_name} ({p2_pts} pts) - Red Kit\n\n"
             f"**3rd (Left):** {p3_name} ({p3_pts} pts) - Green Kit\n\n"
             f"*Note: A full graphic generation with these names would replace this.*")
else:
    st.warning("Insufficient player data for dynamic podium.")
    st.image("image_0.png", caption="Static Podium (Incomplete Data)", use_container_width=True)


# -----------------------------
# STYLING FUNCTION
# -----------------------------
# Helper function to inject progressively larger font sizes for podium rows 1 and 2
def apply_progressive_fonts(row):
    if row.name == 1:
        return ['font-size: 18px; font-weight: bold;'] * len(row)
    elif row.name == 2:
        return ['font-size: 15px; font-weight: bold;'] * len(row)
    return [''] * len(row)


# -----------------------------
# SIDE-BY-SIDE DISPLAY
# -----------------------------
col1, col2 = st.columns([1, 1])

# LEFT SIDE: STACKED TABLES (BEST PLAYER PER TEAM)
with col1:
    st.subheader("🥇 Best Player per Team")
    styled_leaders = leaders_table.style.apply(apply_progressive_fonts, axis=1)
    st.dataframe(styled_leaders, use_container_width=True, height=180)

# RIGHT SIDE: COMPACT CHART
with col2:
    st.subheader("📊 Team Scores")

    top_team = df.sort_values(by="Points", ascending=False).iloc[0]["Team"]

    fig, ax = plt.subplots(figsize=(5, 3.2))  # Bumped up height slightly to match stacked layout

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
    st.pyplot(fig, use_container_width=True)


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
