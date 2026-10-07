import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
import time
from datetime import datetime

from login import show_login
from signup import show_signup

# ============================================================
# CONFIGURATION
# ============================================================

# API_BASE = "http://127.0.0.1:8000"


API_BASE = os.getenv(
    "API_BASE",
    "http://127.0.0.1:8000"
)


# def wait_for_backend():
#     """
#     Wait until the backend wakes up.
#     Only executed once when the app starts.
#     """

#     placeholder = st.empty()

#     MAX_RETRIES = 12        # 12 × 5 = 60 sec
#     RETRY_DELAY = 5

#     for attempt in range(MAX_RETRIES):

#         try:
#             response = requests.get(
#                 f"{API_BASE}/",
#                 timeout=10
#             )

#             if response.status_code == 200:
#                 placeholder.empty()
#                 return True

#         except:
#             pass

#         placeholder.info(
#             f"""
# 🚀 **Starting Backend...**

# Render Free Tier puts the backend to sleep.

# Please wait...

# Attempt **{attempt+1}/{MAX_RETRIES}**
# """
#         )

#         time.sleep(RETRY_DELAY)

#     placeholder.error(
#         """
# ❌ Backend could not be started.

# Please refresh the page.
# """
#     )

#     return False

st.set_page_config(
    page_title="LeetRecall AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# AUTHENTICATION SESSION
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

 

if "backend_ready" not in st.session_state:
    st.session_state.backend_ready = False

if not st.session_state.backend_ready:
    st.title("🧠 LeetRecall AI")
    
    st.warning("""
🚀 Backend Wake-Up Required

This project is hosted on Render's Free Tier.
The backend automatically goes to sleep after a period of inactivity.

Please follow these steps:
1. Click 🚀 Open Backend
2. Wait about 40–60 seconds
3. When the backend page shows:
   {"message":"LeetRecall AI Backend Running"}
4. Return to this page.
5. Click ✅ Continue to Dashboard.
""")

    st.link_button("🚀 Open Backend", API_BASE, use_container_width=True)
    
    st.write("")
    
    if st.button("✅ Continue to Dashboard", use_container_width=True):
        st.session_state.backend_ready = True
        st.rerun()
        
    st.stop()


# ============================================================
# LOGIN / SIGNUP SCREEN
# ============================================================

if not st.session_state.logged_in:

    if st.session_state.show_signup:

        show_signup()

        st.write("")

        if st.button("⬅ Back to Login", use_container_width=True):
            st.session_state.show_signup = False
            st.rerun()

    else:

        show_login()

        st.write("")

        if st.button("Create New Account", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()

    st.stop()
# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
            

@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

[data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
    font-size: 24px !important;
    font-variation-settings:
        'FILL' 0,
        'wght' 400,
        'GRAD' 0,
        'opsz' 24;
}
            

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html,
    body,
    [data-testid="stAppViewContainer"] * {
        font-family: 'Inter', sans-serif;
    }
/* Hides the old Streamlit menu */
#MainMenu { display: none !important; }
/* Hides the new updated Streamlit menu container */
[data-testid="stTopBar"] button[kind="header"] {
    display: none !important;
}
/* Extra measure: hide the whole top bar left section if the button is inside it */
[data-testid="stTopBarLeft"] {
    display: none !important;
}



/* Completely remove the new Streamlit top chat input bar */
div[data-testid="stChatInput"] {
    display: none !important;
}
button[aria-label="Chat input"] {
    display: none !important;
}
section[data-testid="stChatInputContainer"] {
    display: none !important;
}                    
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(20px) !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #94a3b8 !important;
    }

    .dataframe {
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    .dataframe th {
        background: rgba(15, 23, 42, 0.9) !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        padding: 14px 16px !important;
        border-bottom: 2px solid rgba(99, 102, 241, 0.3) !important;
    }
    .dataframe td {
        padding: 12px 16px !important;
        font-size: 0.88rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.04) !important;
        color: #cbd5e1 !important;
    }
    .dataframe tr:hover td {
        background: rgba(99, 102, 241, 0.06) !important;
    }

    .section-header {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.01em;
    }

    .card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.5));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.3); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.5); }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
    }

    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(15, 23, 42, 0.4);
        border-radius: 12px;
        padding: 6px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        padding: 8px 20px !important;
        color: #94a3b8 !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #cbd5e1 !important;
    }

    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.2), transparent) !important;
        margin: 2rem 0 !important;
    }

    .js-plotly-plot .plotly .modebar {
        right: 10px !important;
        top: 10px !important;
    }

    /* --- Sidebar radio buttons (the only CSS addition) --- */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 1px !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #94a3b8 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 9px 14px !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(99, 102, 241, 0.08) !important;
    }
            
        /* --- FIX: Replace raw text sidebar toggle with a styled icon button --- */
    [data-testid="stSidebarCollapsedControl"] {
        /* Hide the default ugly text button */
        display: none !important;
    }
    
    /* Create a new styled toggle button */
  
    
    [data-testid="stSidebar"]::before:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }
            

