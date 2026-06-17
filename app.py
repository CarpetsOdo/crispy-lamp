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
def get_group_data(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select("table tr")

        total = 0
        leader_name = "N/A"
        leader_points = 0
        first_row_found = False

        for row in rows:
            cols = row.find_all("td")

            if len(cols) >= 3:
                try:
                    name = cols[1].text.strip()
                    pts = int(cols[2].text.strip().replace(".", "").replace(",", ""))

                    total += pts

                    if not first_row_found:
                        leader_name = name
                        leader_points = pts
                        first_row_found = True

                except:
                    pass

        return total, leader_name, leader_points

    except:
        return 0, "Error", 0


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
team_results = []
leader_results = []

for team, url in GROUPS.items():
    total, leader_name, leader_points = get_group_data(url)

    team_results.append({
        "Team": team,
        "Points": total
    })

    leader_results.append({
        "Team": team,
        "Leader": leader_name,
        "Points": leader_points
    })

df = pd.DataFrame(team_results)
leaders_df = pd.DataFrame(leader_results)

# Safety check
if len(df) == 0:
    st.error("No data available")
    st.stop()

# Sort for chart
df_chart = df.sort_values(by="Points", ascending=True)
df_table = df.sort_values(by="Points", ascending=False).reset_index(drop=True)
df_table.index += 1

leaders_table = leaders_df.sort_values(by="Points", ascending=False).reset_index(drop=True)
leaders_table.index += 1


# -----------------------------
# DISPLAY
# -----------------------------
team_leader = df_table.iloc[0]

st.success(f"🏆 Leading Team: {team_leader['Team']} — {team_leader['Points']} pts")

col1, col2 = st.columns([2, 1])

# -----------------------------
# LEFT: CHART
# -----------------------------
with col1:
    st.subheader("📊 Team Scores")

    fig, ax = plt.subplots(figsize=(6, 3.5))

    colors = []
    for team in df_chart["Team"]:
        if team == team_leader["Team"]:
            colors.append("#FFD700")
        else:
            colors.append(TEAM_COLORS.get(team, "#cccccc"))

    bars = ax.barh(df_chart["Team"], df_chart["Points"], color=colors, height=0.5)

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
    ax.tick_params(left=False, bottom=False)

    max_val = df_chart["Points"].max()

    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + max_val * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)}",
            va='center',
            fontsize=10
        )

    plt.tight_layout()
    st.pyplot(fig)


# -----------------------------
# RIGHT: STACKED TABLES
# -----------------------------
with col2:

    st.subheader("📋 Team Ranking")
    st.dataframe(df_table, use_container_width=True, height=200)

    st.markdown("---")

    st.subheader("🥇 Best Player")
    st.dataframe(leaders_table, use_container_width=True, height=200)


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
``
