import json
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
import streamlit as st

# --- Email sending utility (simulated, ready for real SMTP) ---
def send_email(to_email, subject, body):
    """
    Simulated email sender. To enable real email, configure SMTP below.
    """
    # --- Simulated: print to Streamlit ---
    st.info(f"Simulated email sent to {to_email}: {subject}\n{body}")
    # --- Real email (uncomment and configure to enable) ---
    # smtp_server = 'smtp.example.com'
    # smtp_port = 587
    # smtp_user = 'your_email@example.com'
    # smtp_password = 'your_password'
    # msg = MIMEText(body)
    # msg['Subject'] = subject
    # msg['From'] = smtp_user
    # msg['To'] = to_email
    # with smtplib.SMTP(smtp_server, smtp_port) as server:
    #     server.starttls()
    #     server.login(smtp_user, smtp_password)
    #     server.sendmail(smtp_user, [to_email], msg.as_string())

# --- Simple user database (for demo only) ---
ACTIVITY_LOG_DIR = "data"

def get_activity_log_path(username):
    return os.path.join(ACTIVITY_LOG_DIR, f"{username}_activity.json")

def log_user_activity(username, action, details=None):
    path = get_activity_log_path(username)
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "details": details or ""
    }
    logs = []
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.insert(0, entry)  # newest first
    with open(path, "w") as f:
        json.dump(logs, f, indent=2)

def get_user_activity(username, limit=10):
    path = get_activity_log_path(username)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                logs = json.load(f)
            return logs[:limit]
        except Exception:
            return []
    return []
"""
Main Streamlit App: AI-Powered Personal Financial Advisor Prototype

- Integrates all modules for a holistic, explainable, goal-oriented advisor.
- UI for profile/goals, plan generation, explanations, and progress visualization.
- Demonstrates research contributions: transparency and personalization.
"""


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from modules import data_manager, planning_engine, explanation_engine

st.set_page_config(page_title="AI Financial Advisor Prototype", layout="wide")

# --- Simple user database (for demo only) ---
USERS = {
    "alice": "password123",
    "bob": "securepass",
    "demo": "demo"
}

def get_user_data_path(username):
    return os.path.join("data", f"{username}_user.json")

def load_user_data_for_user(username):
    path = get_user_data_path(username)
    if not os.path.exists(path):
        # Copy default data for new user
        import shutil
        shutil.copyfile(os.path.join("data", "synthetic_user.json"), path)
    # Patch: ensure file is valid, else reset
    try:
        with open(path, "r") as f:
            import json
            json.load(f)
    except Exception:
        os.remove(path)
        import shutil
        shutil.copyfile(os.path.join("data", "synthetic_user.json"), path)
    # Use data_manager but override DATA_PATH
    orig_path = data_manager.DATA_PATH
    data_manager.DATA_PATH = path
    data = data_manager.load_user_data()
    data_manager.DATA_PATH = orig_path
    return data

def save_user_data_for_user(username, data):
    path = get_user_data_path(username)
    orig_path = data_manager.DATA_PATH
    data_manager.DATA_PATH = path
    data_manager.save_user_data(data)
    data_manager.DATA_PATH = orig_path

