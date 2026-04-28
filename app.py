import streamlit as st
import pandas as pd
import datetime
import os
import calendar

# ================= CONFIG =================
st.set_page_config(page_title="Smart Planner", layout="wide")

DAILY_FILE = "daily_tasks.csv"
MONTHLY_FILE = "monthly_tasks.csv"

# ================= UI STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
h1, h2, h3 {
    color: #22c55e;
}
.card {
    padding: 20px;
    border-radius: 12px;
    background: #1e293b;
    margin-bottom: 15px;
}
.metric {
    font-size: 22px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================= INIT =================
def init_file(file):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=["task", "date", "completed"])
        df.to_csv(file, index=False)

init_file(DAILY_FILE)
init_file(MONTHLY_FILE)

# ================= DATA =================
def load_data(file):
    try:
        df = pd.read_csv(file)
        return df[["task", "date", "completed"]]
    except:
        return pd.DataFrame(columns=["task", "date", "completed"])

def save_data(df, file):
    df.to_csv(file, index=False)

# ================= SIDEBAR =================
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["Daily Tasks", "Monthly Planner"])

# ================= DAILY =================
if page == "Daily Tasks":
    today = datetime.date.today()
    day_name = today.strftime("%A")

    st.title(f"🌞 {day_name} - {today}")

    df = load_data(DAILY_FILE)
    df = df[df["date"] == str(today)]

    # ADD TASK
    new_task = st.text_input("➕ Add Task")
    if st.button("Add Task") and new_task:
        new_row = pd.DataFrame({
            "task": [new_task],
            "date": [str(today)],
            "completed": [False]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df, DAILY_FILE)
        st.rerun()

    # TASK LIST
    st.subheader("Your Tasks")
    to_delete = []

    for i in df.index:
        col1, col2, col3 = st.columns([0.5, 0.3, 0.2])

        with col1:
            st.write(df.at[i, "task"])

        with col2:
            df.at[i, "completed"] = st.checkbox(
                "Completed",
                value=bool(df.at[i, "completed"]),
                key=f"d_{i}"
            )

        with col3:
            if st.button("❌", key=f"del_d_{i}"):
                to_delete.append(i)

    if to_delete:
        df = df.drop(to_delete)
        save_data(df, DAILY_FILE)
        st.rerun()

    save_data(df, DAILY_FILE)

    # PERFORMANCE
    total = len(df)
    done = df["completed"].sum()
    perf = int((done / total) * 100) if total > 0 else 0

    # KPI CARDS
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Tasks", total)
    col2.metric("Completed", int(done))
    col3.metric("Performance", f"{perf}%")

    st.progress(perf / 100)

    # CHART
    st.subheader("📊 Daily Trend")

    full_df = load_data(DAILY_FILE)
    if not full_df.empty:
        trend = full_df.groupby("date")["completed"].mean() * 100
        st.line_chart(trend)

# ================= MONTHLY =================
elif page == "Monthly Planner":
    st.title("📅 Monthly Habit Tracker")

    today = datetime.date.today()
    year, month = today.year, today.month
    current_month = today.strftime("%Y-%m")

    df = load_data(MONTHLY_FILE)

    # RESET MONTH
    if not df.empty:
        df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")
        if df["month"].iloc[0] != current_month:
            df = pd.DataFrame(columns=["task", "date", "completed"])

    # ADD HABIT
    new_task = st.text_input("➕ Add Habit")
    if st.button("Add Habit") and new_task:
        num_days = calendar.monthrange(year, month)[1]

        rows = []
        for day in range(1, num_days + 1):
            rows.append({
                "task": new_task,
                "date": str(datetime.date(year, month, day)),
                "completed": False
            })

        df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
        save_data(df, MONTHLY_FILE)
        st.rerun()

    # DELETE
    tasks = df["task"].unique()
    delete_task = st.selectbox("🗑️ Delete Habit", ["None"] + list(tasks))

    if delete_task != "None" and st.button("Delete Habit"):
        df = df[df["task"] != delete_task]
        save_data(df, MONTHLY_FILE)
        st.rerun()

    # GRID
    st.subheader("📊 Habit Grid")

    for task in tasks:
        st.write(f"### {task}")
        task_df = df[df["task"] == task]

        cols = st.columns(7)

        for i, row in task_df.iterrows():
            day = datetime.datetime.strptime(row["date"], "%Y-%m-%d").day
            col = cols[(day - 1) % 7]

            with col:
                df.loc[i, "completed"] = st.checkbox(
                    str(day),
                    value=bool(row["completed"]),
                    key=f"{task}_{day}"
                )

    save_data(df, MONTHLY_FILE)

    # ✅ MONTHLY PERFORMANCE (FIXED)
    total = len(df)
    done = df["completed"].sum()
    monthly_perf = int((done / total) * 100) if total > 0 else 0

    # KPI DASHBOARD
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Entries", total)
    col2.metric("Completed", int(done))
    col3.metric("Monthly Avg", f"{monthly_perf}%")

    st.progress(monthly_perf / 100)

    # TREND GRAPH
    st.subheader("📊 Monthly Trend")

    if not df.empty:
        trend = df.groupby("date")["completed"].mean() * 100
        st.line_chart(trend)