/* Targets the exact container holding the sidebar toggle text */
button[data-testid="stSidebarToggle"] span {
    display: none !important;
}

/* Replaces the hidden text with a clean icon */


</style>
""", unsafe_allow_html=True)

# ============================================================
# BACKGROUND GRADIENT
# ============================================================

st.markdown("""
<div style="
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(160deg, #0a0e1a 0%, #0f172a 30%, #1a1040 60%, #0f172a 100%);
    z-index: -2;
"></div>
<div style="
    position: fixed;
    top: -200px; right: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
    z-index: -1;
    border-radius: 50%;
"></div>
<div style="
    position: fixed;
    bottom: -300px; left: -200px;
    width: 700px; height: 700px;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.06) 0%, transparent 70%);
    z-index: -1;
    border-radius: 50%;
"></div>
""", unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS (unchanged)
# ============================================================

# def safe_api_call(endpoint: str, params: dict = None) -> dict | list:

#     # if not backend_ready:
#     #     return []
#     try:
#         response = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=60)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.ConnectionError:
#         st.error("⚠️ Backend server is not running. Please start the FastAPI server first.")
#         return []
#     except requests.exceptions.Timeout:
#         st.error("⚠️ Request timed out. Server may be overloaded.")
#         return []
#     except requests.exceptions.HTTPError as e:
#         st.error(f"⚠️ Server error: {e.response.status_code}")
#         return []
#     except Exception:
#         st.error("⚠️ An unexpected error occurred while fetching data.")
#         return []


def safe_api_call(endpoint: str, params: dict = None):
    try:
        response = requests.get(
            f"{API_BASE}{endpoint}",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except Exception:
        return []

def render_metric_card(column, label: str, value, icon: str, color: str = "#6366f1"):
    if isinstance(value, (int, float)):
        display_value = f"{value:,}"
    else:
        display_value = str(value)

    with column:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.6));
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 24px 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        ">
            <div style="
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 3px;
                background: linear-gradient(90deg, {color}, {color}88);
                border-radius: 16px 16px 0 0;
            "></div>
            <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
            <div style="
                font-size: 2rem;
                font-weight: 800;
                color: #f1f5f9;
                letter-spacing: -0.03em;
                line-height: 1.1;
            ">{display_value}</div>
            <div style="
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: #64748b;
                margin-top: 6px;
            ">{label}</div>
        </div>
        """, unsafe_allow_html=True)


def create_chart(df, x_col, y_col, title, color_col=None, color_sequence=None, orientation="v"):
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=None,
        color=color_col,
        color_discrete_sequence=color_sequence or ["#6366f1"],
        orientation=orientation,
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8", size=12),
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.06)",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.06)",
            tickfont=dict(size=11),
        ),
        bargap=0.35,
        bargroupgap=0.15,
        hoverlabel=dict(
            bgcolor="#1e293b",
            bordercolor="#6366f1",
            font=dict(family="Inter", color="#e2e8f0", size=13),
        ),
    )

    fig.update_traces(
        marker=dict(
            cornerradius=6,
            line=dict(width=0),
        ),
        hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>" if "%" in title else "<b>%{x}</b><br>%{y}<extra></extra>",
    )

    return fig


