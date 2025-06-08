"""
streamlit_app.py  –  UIUC room-schedule viewer
================================================
* All-Python, no custom JS
* Sidebar selectors for Building & Room
* Gridded weekly timetable (30-minute rows, Mon–Sun columns)

Author: (your name)
"""

from __future__ import annotations
from datetime import datetime, timedelta
import re

import pandas as pd
import streamlit as st

#####################################################################
# CONFIG
#####################################################################
CSV_PATH = "SP25_UIUC_courses.csv"
TIME_STEP = 30  # minutes per row
DAY_ORDER = ["M", "T", "W", "R", "F", "S", "U"]
SLOT_START = 7  # 07:00
SLOT_END = 22  # 22:00  (exclusive)


#####################################################################
# HELPERS
#####################################################################


@st.cache_data(show_spinner=False)
def load_courses(path: str) -> pd.DataFrame:
    """Read the CSV once; cache in Streamlit’s in-memory store."""
    return pd.read_csv(path)


def parse_timemark(s: str) -> datetime.time:
    """'09:00AM' -> datetime.time(9, 0)."""
    return datetime.strptime(s.strip(), "%I:%M%p").time()


def time_range(start, end, step_minutes=TIME_STEP):
    """  
    Yield 'HH:MM' strings from *start* up to (not incl.) *end* every *step* min.    """
    cur = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    while cur < end_dt:
        yield cur.strftime("%H:%M")
        cur += timedelta(minutes=step_minutes)


def build_grid(room_df: pd.DataFrame) -> pd.DataFrame:
    """  
    Convert `room_df` (only rows for ONE room) into a timetable DataFrame:        rows = time slots 07:00 … 21:30        cols = DAY_ORDER        cell  = newline-joined label(s) or '' if free    """
    slots = [
        f"{h:02d}:{m:02d}"
        for h in range(SLOT_START, SLOT_END)
        for m in (0, 30)
    ]
    grid = pd.DataFrame("", index=slots, columns=DAY_ORDER)

    for _, row in room_df.iterrows():
        label = f"{row['Class']} {row['Section']} · {row['Instructor']}"

        # "09:00AM - 09:50AM"
        start_text, end_text = map(str.strip, row["Time"].split("-"))
        start, end = parse_timemark(start_text), parse_timemark(end_text)

        for day in list(row["Day"].strip()):
            for slot in time_range(start, end):
                grid.at[slot, day] += (label + "\n")

                # strip trailing newline if any, replace empty with whitespace (nicer look)
    grid = grid.applymap(lambda x: x.rstrip("\n") if x else " ")
    return grid


#####################################################################
# STREAMLIT PAGE
#####################################################################
st.set_page_config(
    page_title="UIUC Room Schedule",
    layout="wide",
    page_icon="random"
)

st.title("UIUC Room Schedule Viewer")

df = load_courses(CSV_PATH)

# ------------------------------------------------------------------
# sidebar inputs
# ------------------------------------------------------------------
st.sidebar.header("Search")
# Extract building names by dropping the first token (room number)
df["BuildingOnly"] = df["Location"].str.split().str[1:].apply(" ".join)
buildings = sorted(df["BuildingOnly"].unique())

sel_building = st.sidebar.selectbox("Building", buildings, index=buildings.index(
    "Loomis Laboratory") if "Loomis Laboratory" in buildings else 0)

rooms = (
    df.loc[df["BuildingOnly"].str.lower() == sel_building.lower(), "Location"]
    .str.split()
    .str[0]
    .unique()
)
sel_room = st.sidebar.selectbox("Room number", sorted(rooms), index=0)

submitted = st.sidebar.button("Show schedule", use_container_width=True)

# ------------------------------------------------------------------
# results
# ------------------------------------------------------------------
if submitted:
    pattern = rf"^{sel_room}\s+{re.escape(sel_building)}$"
    room_df = df[df["Location"].str.contains(pattern, flags=re.I, regex=True)]

    if room_df.empty:
        st.warning(f"No classes found for room {sel_room} in {sel_building}.")
        st.stop()

    timetable = build_grid(room_df)

    st.subheader(f"Room {sel_room} – {sel_building}")
    # Display with Streamlit’s interactive data editor
    st.dataframe(
        timetable,
        use_container_width=True,
        height=min(800, 22 * len(timetable) + 35),
    )

    st.caption(
        "Tip: double-click a cell to copy text; sort/filter, "
        "or download to CSV via menu ▸.")

else:
    st.info("Select a building and room number, then press **Show schedule**.")