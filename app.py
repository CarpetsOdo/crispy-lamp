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

# 🎨 Define team colours here
TEAM_COLORS = {
    "Alfacinhas FC": "#1f77b4",        # blue
    "Os Magmáticos": "#d62728",        # red
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
# PAGE
# -----------------------------
st.set_page_config(page_title="Kicktipp Team Battle", layout="wide")

st.title("🏆 Kicktipp Team Battle")

if st.button("🔄 Refresh"):
    st.rerun()


# -----------------------------
# DATA
# -----------------------------
results = {}

for team, url in GROUPS.items():
    results[team] = get_group_total(url)

df = pd.DataFrame(list(results.items()), columns=["Team", "Points"])
df = df.sort_values(by="Points", ascending=True)  # ascending for horizontal chart


# -----------------------------
# DISPLAY
# -----------------------------
if len(df) > 0:

    leader = df.iloc[-1]

    st.success(f"🏆 Leading: {leader['Team']} — {leader['Points']} pts")

    col1, col2 = st.columns([2, 1])

    # 📊 HORIZONTAL BAR CHART
    with col1:
        st.subheader("📊 Team Scores")

        fig, ax = plt.subplots()

        colors = [TEAM_COLORS.get(team, "#888888") for team in df["Team"]]

        ax.barh(df["Team"], df["Points"], color=colors)

        # Clean look
        ax.set_xlabel("Points")
        ax.set_ylabel("")
        ax.spines[['top', 'right', 'left']].set_visible(False)

        # Add values at the end of bars
        for i, v in enumerate(df["Points"]):
            ax.text(v + 1, i, str(v), va='center')

        st.pyplot(fig)

    # 📋 TABLE
    with col2:
        st.subheader("📋 Ranking")
        df_display = df.sort_values(by="Points", ascending=False).reset_index(drop=True)
        df_display.index += 1
        st.dataframe(df_display, use_container_width=True)

else:
    st.error("No data available")

st.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")


# -----------------------------
# AUTO REFRESH
# -----------------------------
st.markdown(
    '<meta http-equiv="refresh" content="60">',
    unsafe_allow_html=True
)