def render_empty_state(icon: str, message: str):
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 48px 24px;
        background: rgba(15, 23, 42, 0.4);
        border: 1px dashed rgba(255,255,255,0.1);
        border-radius: 16px;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 12px; opacity: 0.6;">{icon}</div>
        <div style="color: #64748b; font-size: 0.95rem; font-weight: 500;">{message}</div>
    </div>
    """, unsafe_allow_html=True)


def section_divider():
    st.markdown('<hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(99,102,241,0.15), transparent); margin: 1.5rem 0;">', unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <div style="font-size: 2.5rem; margin-bottom: 4px;">🧠</div>
        <div style="
            font-size: 1.4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1, #a78bfa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
        ">
            LeetRecall AI
        </div>
        <div style="
            font-size:0.72rem;
            color:#475569;
            font-weight:500;
            text-transform:uppercase;
            letter-spacing:0.12em;
            margin-top:4px;
        ">
            DSA Revision System
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ============================================================
    # USER PROFILE
    # ============================================================

    st.markdown("### 👤 Logged In")
    st.success(f"Welcome, **{st.session_state.username}**")
    st.caption(st.session_state.email)

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.show_signup = False
        st.session_state.pop("token", None)
        st.session_state.pop("username", None)
        st.session_state.pop("email", None)
        st.rerun()

    st.markdown("---")

    # ============================================================
    # NAVIGATION (Fixed - no duplicate text)
    # ============================================================

    st.markdown("""
    <div style="padding:0 4px;">
        <div style="
            font-size:0.7rem;
            font-weight:600;
            text-transform:uppercase;
            letter-spacing:0.1em;
            color:#475569;
            margin-bottom:10px;
        ">
            Navigation
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_options = [
        "📋  View All",
        "📊  Dashboard",
        "📌  Revision Queue",
        "📉  Decay Analysis",
        "📚  Topic Mastery",
        "🎯  Pattern Coverage",
        "⚠️  Weak Areas",
        "🏆  Contest Analyzer",
        "🧠  AI Coach",
        "📅  Interview Planner",
    ]

    # FIX: Use empty string as label to avoid duplicate text
    selected = st.radio(
        label="",                          # Empty label instead of "nav"
        options=nav_options,
        label_visibility="collapsed",
        index=0,
    )

    page = selected.split("  ")[-1].strip()
    show_all = (page == "View All")

    st.markdown("---")

    # ============================================================
    # SYSTEM STATUS
    # ============================================================

    st.markdown("""
    <div style="
        background: linear-gradient(
            135deg,
            rgba(99,102,241,0.1),
            rgba(139,92,246,0.1)
        );
        border:1px solid rgba(99,102,241,0.15);
        border-radius:12px;
        padding:16px;
        text-align:center;
    ">
        <div style="
            font-size:0.7rem;
            font-weight:600;
            text-transform:uppercase;
            letter-spacing:0.1em;
            color:#818cf8;
            margin-bottom:6px;
        ">
            System Status
        </div>
        <div style="
            display:flex;
            align-items:center;
            justify-content:center;
            gap:6px;
        ">
            <div style="
                width:8px;
                height:8px;
                border-radius:50%;
                background:#22c55e;
                box-shadow:0 0 8px rgba(34,197,94,0.5);
            "></div>
            <span style="
                color:#86efac;
                font-size:0.82rem;
                font-weight:500;
            ">
                Online
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:20px 0 10px 0;text-align:center;">
        <div style="
            font-size:0.7rem;
            color:#334155;
            font-weight:400;
        ">
            Built with Spaced Repetition<br>
            & AI-Powered Insights
        </div>
    </div>
    """, unsafe_allow_html=True)
# ============================================================
# MAIN CONTENT  —  wrapped in if/elif, same rendering code
# ============================================================

# --- Header (shown on View All and Dashboard) ---
if show_all or page == "Dashboard":
    st.markdown("""
    <div style="margin-bottom: 8px;">
        <h1 style="
            font-size: 2rem;
            font-weight: 800;
            color: #f1f5f9;
            letter-spacing: -0.03em;
            margin: 0 0 4px 0;
            line-height: 1.1;
        ">Dashboard</h1>
        <p style="
            font-size: 0.92rem;
            color: #64748b;
            font-weight: 400;
            margin: 0;
        ">Your intelligent DSA revision & retention overview</p>
    </div>
    """, unsafe_allow_html=True)

    section_divider()

    # DASHBOARD STATS
    stats = safe_api_call("/dashboard/stats")

    if stats and isinstance(stats, dict):
        col1, col2, col3, col4 = st.columns(4)
        render_metric_card(col1, "Total Users", stats.get("total_users", 0), "👥", "#6366f1")
        render_metric_card(col2, "Questions", stats.get("total_questions", 0), "📝", "#8b5cf6")
        render_metric_card(col3, "Total Solves", stats.get("total_solves", 0), "✅", "#06b6d4")
        render_metric_card(col4, "Revisions", stats.get("total_revisions", 0), "🔄", "#f59e0b")
    else:
        render_empty_state("📊", "Unable to load dashboard statistics")

    section_divider()

