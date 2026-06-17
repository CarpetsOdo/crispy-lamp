import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
GROUPS = {
    "Alfacinhas FC": "https://www.kicktipp.pt/alfacinhas-fc/ranking",
    "Os Magmáticos": "https://www.kicktipp.pt/os-magmaticos/ranking",
    "Treinadores de Bancada": "https://www.kicktipp.pt/treinadores-de-bancada/ranking"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}


# -----------------------------
# SCRAPER
# -----------------------------
def get_group_total(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            return 0

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

# Manual refresh
if st.button("🔄 Refresh"):
    st.rerun()

# -----------------------------
# DATA
# -----------------------------
results = {}

for team, url in GROUPS.items():
    results[team] = get_group_total(url)

df = pd.DataFrame(list(results.items()), columns=["Team", "Points"])
df = df.sort_values(by="Points", ascending=False)

# -----------------------------
# DISPLAY
# -----------------------------
if len(df) > 0:
    leader = df.iloc[0]
    st.success(f"🏆 Leading: {leader['Team']} — {leader['Points']} pts")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Team Scores")
        st.bar_chart(df.set_index("Team"))

    with col2:
        st.subheader("📋 Ranking")
        st.dataframe(df, use_container_width=True)

else:
    st.error("No data available")

st.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")

# -----------------------------
# AUTO REFRESH (60s)
# -----------------------------
st.markdown(
    '<meta http-equiv="refresh" content="60">',
    unsafe_allow_html=True
)
