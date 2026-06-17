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

# 🎨 Team colours
TEAM_COLORS = {
    "Alfacinhas FC": "#1f77b4",       # blue
    "Os Magmáticos": "#d62728",       # red
    "Treinadores de Bancada": "#2ca02c"  # green
}

HEADERS = {"User-Agent": "Mozilla/5.0"}


# -----------------------------
# SCRAPER
# -----------------------------
def get_group_total(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        total = 0
        rows = soup.select("table tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                try:
                    pts = int(cols[2].text.strip().replace(".", "").replace(",", ""))
                    total += pts
                except:
                    pass

        return total

    except:
        return 0


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
results = {}

for team, url in GROUPS.items():
    results[team] = get_group_total(url)

df = pd.DataFrame(list(results.items()), columns=["Team", "Points"])

# Sort for horizontal chart (small -> large)
df = df.sort_values(by="Points", ascending=True)


# -----------------------------
# DISPLAY
# -----------------------------
if len(df) > 0:

    leader = df.iloc[-1]

    st.success(f"🏆 Leading: {leader['Team']} — {leader['Points']} pts")

    col1, col2 = st.columns([2, 1])

    # -----------------------------
    # 📊 CLEAN HORIZONTAL CHART
    # -----------------------------
    with col1:
        st.subheader("📊 Team Scores")

        fig, ax = plt.subplots(figsize=(6, 3.5))

        # Highlight leader in gold, others in team colours
        colors = []
        for team in df["Team"]:
            if team == leader["Team"]:
                colors.append("#FFD700")  # gold
            else:
                colors.append(TEAM_COLORS.get(team, "#cccccc"))

        bars = ax.barh(df["Team"], df["Points"], color=colors, height=0.5)

        # Clean styling
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
        ax.tick_params(left=False, bottom=False)

        # Add value labels
        max_val = max(df["Points"]) if len(df) > 0 else 1

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
    # 📋 TABLE
    # -----------------------------
    with col2:
        st.subheader("📋 Ranking")

        df_display = df.sort_values(by="Points", ascending=False).reset_index(drop=True)
        df_display.index += 1

        st.dataframe(df_display, use_container_width=True)

else:
    st.error("No data available")


# -----------------------------
# FOOTER
# -----------------------------
st.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")

# -----------------------------
# AUTO REFRESH (60s)
# -----------------------------
st.markdown(
    '<meta http-equiv="refresh" content="60">',
    unsafe_allow_html=True
)