# --- RECOMMENDATIONS ---
if show_all or page == "Revision Queue":
    if not show_all:
        st.markdown("""
        <div style="margin-bottom: 8px;">
            <h1 style="font-size: 2rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.03em; margin: 0 0 4px 0; line-height: 1.1;">📌 Revision Queue</h1>
            <p style="font-size: 0.92rem; color: #64748b; font-weight: 400; margin: 0;">Questions sorted by forgetting probability</p>
        </div>
        """, unsafe_allow_html=True)
        section_divider()
    else:
        st.markdown('<p class="section-header">📌 Questions To Revise</p>', unsafe_allow_html=True)

    recommendations = safe_api_call("/recommendations")

    if recommendations and len(recommendations) > 0:
        rec_df = pd.DataFrame(recommendations)
        column_renames = {
            "title": "Title", "difficulty": "Difficulty", "topic": "Topic",
            "pattern": "Pattern", "forget_probability": "Forget Prob.",
            "last_revised": "Last Revised", "url": "Link", "question_id": "ID",
        }
        display_df = rec_df.rename(columns={k: v for k, v in column_renames.items() if k in rec_df.columns})
        if "Forget Prob." in display_df.columns:
            display_df["Forget Prob."] = display_df["Forget Prob."].apply(
                lambda x: f"{x:.1%}" if isinstance(x, (int, float)) and x <= 1 else f"{x}"
            )
        st.dataframe(
            display_df, use_container_width=True,
            height=min(400, 50 + len(display_df) * 45), hide_index=True,
        )
    else:
        render_empty_state("📌", "No recommendations available right now")

    if show_all:
        section_divider()