# --- Login/Logout logic ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def login_form():
    st.markdown("""
    <div style='text-align:center;'>
        <span style='font-size:3em;'>🤖💸</span>
        <h1 style='margin-bottom:0.2em;'>FinAI Advisor</h1>
        <p style='font-size:1.1em;'>Your Explainable, Goal-Oriented Financial Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'>Demo users: <b>alice/password123</b>, <b>bob/securepass</b>, <b>demo/demo</b></div>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("👤 Username", max_chars=20, key="login_user")
        password = st.text_input("🔒 Password", type="password", max_chars=20, key="login_pass")
        submit = st.form_submit_button("Login")
        if submit:
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

if not st.session_state.logged_in:
    login_form()
    st.stop()

# --- Main App (after login) ---
username = st.session_state.username
user_data = load_user_data_for_user(username)
income = user_data["income"]
expenses = user_data["expenses"]
risk_profile = user_data["risk_profile"]
goals = user_data["goals"]



# --- Calculate monthly savings before dashboard ---
monthly_savings = data_manager.compute_monthly_savings(income, expenses)

# --- App Header with Icon ---
st.markdown("""
<div style='display:flex;align-items:center;gap:1em;'>
    <span style='font-size:2.5em;'>🤖💸</span>
    <h1 style='margin-bottom:0;'>FinAI Advisor</h1>
</div>
<hr style='margin-top:0;margin-bottom:1em;'>
""", unsafe_allow_html=True)


# --- Dashboard: User Activity, Calendar, and Reminders ---
st.markdown(f"<div style='font-size:1.2em;'><b>Welcome, {username}!</b></div>", unsafe_allow_html=True)
st.markdown(f"<span style='font-size:1.1em;'>💰 <b>Monthly Savings:</b> ₹{monthly_savings:.2f}</span>", unsafe_allow_html=True)
st.markdown(f"<span style='font-size:1.1em;'>🎯 <b>Active Goals:</b> {len(goals)}</span>", unsafe_allow_html=True)
st.markdown(f"<span style='font-size:1.1em;'>🛡️ <b>Risk Profile:</b> {risk_profile}</span>", unsafe_allow_html=True)

# --- Home Loan Reminder & Email Button ---
home_loan_goals = [g for g in goals if "home loan" in g["name"].lower()]
if home_loan_goals:
    st.warning(f"🏠 <b>Home Loan Reminder:</b> You have a Home Loan goal. Don't forget to review your repayment plan and deadlines!", icon=None)
    if st.button("📧 Send Reminder Email"):
        send_email(user_data.get("email", f"{username}@example.com"),
                   "Home Loan Goal Reminder",
                   "This is a reminder to review your Home Loan goal and repayment plan in FinAI Advisor.")

# --- Calendar View of Goal Deadlines ---
import pandas as pd
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("📅 Goal Progress Chart")
calendar_df = pd.DataFrame([
    {"Goal": g["name"], "Deadline": g["deadline"], "Target (₹)": g["target_amount"], "Priority": g["priority"], "Current (₹)": g["current_amount"]}
    for g in goals
])
if not calendar_df.empty:
    calendar_df = calendar_df.sort_values("Deadline")
    st.dataframe(calendar_df, use_container_width=True)
    # --- Improved progress bar chart with log scale and grid ---
    import matplotlib.pyplot as plt
    import numpy as np
    fig, ax = plt.subplots(figsize=(8, 0.6 * len(calendar_df) + 1))
    ylabels = list(calendar_df["Goal"])
    current = calendar_df["Current (₹)"]
    target = calendar_df["Target (₹)"]
    bar_width = 0.35
    y = np.arange(len(ylabels))
    # Use log scale for x-axis if range is large
    max_target = max(target)
    min_target = min(target)
    use_log = max_target > 10 * max(min_target, 1)
    # Plot bars
    ax.barh(y - bar_width/2, target, height=bar_width, color="#e0e0e0", label="Target")
    ax.barh(y + bar_width/2, current, height=bar_width, color="#4f8cff", label="Current")
    # Add value labels
    for i, (c, t) in enumerate(zip(current, target)):
        ax.text(c, i + bar_width/2, f"₹{c:.0f}", va='center', ha='left', fontsize=9, color="#4f8cff", weight='bold')
        ax.text(t, i - bar_width/2, f"₹{t:.0f}", va='center', ha='right', fontsize=9, color="#888888")
    ax.set_yticks(y)
    ax.set_yticklabels(ylabels)
    ax.set_xlabel("Amount (₹)")
    ax.legend(loc='upper right')
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    if use_log:
        ax.set_xscale('log')
        ax.set_xlim(left=max(1, min(current.min(), target.min())), right=max(current.max(), target.max())*1.2)
    else:
        ax.set_xlim(left=0, right=max(current.max(), target.max())*1.2)
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("No goals to display in chart.")

# --- Filter Activity Log by Goal ---
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("🕒 Recent Activity (Filter by Goal)")
goal_names = [g["name"] for g in goals]
selected_goal = st.selectbox("Select a goal to filter activity log:", ["All Goals"] + goal_names, key="activity_goal_filter")
activity = get_user_activity(username, limit=30)
if selected_goal != "All Goals":
    activity = [a for a in activity if selected_goal.lower() in a["details"].lower()]
if activity:
    for entry in activity[:7]:
        st.markdown(f"- <b>{entry['timestamp']}</b>: {entry['action']} {entry['details']}", unsafe_allow_html=True)
else:
    st.info("No recent activity for this goal yet.")

st.sidebar.header(f"Profile & Goals ({username})")
if st.sidebar.button("Logout"):
    logout()

# --- Dashboard Summary ---
monthly_savings = data_manager.compute_monthly_savings(income, expenses)
st.markdown(f"<div style='font-size:1.2em;'><b>Welcome, {username}!</b></div>", unsafe_allow_html=True)
st.markdown(f"<span style='font-size:1.1em;'>💰 <b>Monthly Savings:</b> ₹{monthly_savings:.2f}</span>", unsafe_allow_html=True)
st.markdown(f"<span style='font-size:1.1em;'>🎯 <b>Active Goals:</b> {len(goals)}</span>", unsafe_allow_html=True)
st.markdown(f"<span style='font-size:1.1em;'>🛡️ <b>Risk Profile:</b> {risk_profile}</span>", unsafe_allow_html=True)

# --- User Options ---
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("What would you like to do?")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📊 View Progress"):
        st.session_state.show_progress = True
with col2:
    if st.button("🎯 Allocate to Goals"):
        st.session_state.show_allocate = True
with col3:
    if st.button("📝 Adjust Profile"):
        st.session_state.show_profile = True
with col4:
    if st.button("➕ Add New Goal"):
        st.session_state.show_add_goal = True

# --- Profile Form (in sidebar, always available) ---
with st.sidebar.form("profile_form"):
    st.subheader("Update Profile")
    income = st.number_input("Monthly Income (₹)", min_value=0.0, value=float(income), step=100.0)
    expenses = st.number_input("Monthly Expenses (₹)", min_value=0.0, value=float(expenses), step=100.0)
    risk_profile = st.selectbox("Risk Profile", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(risk_profile))
    email = st.text_input("Email", value=user_data.get("email", f"{username}@example.com"), key="profile_email")
    st.markdown("*Risk profile influences long-term advice (not implemented in this prototype).*")
    submitted_profile = st.form_submit_button("Save Profile")
    if submitted_profile:
        user_data["income"] = income
        user_data["expenses"] = expenses
        user_data["risk_profile"] = risk_profile
        user_data["email"] = email
        save_user_data_for_user(username, user_data)
        log_user_activity(username, "Updated profile", f"Income: ₹{income}, Expenses: ₹{expenses}, Risk: {risk_profile}, Email: {email}")
        st.success("Profile updated. Please refresh to see changes.")

# --- Add New Goal (in sidebar, only if selected) ---
if st.session_state.get("show_add_goal", False):
    with st.sidebar.form("add_goal_form"):
        st.subheader("Add New Goal")
        new_name = st.text_input("Goal Name", key="add_goal_name")
        target = st.number_input("Target Amount (₹)", min_value=0.0, step=100.0, key="add_goal_target")
        current = st.number_input("Current Amount (₹)", min_value=0.0, step=100.0, key="add_goal_current")
        deadline = st.date_input("Deadline", key="add_goal_deadline")
        priority = st.slider("Priority (1=Low, 5=High)", 1, 5, 3, key="add_goal_priority")
        add_goal_btn = st.form_submit_button("Add Goal")
        if add_goal_btn and new_name:
            new_goal = {
                "name": new_name,
                "target_amount": target,
                "current_amount": current,
                "deadline": str(deadline),
                "priority": priority
            }
            goals.append(new_goal)
            user_data["goals"] = goals
            save_user_data_for_user(username, user_data)
            log_user_activity(username, "Added new goal", f"{new_name} (Target: ₹{target}, Deadline: {deadline})")
            if "home loan" in new_name.lower():
                log_user_activity(username, "Home Loan goal added", f"{new_name}")
            st.success("Goal added!")
            st.session_state.show_add_goal = False
            st.rerun()

# --- Manage Goals (in sidebar) ---
st.sidebar.subheader("Manage Goals")
goals_df = data_manager.get_goals_dataframe(goals)
for idx, row in goals_df.iterrows():
    with st.sidebar.expander(f"Edit Goal: {row['name']}"):
        new_name = st.text_input(f"Goal Name", value=row["name"], key=f"name_{idx}")
        target = st.number_input(f"Target Amount (₹)", min_value=0.0, value=float(row["target_amount"]), step=100.0, key=f"target_{idx}")
        current = st.number_input(f"Current Amount (₹)", min_value=0.0, value=float(row["current_amount"]), step=100.0, key=f"current_{idx}")
        deadline = st.date_input(f"Deadline", value=row["deadline"].date(), key=f"deadline_{idx}")
        priority = st.slider(f"Priority (1=Low, 5=High)", 1, 5, int(row["priority"]), key=f"priority_{idx}")
        if st.button("Save Goal", key=f"save_{idx}"):
            old_goal = goals_df.loc[idx].to_dict()
            goals_df.at[idx, "name"] = new_name
            goals_df.at[idx, "target_amount"] = target
            goals_df.at[idx, "current_amount"] = current
            goals_df.at[idx, "deadline"] = pd.to_datetime(deadline)
            goals_df.at[idx, "priority"] = priority
            # Save all goals at once
            user_data = data_manager.update_goals_in_data(user_data, goals_df)
            save_user_data_for_user(username, user_data)
            log_user_activity(username, "Updated goal", f"{new_name} (Target: ₹{target}, Current: ₹{current}, Deadline: {deadline})")
            if "home loan" in new_name.lower():
                log_user_activity(username, "Home Loan goal updated", f"{new_name}")
            st.success("Goal updated. Please refresh to see changes.")

# --- Goal Completion & Milestone Tracking ---
if "completed_goals" not in user_data:
    user_data["completed_goals"] = []
    save_user_data_for_user(username, user_data)

st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("✅ Mark Goals as Completed")
active_goal_names = [g["name"] for g in goals if g["name"] not in user_data["completed_goals"]]
completed_goal_names = user_data["completed_goals"]
if active_goal_names:
    selected_complete = st.selectbox("Select a goal to mark as completed:", ["-- Select --"] + active_goal_names, key="complete_goal_select")
    if selected_complete != "-- Select --" and st.button("Mark as Completed"):
        user_data["completed_goals"].append(selected_complete)
        save_user_data_for_user(username, user_data)
        log_user_activity(username, "Completed goal", selected_complete)
        st.success(f"Goal '{selected_complete}' marked as completed!")
        st.rerun()
else:
    st.info("No active goals to complete.")

if completed_goal_names:
    st.markdown("### 🏆 Completed Milestones")
    for g in completed_goal_names:
        st.markdown(f"- <b>{g}</b>", unsafe_allow_html=True)
else:
    st.info("No completed milestones yet.")

# --- Main Content: Allocation & Progress ---
if st.session_state.get("show_allocate", False):
    st.subheader("🎯 Allocate to Goals")
    if st.button("Generate Plan"):
        # Recompute DataFrame in case of updates
        goals_df = data_manager.get_goals_dataframe(user_data["goals"])
        allocations, reason_tags = planning_engine.plan_allocations(goals_df, monthly_savings)
        explanations = explanation_engine.explain_allocations(reason_tags)

        # Update current_amounts for simulation and save
        for idx, row in goals_df.iterrows():
            alloc = allocations.get(row["name"], 0.0)
            goals_df = data_manager.update_goal(goals_df, idx, alloc)
        user_data = data_manager.update_goals_in_data(user_data, goals_df)
        save_user_data_for_user(username, user_data)

        # Show Allocations Table
        alloc_df = pd.DataFrame([
            {
                "Goal": g,
                "Allocated (₹)": allocations[g],
                "Required This Month (₹)": float(goals_df[goals_df["name"] == g]["required_monthly"].values[0]),
                "Months Left": int(goals_df[goals_df["name"] == g]["months_left"].values[0]),
                "Priority": int(goals_df[goals_df["name"] == g]["priority"].values[0])
            }
            for g in allocations
        ])
        st.subheader("Monthly Allocation Plan")
        st.dataframe(alloc_df, use_container_width=True)

        # Show Explanations
        st.subheader("Explanations (XAI)")
        for g, exp in explanations.items():
            st.markdown(f"- **{g}**: {exp.replace('$', '₹')}")

        st.session_state.show_allocate = False

    else:
        st.markdown("Click **Generate Plan** to see allocations and explanations.")

if st.session_state.get("show_progress", False):
    st.subheader("📊 Goal Progress")
    fig, ax = plt.subplots(figsize=(8, 3))
    names = goals_df["name"]
    current = goals_df["current_amount"]
    target = goals_df["target_amount"]
    ax.barh(names, target, color="#e0e0e0", label="Target")
    ax.barh(names, current, color="#4f8cff", label="Current")
    ax.set_xlabel("Amount (₹)")
    ax.legend()
    st.pyplot(fig)
    st.session_state.show_progress = False

st.markdown("---")
st.caption("Academic prototype for AI/ML course. No real financial advice. See README for details.")

# --- Personalized Suggestions ---
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("💡 Personalized Suggestions")
suggestions = []
# Suggest Emergency Fund if not present
if not any("emergency" in g["name"].lower() for g in goals):
    suggestions.append("Consider adding an Emergency Fund goal to cover 3-6 months of expenses.")
# Suggest Retirement if not present
if not any("retirement" in g["name"].lower() for g in goals):
    suggestions.append("Plan for the long term: add a Retirement goal if you haven't already.")
# Suggest increasing savings if monthly savings is low
if data_manager.compute_monthly_savings(income, expenses) < 1000:
    suggestions.append("Your monthly savings are low. Review your expenses or increase your income to achieve your goals faster.")
# Suggest reviewing overdue goals
from datetime import datetime
for g in goals:
    try:
        deadline = pd.to_datetime(g["deadline"])
        if deadline < datetime(2025, 9, 24) and g["name"] not in user_data.get("completed_goals", []):
            suggestions.append(f"Goal '{g['name']}' is past its deadline. Consider updating or completing it.")
    except Exception:
        pass
if suggestions:
    for s in suggestions:
        st.info(s)
else:
    st.info("No suggestions at this time. Keep up the good work!")

# --- Export/Download Reports ---
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("⬇️ Export/Download Reports")
import io
# Export goals
if st.button("Download Goals as CSV"):
    goals_df_export = pd.DataFrame(goals)
    csv = goals_df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Goals CSV",
        data=csv,
        file_name=f'{username}_goals.csv',
        mime='text/csv',
    )
# Export activity log
activity_log = get_user_activity(username, limit=1000)
if st.button("Download Activity Log as CSV"):
    if activity_log:
        activity_df = pd.DataFrame(activity_log)
        csv = activity_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Activity Log CSV",
            data=csv,
            file_name=f'{username}_activity_log.csv',
            mime='text/csv',
        )
    else:
        st.info("No activity log to export.")