# --- DECAY ANALYSIS ---
if show_all or page == "Decay Analysis":
    if not show_all:
        st.markdown("""
        <div style="margin-bottom: 8px;">
            <h1 style="font-size: 2rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.03em; margin: 0 0 4px 0; line-height: 1.1;">📉 Decay Analysis</h1>
            <p style="font-size: 0.92rem; color: #64748b; font-weight: 400; margin: 0;">Visualize which problems you're most likely to forget</p>
        </div>
        """, unsafe_allow_html=True)
        section_divider()
    else:
        st.markdown('<p class="section-header">📉 Knowledge Decay Analysis</p>', unsafe_allow_html=True)

    recommendations = safe_api_call("/recommendations")

    if recommendations and len(recommendations) > 0:
        chart_df = pd.DataFrame(recommendations)

        if "forget_probability" in chart_df.columns and "title" in chart_df.columns:
            if chart_df["forget_probability"].max() <= 1:
                chart_df["forget_probability"] = chart_df["forget_probability"] * 100

            chart_df = chart_df.sort_values("forget_probability", ascending=True)
            chart_df["severity"] = pd.cut(
                chart_df["forget_probability"],
                bins=[0, 30, 60, 100],
                labels=["Low Risk", "Medium Risk", "High Risk"],
            )
            color_map = {"Low Risk": "#22c55e", "Medium Risk": "#f59e0b", "High Risk": "#ef4444"}

            fig = px.bar(
                chart_df, x="forget_probability", y="title",
                color="severity", color_discrete_map=color_map, orientation="h",
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#94a3b8", size=12),
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis=dict(
                    title="Forget Probability (%)",
                    gridcolor="rgba(255,255,255,0.04)",
                    linecolor="rgba(255,255,255,0.06)", range=[0, 105],
                ),
                yaxis=dict(
                    title=None, gridcolor="rgba(255,255,255,0.04)",
                    linecolor="rgba(255,255,255,0.06)", tickfont=dict(size=11),
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
                bargap=0.3,
                hoverlabel=dict(bgcolor="#1e293b", bordercolor="#6366f1", font=dict(family="Inter", color="#e2e8f0", size=13)),
            )
            fig.update_traces(
                marker=dict(cornerradius=4, line=dict(width=0)),
                hovertemplate="<b>%{y}</b><br>Forget Probability: %{x:.1f}%<extra></extra>",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            render_empty_state("📉", "Missing required data for decay chart")
    else:
        render_empty_state("📉", "No data available for decay analysis")

    if show_all:
        section_divider()

# --- TOPIC MASTERY & PATTERN COVERAGE ---
if show_all or page == "Topic Mastery" or page == "Pattern Coverage":
    if not show_all:
        if page == "Topic Mastery":
            st.markdown("""
            <div style="margin-bottom: 8px;">
                <h1 style="font-size: 2rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.03em; margin: 0 0 4px 0; line-height: 1.1;">📚 Topic Mastery</h1>
                <p style="font-size: 0.92rem; color: #64748b; font-weight: 400; margin: 0;">Track proficiency across all DSA topics</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="margin-bottom: 8px;">
                <h1 style="font-size: 2rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.03em; margin: 0 0 4px 0; line-height: 1.1;">🎯 Pattern Coverage</h1>
                <p style="font-size: 0.92rem; color: #64748b; font-weight: 400; margin: 0;">See how well you've covered each pattern</p>
            </div>
            """, unsafe_allow_html=True)
        section_divider()

    if show_all or page == "Topic Mastery":
        col_topics, col_patterns = st.columns(2)

        with col_topics:
            if show_all:
                st.markdown('<p class="section-header">📚 Topic Mastery</p>', unsafe_allow_html=True)

            topic_data = safe_api_call("/topic-mastery")

            if topic_data and len(topic_data) > 0:
                topic_df = pd.DataFrame(topic_data)
                if "mastery" in topic_df.columns and topic_df["mastery"].max() <= 1:
                    topic_df["mastery"] = topic_df["mastery"] * 100
                topic_df = topic_df.sort_values("mastery", ascending=True)
                topic_df["level"] = pd.cut(topic_df["mastery"], bins=[0, 30, 60, 80, 100], labels=["Beginner", "Intermediate", "Advanced", "Expert"])
                level_colors = {"Beginner": "#ef4444", "Intermediate": "#f59e0b", "Advanced": "#6366f1", "Expert": "#22c55e"}

                fig = px.bar(topic_df, x="mastery", y="topic", color="level", color_discrete_map=level_colors, orientation="h")
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#94a3b8", size=11),
                    margin=dict(t=5, b=5, l=5, r=5),
                    xaxis=dict(range=[0, 105], gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)", title="Mastery (%)", title_font=dict(size=10)),
                    yaxis=dict(title=None, gridcolor="rgba(255,255,255,0.04)", tickfont=dict(size=10)),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9)),
                    bargap=0.3,
                    hoverlabel=dict(bgcolor="#1e293b", bordercolor="#6366f1", font=dict(family="Inter", color="#e2e8f0", size=12)),
                )
                fig.update_traces(marker=dict(cornerradius=4, line=dict(width=0)), hovertemplate="<b>%{y}</b><br>Mastery: %{x:.1f}%<extra></extra>")
                st.plotly_chart(fig, use_container_width=True)
            else:
                render_empty_state("📚", "No topic data available")

        with col_patterns:
            if show_all:
                st.markdown('<p class="section-header">🎯 Pattern Coverage</p>', unsafe_allow_html=True)

            pattern_data = safe_api_call("/pattern-coverage")

            if pattern_data and len(pattern_data) > 0:
                pattern_df = pd.DataFrame(pattern_data)
                if "coverage" in pattern_df.columns and pattern_df["coverage"].max() <= 1:
                    pattern_df["coverage"] = pattern_df["coverage"] * 100
                pattern_df = pattern_df.sort_values("coverage", ascending=True)
                pattern_df["status"] = pd.cut(pattern_df["coverage"], bins=[0, 30, 60, 100], labels=["Low", "Medium", "High"])
                status_colors = {"Low": "#ef4444", "Medium": "#f59e0b", "High": "#22c55e"}

                fig = px.bar(pattern_df, x="coverage", y="pattern", color="status", color_discrete_map=status_colors, orientation="h")
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#94a3b8", size=11),
                    margin=dict(t=5, b=5, l=5, r=5),
                    xaxis=dict(range=[0, 105], gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)", title="Coverage (%)", title_font=dict(size=10)),
                    yaxis=dict(title=None, gridcolor="rgba(255,255,255,0.04)", tickfont=dict(size=10)),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9)),
                    bargap=0.3,
                    hoverlabel=dict(bgcolor="#1e293b", bordercolor="#6366f1", font=dict(family="Inter", color="#e2e8f0", size=12)),
                )
                fig.update_traces(marker=dict(cornerradius=4, line=dict(width=0)), hovertemplate="<b>%{y}</b><br>Coverage: %{x:.1f}%<extra></extra>")
                st.plotly_chart(fig, use_container_width=True)
            else:
                render_empty_state("🎯", "No pattern data available")

    if show_all:
        section_divider()

# --- WEAK AREAS ---
if show_all or page == "Weak Areas":
    if not show_all:
        st.markdown("""
        <div style="margin-bottom: 8px;">
            <h1 style="font-size: 2rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.03em; margin: 0 0 4px 0; line-height: 1.1;">⚠️ Weak Areas</h1>
            <p style="font-size: 0.92rem; color: #64748b; font-weight: 400; margin: 0;">Identify your weakest topics and patterns</p>
        </div>
        """, unsafe_allow_html=True)
        section_divider()

    col_weak_t, col_weak_p = st.columns(2)

    with col_weak_t:
        st.markdown('<p class="section-header">⚠️ Weak Topics</p>', unsafe_allow_html=True)
        weak_topics = safe_api_call("/weak-topics")

        if weak_topics and len(weak_topics) > 0:
            weak_df = pd.DataFrame(weak_topics)
            col_renames = {"topic": "Topic", "mastery": "Mastery", "total_questions": "Questions", "solved": "Solved", "accuracy": "Accuracy"}
            display_weak = weak_df.rename(columns={k: v for k, v in col_renames.items() if k in weak_df.columns})
            if "Mastery" in display_weak.columns:
                display_weak["Mastery"] = display_weak["Mastery"].apply(
                    lambda x: f"{x:.1%}" if isinstance(x, (int, float)) and x <= 1 else f"{x:.1f}%"
                )
            st.dataframe(display_weak, use_container_width=True, hide_index=True, height=min(350, 50 + len(display_weak) * 42))
        else:
            render_empty_state("✅", "No weak topics — great job!")

    with col_weak_p:
        st.markdown('<p class="section-header">🚨 Weak Patterns</p>', unsafe_allow_html=True)
        weak_patterns = safe_api_call("/weak-patterns")

        if weak_patterns and len(weak_patterns) > 0:
            weak_pattern_df = pd.DataFrame(weak_patterns)
            col_renames = {"pattern": "Pattern", "coverage": "Coverage", "total_questions": "Questions", "solved": "Solved", "accuracy": "Accuracy"}
            display_weak_p = weak_pattern_df.rename(columns={k: v for k, v in col_renames.items() if k in weak_pattern_df.columns})
            if "Coverage" in display_weak_p.columns:
                display_weak_p["Coverage"] = display_weak_p["Coverage"].apply(
                    lambda x: f"{x:.1%}" if isinstance(x, (int, float)) and x <= 1 else f"{x:.1f}%"
                )
            st.dataframe(display_weak_p, use_container_width=True, hide_index=True, height=min(350, 50 + len(display_weak_p) * 42))
        else:
            render_empty_state("✅", "No weak patterns — keep it up!")

    if show_all:
        section_divider()

# --- CONTEST ANALYZER ---
if show_all or page == "Contest Analyzer":
    if not show_all:
        st.markdown("""
        <div style="margin-bottom: 8px;">
            <h1 style="font-size: 2rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.03em; margin: 0 0 4px 0; line-height: 1.1;">🏆 Contest Analyzer</h1>
            <p style="font-size: 0.92rem; color: #64748b; font-weight: 400; margin: 0;">Contest questions matched to your weak patterns</p>
        </div>
        """, unsafe_allow_html=True)
        section_divider()
    else:
        st.markdown('<p class="section-header">🏆 Contest Analyzer</p>', unsafe_allow_html=True)

    contest_data = safe_api_call("/contest-analyzer")

    if contest_data and len(contest_data) > 0:
        contest_df = pd.DataFrame(contest_data)
        col_renames = {"question": "Question", "contest": "Contest", "difficulty": "Difficulty", "pattern": "Pattern", "topic": "Topic", "url": "Link", "rating": "Rating"}
        display_contest = contest_df.rename(columns={k: v for k, v in col_renames.items() if k in contest_df.columns})
        st.dataframe(display_contest, use_container_width=True, hide_index=True, height=min(400, 50 + len(display_contest) * 42))
    else:
        render_empty_state("🏆", "No contest questions matched your current weak patterns.")

    if show_all:
        section_divider()

# --- AI CONTEST REVIEW ---
if show_all or page == "Contest Analyzer":
    if show_all:
        st.markdown('<p class="section-header">🧠 AI Contest Review</p>', unsafe_allow_html=True)

    contest_ai = safe_api_call("/contest-ai")

    if contest_ai:
        if isinstance(contest_ai, dict) and "review" in contest_ai:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(34, 197, 94, 0.08), rgba(16, 185, 129, 0.04));
                border: 1px solid rgba(34, 197, 94, 0.2);
                border-radius: 12px;
                padding: 20px 24px;
            ">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                    <span style="font-size: 1.1rem;">🤖</span>
                    <span style="color: #86efac; font-weight: 600; font-size: 0.9rem;">AI Review</span>
                </div>
                <div style="color: #d1d5db; font-size: 0.92rem; line-height: 1.7;">{contest_ai['review']}</div>
            </div>
            """, unsafe_allow_html=True)
        elif isinstance(contest_ai, list) and len(contest_ai) > 0:
            for idx, item in enumerate(contest_ai):
                question_title = item.get("question", f"Question #{idx + 1}")
                pattern = item.get("pattern", "N/A")
                difficulty = item.get("difficulty", "N/A")
                ai_review = item.get("ai_review", "No review available.")
                diff_colors = {"Easy": "#22c55e", "Medium": "#f59e0b", "Hard": "#ef4444"}
                badge_color = diff_colors.get(difficulty, "#6366f1")

                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.4));
                    border: 1px solid rgba(255,255,255,0.06);
                    border-radius: 12px;
                    padding: 20px 24px;
                    margin-bottom: 12px;
                ">
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
                        <span style="color: #f1f5f9; font-weight: 600; font-size: 1rem;">{question_title}</span>
                        <div style="display: flex; gap: 8px;">
                            <span style="background: rgba(99,102,241,0.15); color: #a5b4fc; font-size: 0.75rem; font-weight: 600; padding: 4px 12px; border-radius: 20px;">{pattern}</span>
                            <span style="background: {badge_color}20; color: {badge_color}; font-size: 0.75rem; font-weight: 600; padding: 4px 12px; border-radius: 20px;">{difficulty}</span>
                        </div>
                    </div>
                    <div style="background: rgba(34, 197, 94, 0.06); border-left: 3px solid #22c55e; padding: 12px 16px; border-radius: 0 8px 8px 0;">
                        <div style="color: #d1d5db; font-size: 0.88rem; line-height: 1.7;">{ai_review}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        render_empty_state("🧠", "No AI contest review available")

    if show_all:
        section_divider()

# --- AI INTERVIEW PLANNER ---
if show_all or page == "Interview Planner":
    if not show_all:
        st.markdown("""
        <div style="margin-bottom: 8px;">
            <h1 style="font-size: 2rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.03em; margin: 0 0 4px 0; line-height: 1.1;">📅 Interview Planner</h1>
            <p style="font-size: 0.92rem; color: #64748b; font-weight: 400; margin: 0;">Get a personalized AI revision plan before your interview</p>
        </div>
        """, unsafe_allow_html=True)
        section_divider()
    else:
        st.markdown('<p class="section-header">🎯 AI Interview Planner</p>', unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.4));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
    ">
    """, unsafe_allow_html=True)

    interview_col1, interview_col2 = st.columns([1, 2])

    with interview_col1:
        interview_date = st.date_input(
            "Select Interview Date",
            value=None,
            min_value=datetime.now().date(),
            label_visibility="collapsed",
        )

    with interview_col2:
        generate_clicked = st.button(
            "🚀 Generate Interview Plan",
            type="primary",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if generate_clicked and interview_date:
        with st.spinner("Generating your personalized interview plan..."):
            result = safe_api_call(
                "/interview-ai",
                params={"interview_date": interview_date.strftime("%Y-%m-%d")},
            )

        if result and isinstance(result, dict):
            col_plan, col_ai = st.columns(2)

            with col_plan:
                st.markdown("""
                <div style="font-size: 0.85rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;">
                    📅 Plan Summary
                </div>
                """, unsafe_allow_html=True)

                if "plan" in result:
                    plan = result["plan"]
                    st.write(f"**📅 Interview Date:** {plan['interview_date']}")
                    st.write(f"**⏳ Days Remaining:** {plan['days_remaining']}")

                    st.markdown("### ⚠️ Weak Topics")
                    if plan["weak_topics"]:
                        for topic in plan["weak_topics"]:
                            st.write(f"• **{topic['topic']}** ({topic['mastery']}%)")
                    else:
                        st.write("No weak topics found.")

                    st.markdown("### 🚨 Weak Patterns")
                    if plan["weak_patterns"]:
                        for pattern in plan["weak_patterns"]:
                            st.write(f"• **{pattern['pattern']}** ({pattern['coverage']}%)")
                    else:
                        st.write("No weak patterns found.")

            with col_ai:
                st.markdown("""
                <div style="font-size: 0.85rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;">
                    🤖 AI Revision Plan
                </div>
                """, unsafe_allow_html=True)

                if "ai_plan" in result:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(34, 197, 94, 0.08), rgba(16, 185, 129, 0.04));
                        border: 1px solid rgba(34, 197, 94, 0.2);
                        border-radius: 12px;
                        padding: 20px 24px;
                    ">
                        <div style="color: #d1d5db; font-size: 0.92rem; line-height: 1.8; white-space: pre-wrap;">{result['ai_plan']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            render_empty_state("🎯", "Could not generate interview plan")

    elif generate_clicked and not interview_date:
        st.warning("Please select an interview date first.")

    if show_all:
        section_divider()

# --- AI COACH ---
if show_all or page == "AI Coach":
    if not show_all:
        st.markdown("""
        <div style="margin-bottom: 8px;">
            <h1 style="font-size: 2rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.03em; margin: 0 0 4px 0; line-height: 1.1;">🤖 AI Coach</h1>
            <p style="font-size: 0.92rem; color: #64748b; font-weight: 400; margin: 0;">Personalized revision advice based on your learning patterns</p>
        </div>
        """, unsafe_allow_html=True)
        section_divider()
    else:
        st.markdown('<p class="section-header">🤖 AI Coach Advice</p>', unsafe_allow_html=True)

    coach_data = safe_api_call("/dynamic-ai-coach")

    if coach_data and isinstance(coach_data, list) and len(coach_data) > 0:
        coach_cols = st.columns(2)

        for idx, item in enumerate(coach_data):
            col = coach_cols[idx % 2]
            with col:
                question_title = item.get("question", "Unknown Question")
                forget_prob = item.get("forget_probability", 0)
                advice = item.get("advice", "No advice available.")

                if isinstance(forget_prob, (int, float)) and forget_prob <= 1:
                    forget_prob_display = f"{forget_prob:.1%}"
                else:
                    forget_prob_display = f"{forget_prob}"

                if isinstance(forget_prob, (int, float)):
                    if forget_prob <= 0.3 or forget_prob <= 30:
                        risk_color = "#22c55e"
                        risk_label = "Low Risk"
                    elif forget_prob <= 0.6 or forget_prob <= 60:
                        risk_color = "#f59e0b"
                        risk_label = "Medium Risk"
                    else:
                        risk_color = "#ef4444"
                        risk_label = "High Risk"
                else:
                    risk_color = "#6366f1"
                    risk_label = "Unknown"

                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.4));
                    border: 1px solid rgba(255,255,255,0.06);
                    border-radius: 12px;
                    padding: 20px 24px;
                    margin-bottom: 12px;
                ">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: #f1f5f9; font-weight: 600; font-size: 0.95rem; flex: 1; margin-right: 12px; line-height: 1.4;">
                            {question_title}
                        </span>
                        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px; flex-shrink: 0;">
                            <span style="background: {risk_color}20; color: {risk_color}; font-size: 0.7rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.05em;">
                                {risk_label}
                            </span>
                            <span style="color: #64748b; font-size: 0.75rem; font-weight: 500;">
                                {forget_prob_display} forget
                            </span>
                        </div>
                    </div>
                    <div style="background: rgba(99, 102, 241, 0.06); border-left: 3px solid #6366f1; padding: 12px 16px; border-radius: 0 8px 8px 0;">
                        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                            <span style="font-size: 0.8rem;">🤖</span>
                            <span style="color: #818cf8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;">
                                Coach Advice
                            </span>
                        </div>
                        <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.7;">{advice}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        render_empty_state("🤖", "No AI coach advice available at this time")

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div style="
    text-align: center;
    padding: 32px 0 16px 0;
    margin-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.04);
">
    <span style="color: #334155; font-size: 0.78rem; font-weight: 400;">
        LeetRecall AI — Intelligent DSA Revision & Retention System
    </span>
</div>
""", unsafe_allow_html=True)