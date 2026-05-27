"""
PostBot — India Post District Intelligence Engine
v10: True CSS fixed sidebar (no layout push) · Claude-style chat · Perfect palette
"""

import streamlit as st
import pandas as pd
import csv, os, datetime
from auth import authenticate, get_demo_credentials
from model_utils import (
    load_district_data, get_states, get_districts,
    get_district_info, get_tier, calculate_suggestion,
)
from chatbot import ask_postbot

st.set_page_config(
    page_title="PostBot",
    page_icon=":mailbox:",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}
)

def init():
    defaults = {
        "page":              "home",
        "officer":           None,
        "district_info":     None,
        "suggestion":        None,
        "chat":              [],
        "chat_history":      [],
        "dark_mode":         False,
        "district_analysed": False,
        "sidebar_open":      True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

DAY = {
    "bg":        "#FBF7F2",
    "sidebar":   "#EDE5D8",
    "card":      "#FFFFFF",
    "border":    "#C08552",
    "accent":    "#8C5A3C",
    "text":      "#3A2218",
    "text2":     "#6B4040",
    "text3":     "#8C5A3C",
    "muted":     "#B07850",
    "bubble_u":  "#8C5A3C",
    "bubble_b":  "#F5EDE0",
    "input_bg":  "#FFFFFF",
}
NIGHT = {
    "bg":        "#1A0F08",
    "sidebar":   "#120A04",
    "card":      "#2A1A0E",
    "border":    "#8C5A3C",
    "accent":    "#D4956A",
    "text":      "#FFF8F0",
    "text2":     "#EDD8C0",
    "text3":     "#D4956A",
    "muted":     "#A07848",
    "bubble_u":  "#6B3A28",
    "bubble_b":  "#2A1A0E",
    "input_bg":  "#2A1A0E",
}

def C():
    return DAY if not st.session_state.get("dark_mode", False) else NIGHT


def inject_css():
    c = C()
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset ── */
*, *::before, *::after {{ box-sizing: border-box; }}
html, body {{ margin:0; padding:0; background:{c['bg']} !important; }}
.stApp {{ background:{c['bg']} !important; }}

/* ── Hide all Streamlit chrome ── */
/* Remove ghost keyboard toggle text */
[data-testid="stSidebarCollapseButton"] {{
    display: none !important;
}}

button[title="View sidebar"] {{
    display: none !important;
}}

button[title="Hide sidebar"] {{
    display: none !important;
}}

/* Remove floating accessibility text */
div[aria-label="dialog"] {{
    display: none !important;
}}

#MainMenu, footer,
[data-testid="stSidebarNav"],
.stDeployButton,
[data-testid="stToolbarActions"],
[data-testid="stAppDeployButton"],
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stExpandSidebarButton"],
button[kind="header"]
{{ display:none !important; visibility:hidden !important; }}

/* ── Sidebar ───────────────────────────────────────── */

[data-testid="stSidebar"] {{
    background: {c['sidebar']} !important;
    border-right: 2px solid {c['border']}33 !important;
    min-width: 240px !important;
    max-width: 240px !important;
    width: 240px !important;
    padding: 0 !important;
    margin: 0 !important;
    top: 0 !important;
}}

[data-testid="stSidebar"][aria-expanded="false"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    min-width: 240px !important;
    width: 240px !important;
}}

[data-testid="stSidebar"] > div:first-child {{
    padding: 0px 10px 2px !important;
    margin-top: 0 !important;
    overflow-y: auto !important;
    height: 100vh !important;
}}

[data-testid="stSidebarContent"],
section[data-testid="stSidebar"],
section[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"],
.css-1d391kg,
.css-6qob1r {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}

/* ── Kill the sidebar header space (collapse button container) ── */
[data-testid="stSidebarHeader"] {{
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}}

/* ── Kill UserContent bottom padding (sidebarTopSpace) ── */
[data-testid="stSidebarUserContent"] {{
    padding-top: 30px !important;
    padding-bottom: 0 !important;
    margin-top: 0 !important;
}}

/* ── Target the Emotion class directly (eelgd2m4 = stSidebarHeader) ── */
.css-eelgd2m4,
div[data-testid="stSidebarHeader"] {{
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}

/* ── Main content area ── */
.block-container {{
    max-width: 100% !important;
    padding-top: 6 !important;
    padding-bottom: 0 !important;

    padding-left: 24px !important;
    padding-right: 24px !important;

    margin-left: 0 !important;
    margin-right: 0 !important;
}}
[data-testid="stMainBlockContainer"] {{
    padding-top: 0 !important;
    padding-left: 24px !important;
    padding-right: 24px !important;
    max-width: 100% !important;
}}
section[data-testid="stMain"] > div:first-child,
section.main > div:first-child {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}

/* Remove remaining top whitespace */
section.main > div {{
    padding-top: 0 !important;
}}

section[data-testid="stMain"] > div {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}

[data-testid="stAppViewContainer"] {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}

/* ════ PAGE CHROME ════ */
/* Force sidebar to stay in layout — never slide off screen */
[data-testid="stSidebar"] {{
    left: 0 !important;
    transform: translateX(0) !important;
}}
section[data-testid="stSidebarContent"] {{
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
}}
.pb-page {{ padding-bottom: 20px; }}
.pb-page-chat {{ min-height: 100vh; }}

/* ════ PAGE WRAPPERS ════ */
.pb-page {{
    padding: 0 !important;
    margin: 0 !important;
    background: {c['bg']};
    font-family: 'DM Sans', sans-serif;
}}
.pb-page-chat {{
    background: {c['bg']};
}}


/* ════ TYPOGRAPHY ════ */
h1,h2,h3,h4 {{
    font-family: 'Playfair Display', serif !important;
    color: {c['text']} !important;
}}

.stMarkdown p {{
    font-size:14px !important;
}}

/* global markdown text */
.stMarkdown {{
    color: {c['text2']} !important;
}}
.pb-h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 42px; font-weight: 700;
    color: {c['text']}; line-height: 1.15; margin-bottom: 10px;
}}
.pb-h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 22px; font-weight: 700;
    color: {c['text']}; margin-bottom: 3px;
}}
.pb-label {{
    font-family: 'DM Sans', sans-serif;
    font-size: 10px; font-weight: 700;
    color: {c['muted']};
    text-transform: uppercase; letter-spacing: 1.3px;
    margin-bottom: 8px;
}}
.pb-sub {{
    font-family: 'DM Sans', sans-serif;
    font-size: 12px; color: {c['muted']};
    margin-bottom: 14px;
}}

/* ════ CARDS ════ */
.pb-card {{
    background: {c['card']};
    border: 1px solid {c['border']}2A;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
}}
.pb-card-l {{
    border-left: 3px solid {c['accent']};
}}
.pb-card-t {{
    border-top: 3px solid {c['accent']};
}}
.pb-num {{
    font-family: 'Playfair Display', serif;
    font-size: 38px; font-weight: 700;
    color: {c['accent']}; line-height: 1; margin-bottom: 3px;
}}

/* ════ INPUTS ════ */
.stTextInput > div > div > input {{
    background: {c['input_bg']} !important;
    border: 1.5px solid {c['border']}55 !important;
    border-radius: 10px !important;
    color: {c['text']} !important;
    font-size: 14px !important;
    padding: 11px 14px !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {c['accent']} !important;
    box-shadow: 0 0 0 3px {c['accent']}12 !important;
    outline: none !important;
}}
.stTextInput label, .stSelectbox label {{
    color: {c['muted']} !important; font-size: 10px !important;
    font-weight: 700 !important; text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.stTextInput {{
    margin-bottom: -8px !important;
}}

.stTextInput > div {{
    margin-bottom: -2px !important;
}}
.stSelectbox > div > div {{
    background: {c['input_bg']} !important;
    border: 1.5px solid {c['border']}55 !important;
    border-radius: 10px !important; color: {c['text']} !important;
}}

/* Dropdown popup */
div[data-baseweb="popover"] {{
    background: {c['card']} !important;
}}

div[data-baseweb="select"] > div {{
    background: {c['input_bg']} !important;
    color: {c['text']} !important;
}}

ul {{
    background: {c['card']} !important;
}}

li[role="option"] {{
    background: {c['card']} !important;
    color: {c['text']} !important;
}}

li[role="option"]:hover {{
    background: {c['accent']}22 !important;
    color: {c['text']} !important;
}}

/* Main page buttons only */

section[data-testid="stMain"] .stButton > button {{
    background: {c['accent']} !important;
    color: #FFF8F0 !important;
    border: 2px solid {c['accent']} !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 18px !important;
    width: 100% !important;
    transition: all 0.15s !important;
    font-family: 'DM Sans', sans-serif !important;
}}

section[data-testid="stMain"] .stButton > button:hover {{
    background: transparent !important;
    color: {c['accent']} !important;
}}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {{

    background: {c['accent']} !important;
    color: #FFF8F0 !important;

    border: 2px solid {c['accent']} !important;
    border-radius: 10px !important;

    font-weight: 600 !important;
    font-size: 13px !important;

    padding: 10px 20px !important;

    width: 100% !important;

    transition: all 0.15s !important;

    font-family: 'DM Sans', sans-serif !important;

    min-height: 36px !important;

    box-shadow: none !important;
}}

[data-testid="stSidebar"] .stButton > button:hover {{

    background: transparent !important;
    color: {c['accent']} !important;

    border: 2px solid {c['accent']} !important;
}}


/* ════ CHAT ════ */
.user-row {{ display:flex; justify-content:flex-end; align-items:flex-end; gap:8px; margin:8px 0; }}
.user-bubble {{
    background: {c['bubble_u']}; color: #FFF8F0;
    border-radius: 18px 4px 18px 18px;
    padding: 11px 16px; max-width: 62%;
    font-family: 'DM Sans', sans-serif; font-size: 13px; line-height: 1.65;
    box-shadow: 0 1px 4px rgba(0,0,0,0.10);
}}
.bot-bubble {{
    background: transparent !important;
    color: {c['text']} !important;

    border: none !important;
    box-shadow: none !important;

    border-radius: 0 !important;

    padding: 2px 4px 2px 0 !important;

    max-width: 92% !important;

    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
}}

/* remove white markdown/code blocks */
/* clean markdown/code blocks */
.bot-bubble pre,
.bot-bubble code {{

    background: rgba(140,90,60,.06) !important;

    border: none !important;
    box-shadow: none !important;

    border-radius: 10px !important;

    padding: 10px 12px !important;

    color: {c['text']} !important;

    white-space: pre-wrap !important;

    overflow-x: auto !important;
}}
/* ordered list numbers */
.bot-bubble ol li::marker {{
    color: {c['text']} !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}}

/* unordered bullets */
.bot-bubble ul li::marker {{
    color: {c['text']} !important;
}}
/* cleaner paragraphs */
.bot-bubble p {{
    margin-bottom: 6px !important;
    color: {c['text']} !important;
}}

/* compact spacing */
.bot-row {{
    margin: 6px 0 !important;
    align-items: flex-start !important;
}}

/* chatbot text */
.bot-bubble p,
.bot-bubble div,
.bot-bubble span,
.bot-bubble strong,
.bot-bubble b,
.bot-bubble li {{
    color: {c['text']} !important;
}}

/* ordered list numbers */
.bot-bubble ol li::marker {{
    color: {c['text3']} !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}}

/* specifically fix numbered lists */
.bot-bubble ol li,
.bot-bubble ul li {{
    color: {c['text']} !important;
    opacity: 1 !important;
}}

/* fix bold text */
.bot-bubble strong,
.bot-bubble b {{
    color: {c['text']} !important;
}}

/* fix markdown containers */
.bot-bubble .stMarkdown,
.bot-bubble .stMarkdown p,
.bot-bubble .stMarkdown li {{
    color: {c['text']} !important;
}}

/* remove faded/transparent effect */
.bot-bubble {{
    opacity: 1 !important;
}}

/* bot markdown override */
.bot-bubble .stMarkdown p,
.bot-bubble .stMarkdown li,
.bot-bubble .stMarkdown ol li,
.bot-bubble .stMarkdown ul li {{
    color: {c['text']} !important;
    opacity: 1 !important;
}}

/* numbered markers */
.bot-bubble .stMarkdown ol li::marker {{
    color: {c['text3']} !important;
    font-weight: 700 !important;
}}

/* Chip buttons — pill style applied directly to Streamlit buttons in chip area */
.pb-chips .stButton > button {{
    background: {c['card']} !important;
    border: 1.5px solid {c['border']}44 !important;
    border-radius: 20px !important;
    color: {c['text3']} !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 7px 14px !important;
    min-height: 0 !important;
    height: auto !important;
    transition: all 0.15s !important;
    box-shadow: none !important;
}}
.pb-chips .stButton > button:hover {{
    background: {c['accent']}10 !important;
    border-color: {c['accent']}66 !important;
    color: {c['accent']} !important;
}}

/* ════ MISC ════ */
.stProgress > div > div > div {{
    background: {c['accent']} !important; border-radius: 4px !important;
}}
.stProgress > div > div {{
    background: {c['border']}22 !important;
    border-radius: 4px !important; height: 6px !important;
}}
div[data-testid="stAlert"] {{
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}}
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-thumb {{
    background: {c['border']}44; border-radius: 4px;
}}

/* Password eye toggle */
button[title="Show password text"],
button[title="Hide password text"] {{

    background: {c['accent']} !important;
    color: #FFF8F0 !important;

    border: 2px solid {c['accent']} !important;
    border-left: none !important;

    border-radius: 0 12px 12px 0 !important;

    box-shadow: none !important;
}}

button[title="Show password text"]:hover,
button[title="Hide password text"]:hover {{

    background: {c['text3']} !important;
    color: #FFF8F0 !important;
}}

/* Password field wrapper */
div[data-testid="stTextInput"]:has(input[type="password"]) > div {{

    background: transparent !important;
    border: none !important;
}}

/* Eye icon outer container */
div[data-testid="stTextInput"]:has(input[type="password"]) button {{

    background: {c['accent']} !important;

    border: 2px solid {c['accent']} !important;
    border-left: none !important;

    border-radius: 0 12px 12px 0 !important;

    min-height: 52px !important;

    box-shadow: none !important;
}}

/* Hover */
div[data-testid="stTextInput"]:has(input[type="password"]) button:hover {{

    background: {c['text3']} !important;
    border-color: {c['text3']} !important;
}}

/* Remove dark wrapper behind password eye */
div[data-testid="stTextInput"] div:has(> button[title="Show password text"]),
div[data-testid="stTextInput"] div:has(> button[title="Hide password text"]) {{

    background: {c['accent']} !important;
    border-radius: 0 14px 14px 0 !important;

    border: none !important;
    box-shadow: none !important;
}}

/* Actual eye button */
button[title="Show password text"],
button[title="Hide password text"] {{

    background: transparent !important;

    color: #FFF8F0 !important;

    border: none !important;
    box-shadow: none !important;

    min-height: 52px !important;
}}

/* Hover */
button[title="Show password text"]:hover,
button[title="Hide password text"]:hover {{

    background: {c['text3']} !important;
}}

/* Remove dark input outline */
.stTextInput input {{

    border: 2px solid {c['border']}55 !important;
    box-shadow: none !important;
    outline: none !important;

    background: {c['input_bg']} !important;
    color: {c['text']} !important;
}}

/* Focus state */
.stTextInput input:focus {{

    border: 2px solid {c['accent']} !important;

    box-shadow: 0 0 0 2px {c['accent']}22 !important;
    outline: none !important;
}}

/* Wrapper */
.stTextInput > div > div {{

    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}}

input {{

    outline: none !important;
    box-shadow: none !important;
    border-color: {c['border']}55 !important;
}}

/* Browser autofill fix */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
textarea:-webkit-autofill,
select:-webkit-autofill {{

    -webkit-text-fill-color: {c['text']} !important;

    transition: background-color 9999s ease-in-out 0s !important;

    box-shadow: 0 0 0px 1000px {c['input_bg']} inset !important;

    border: 2px solid {c['accent']} !important;
}}

/* Autofill dropdown */
input:-webkit-autofill::first-line {{
    color: #FFF8F0 !important;
}}
</style>
""", unsafe_allow_html=True)


def render_navbar():
    c    = C()
    page = st.session_state.get("page", "home")
    o    = st.session_state.get("officer", None)
    dm   = st.session_state.get("dark_mode", False)

    if o:
        items = [
            ("home",     "🏠", "Home"),
            ("district", "📍", "District"),
        ]

        if st.session_state.get("district_analysed", False):
            items.extend([
                ("chat",     "💬", "PostBot Chat"),
                ("analysis", "📊", "Full Analysis"),
            ])
    else:
        items = [
            ("home",     "🏠", "Home"),
            ("login",    "🔑", "Login"),
            ("signup",   "📝", "Signup"),
        ]
    visible = items

    with st.sidebar:
        # ── Brand ─────────────────────────────────────────────────────────────
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;
     padding:0 0 6px;border-bottom:1px solid {c['border']}33;margin-bottom:4px;">
  <div style="width:36px;height:36px;border-radius:10px;background:{c['accent']};
       display:flex;align-items:center;justify-content:center;flex-shrink:0;
       box-shadow:0 2px 8px {c['accent']}44;">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
         stroke="#FFF8F0" stroke-width="2.5">
      <rect x="2" y="4" width="20" height="16" rx="2"/>
      <path d="M2 8l10 6 10-6"/>
    </svg>
  </div>
  <div>
    <div style="font-family:'Playfair Display',serif;font-size:17px;
         font-weight:900;color:{c['text']};line-height:1.1;">PostBot</div>
    <div style="font-size:9px;color:{c['muted']};letter-spacing:1.5px;
         text-transform:uppercase;margin-top:2px;">India Post Intelligence</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Section label ─────────────────────────────────────────────────────
        st.markdown(
            f'<div style="font-size:9px;font-weight:700;color:{c["muted"]};'
            f'letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;'
            f'padding-left:4px;">Navigation</div>',
            unsafe_allow_html=True
        )

        # ── Navigation buttons ────────────────────────────────────────────────

        for pg, icon, lbl in visible:
            if st.button(f"{icon}  {lbl}", key=f"nav_{pg}", use_container_width=True):
                st.session_state.page = pg
                st.rerun()
        
        # ── Divider ───────────────────────────────────────────────────────────
        st.markdown(
            f'<div style="border-top:1px solid {c["border"]}33;margin:14px 0 10px;"></div>',
            unsafe_allow_html=True)

        # ── Settings label ────────────────────────────────────────────────────
        st.markdown(
            f'<div style="font-size:9px;font-weight:700;color:{c["muted"]};'
            f'letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;'
            f'padding-left:4px;">Settings</div>',
            unsafe_allow_html=True
        )

       # ── Dark mode ─────────────────────────────────────────────────────────
        dm_icon = "☀️" if dm else "🌙"
        dm_lbl  = "Light Mode" if dm else "Dark Mode"

        if st.button(f"{dm_icon}  {dm_lbl}", key="nav_dm", use_container_width=True):
            st.session_state.dark_mode = not dm
            st.rerun()

        # ── Sign out ──────────────────────────────────────────────────────────
        if o:
            if st.button("🚪  Sign Out", key="nav_out", use_container_width=True):
                st.session_state.update({
                    "officer": None,
                    "page": "home",
                    "district_info": None,
                    "suggestion": None,
                    "chat": [],
                    "district_analysed": False,
                })
                st.rerun()

        # ── Officer card ──────────────────────────────────────────────────────
        if o:
            ini = "".join(w[0].upper() for w in o["name"].split()[:2])
            st.markdown(f"""
<div style="margin-top:auto;padding-top:10px;">
  <div style="background:{c['card']};border:1px solid {c['border']}44;
       border-radius:10px;padding:10px 12px;display:flex;align-items:center;gap:10px;
       box-shadow:0 1px 4px rgba(0,0,0,0.05);">
    <div style="width:32px;height:32px;border-radius:50%;
         background:linear-gradient(135deg,{c['accent']},{c['accent']}cc);
         display:flex;align-items:center;justify-content:center;
         font-size:11px;font-weight:800;color:#FFF8F0;flex-shrink:0;
         letter-spacing:0.5px;">{ini}</div>
    <div style="overflow:hidden;">
      <div style="font-size:12px;font-weight:700;color:{c['text']};
           white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{o['name']}</div>
      <div style="font-size:10px;color:{c['muted']};line-height:1.4;
           white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{o.get('role','')[:28]}</div>
    </div>
  </div>
  <div style="text-align:center;margin-top:10px;padding-bottom:4px;">
    <span style="font-size:9px;color:{c['muted']};letter-spacing:0.8px;">
      PostBot · Group 10 · Great Lakes PGP</span>
  </div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div style="margin-top:20px;text-align:center;padding-bottom:4px;">
  <span style="font-size:9px;color:{c['muted']};letter-spacing:0.8px;">
    PostBot · Group 10 · Great Lakes PGP</span>
</div>""", unsafe_allow_html=True)




# ─── CARD helper ──────────────────────────────────────────────────────────────
def card(content, border_left=None, border_top=None, pad="12px", mb="8px", extra=""):
    c = C()
    bl = f"border-left:3px solid {border_left};" if border_left else ""
    bt = f"border-top:3px solid {border_top};" if border_top else ""
    return (
        f'<div style="background:{c["card"]};border:1px solid {c["border"]}44;'
        f'border-radius:10px;padding:{pad};margin-bottom:{mb};{bl}{bt}{extra}">'
        f'{content}</div>'
    )

def label(text):
    c = C()
    return (f'<div style="color:{c["muted"]};font-size:10px;font-weight:700;'
            f'letter-spacing:1.2px;text-transform:uppercase;margin-bottom:6px;">{text}</div>')

def big_num(val, color):
    return (f'<div style="color:{color};font-family:\'Playfair Display\',serif;'
            f'font-size:42px;font-weight:900;line-height:1;margin-bottom:4px;">{val}</div>')


# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
def home_page():
    st.markdown('<div class="pb-page">', unsafe_allow_html=True)
    c = C()

    st.markdown(f"""
<div style="background:{c['sidebar']};padding:8px 28px 14px;border-bottom:1px solid {c['border']}22;">
  <div style="display:inline-block;background:{c['accent']}18;border:1px solid {c['border']}55;
       border-radius:20px;padding:4px 14px;margin-bottom:16px;">
    <span style="color:{c['accent']};font-size:11px;font-weight:700;letter-spacing:1.5px;">
      INDIA POST · GROUP 10 CAPSTONE · AI-POWERED
    </span>
  </div>
  <div style="font-family:'Playfair Display',serif;color:{c['text']};font-size:44px;
       font-weight:900;line-height:1.1;margin-bottom:14px;max-width:640px;">
    India Post's District<br>
    <span style="color:{c['accent']};">Intelligence</span> Engine
  </div>
  <div style="color:{c['text3']};font-size:15px;line-height:1.75;max-width:480px;margin-bottom:20px;">
    Analyse postal infrastructure across 754 districts. Understand delivery gaps,
    simulate scenarios, and get AI-driven recommendations.
  </div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;">
    {"".join(f'<span style="background:{c["accent"]}15;border:1px solid {c["border"]}66;border-radius:20px;padding:4px 12px;color:{c["text"]};font-size:12px;font-weight:600;">{t}</span>' for t in ["754 Districts","Groq Llama 3.3","36 States &amp; UTs","CatBoost R²=0.92"])}
  </div>
</div>
""", unsafe_allow_html=True)

    # Info sections
    st.markdown('<div style="padding:0px 28px;">', unsafe_allow_html=True)

    st.markdown(
        f'<div style="font-family:\'Playfair Display\',serif;color:{c["text"]};'
        f'font-size:20px;font-weight:800;margin-bottom:3px;">What PostBot Does</div>'
        f'<div style="color:{c["text3"]};font-size:12px;margin-bottom:14px;">Four capabilities in one interface</div>',
        unsafe_allow_html=True
    )
    cols = st.columns(4)
    for col, title, sub in [
        (cols[0], "Real Dataset",      "Actual BO, PO, HO counts from the India Post dataset."),
        (cols[1], "Delivery Analysis", "Classifies districts as Low / Moderate / Good / High tier."),
        (cols[2], "Smart Suggestions", "Calculates BOs needed to reach the next performance tier."),
        (cols[3], "AI Chatbot",        "Ask what-if questions and get instant action plans."),
    ]:
        with col:
            st.markdown(card(
                f'<div style="color:{c["text"]};font-weight:600;font-size:13px;margin-bottom:5px;">{title}</div>'
                f'<div style="color:{c["text3"]};font-size:12px;line-height:1.6;">{sub}</div>',
                border_top=c["accent"], mb="12px"
            ), unsafe_allow_html=True)

    st.markdown(
        f'<div style="font-family:\'Playfair Display\',serif;color:{c["text"]};'
        f'font-size:20px;font-weight:800;margin:12px 0 3px;">The 3 Post Office Types</div>'
        f'<div style="color:{c["text3"]};font-size:12px;margin-bottom:14px;">165,000+ offices nationwide</div>',
        unsafe_allow_html=True
    )
    ecols = st.columns(3)
    for col, name, rate, desc in [
        (ecols[0], "Branch Office (BO)",    "98.7%", "Backbone of rural delivery — strongest predictor of district performance."),
        (ecols[1], "Sub Post Office (PO)",  "76.2%", "1 in 4 has zero active delivery — the biggest gap in the system."),
        (ecols[2], "Head Post Office (HO)", "99.1%", "District HQ — extremely reliable, 1–3 per district."),
    ]:
        with col:
            st.markdown(card(
                f'<div style="color:{c["muted"]};font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:5px;">{name}</div>'
                f'{big_num(rate, c["accent"])}'
                f'<div style="color:{c["muted"]};font-size:10px;margin-bottom:6px;">delivery rate</div>'
                f'<div style="color:{c["text2"]};font-size:12px;line-height:1.5;">{desc}</div>',
                border_left=c["accent"], mb="12px"
            ), unsafe_allow_html=True)

    st.markdown(
        f'<div style="font-family:\'Playfair Display\',serif;color:{c["text"]};'
        f'font-size:20px;font-weight:800;margin:12px 0 3px;">Performance Tiers</div>'
        f'<div style="color:{c["text3"]};font-size:12px;margin-bottom:14px;">K-Means clustering of 720 districts</div>',
        unsafe_allow_html=True
    )
    tcols = st.columns(4)
    for col, dot, lbl, rng, sub in [
        (tcols[0], "#c0392b", "Low",      "< 70%",  "19 districts"),
        (tcols[1], "#d4a017", "Moderate", "70–85%", "235 districts"),
        (tcols[2], "#2563eb", "Good",     "85–95%", "261 districts"),
        (tcols[3], "#16a34a", "High",     "> 95%",  "205 districts"),
    ]:
        with col:
            st.markdown(card(
                f'<div style="width:10px;height:10px;border-radius:50%;background:{dot};margin:0 auto 7px;"></div>'
                f'<div style="color:{c["text"]};font-weight:700;font-size:13px;margin-bottom:2px;text-align:center;">{lbl}</div>'
                f'<div style="color:{c["accent"]};font-family:\'Playfair Display\',serif;font-size:15px;font-weight:900;margin:3px 0;text-align:center;">{rng}</div>'
                f'<div style="color:{c["text3"]};font-size:11px;text-align:center;">{sub}</div>',
                mb="12px"
            ), unsafe_allow_html=True)
            
    # ── Tableau Dashboards Section ─────────────────────────────
    st.markdown(
        f'<div style="font-family:\'Playfair Display\',serif;color:{c["text"]};'
        f'font-size:20px;font-weight:800;margin:12px 0 3px;">Live Tableau Dashboards</div>'
        f'<div style="color:{c["text3"]};font-size:12px;margin-bottom:14px;">Interactive national & district-level views</div>',
        unsafe_allow_html=True
    )
    dcols = st.columns(2)
    with dcols[0]:
        st.markdown(card(
            f'<div style="color:{c["muted"]};font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">Dashboard 1</div>'
            f'<div style="color:{c["text"]};font-weight:700;font-size:14px;margin-bottom:4px;">🗺️ National Overview</div>'
            f'<div style="color:{c["text3"]};font-size:12px;line-height:1.6;margin-bottom:10px;">754 districts · choropleth map · tier distribution · state rankings</div>'
            f'<a href="https://public.tableau.com/app/profile/vishwadesai.ds/viz/IndiaPostInfrastructure/NationalOverview" target="_blank" '
            f'style="background:{c["accent"]};color:#FFF8F0;padding:7px 16px;border-radius:8px;'
            f'font-size:12px;font-weight:700;text-decoration:none;display:inline-block;">View Dashboard →</a>',
            border_top=c["accent"], mb="12px"
        ), unsafe_allow_html=True)

    with dcols[1]:
        st.markdown(card(
            f'<div style="color:{c["muted"]};font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">Dashboard 2</div>'
            f'<div style="color:{c["text"]};font-weight:700;font-size:14px;margin-bottom:4px;">📍 District Intelligence</div>'
            f'<div style="color:{c["text3"]};font-size:12px;line-height:1.6;margin-bottom:10px;">BO gap analysis · district heatmap · tier filters · actionable rankings</div>'
            f'<a href="https://public.tableau.com/app/profile/vishwadesai.ds/viz/DistrictIntelligence/DistrictIntelligence" target="_blank" '
            f'style="background:{c["accent"]};color:#FFF8F0;padding:7px 16px;border-radius:8px;'
            f'font-size:12px;font-weight:700;text-decoration:none;display:inline-block;">View Dashboard →</a>',
            border_top=c["accent"], mb="12px"
        ), unsafe_allow_html=True)

    st.markdown(
        f'<div style="border-top:1px solid {c["border"]}33;margin-top:20px;padding:12px 0;text-align:center;">'
        f'<div style="color:{c["muted"]};font-size:11px;">PostBot · Group 10 · Great Lakes PGP · Sep 2025–Apr 2026 · Groq AI · CatBoost R²=0.9243</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def login_page():
    st.markdown('<div class="pb-page">', unsafe_allow_html=True)
    c = C()

    _, col, _ = st.columns([0.65, 1.7, 0.65])
    with col:
        st.markdown(
            f'<div style="text-align:center;padding-top:0px;margin-bottom:4px;">'
            f'<div style="width:52px;height:52px;border-radius:14px;background:{c["accent"]};'
            f'display:inline-flex;align-items:center;justify-content:center;margin-bottom:12px;">'
            f'<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#FFF8F0" stroke-width="2.5">'
            f'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 8l10 6 10-6"/></svg></div>'
            f'<div style="font-family:\'Playfair Display\',serif;color:{c["text"]};font-size:22px;font-weight:900;margin-bottom:3px;">PostBot</div>'
            f'<div style="color:{c["text3"]};font-size:12px;">India Post Intelligence Engine</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── Single card containing all login fields + actions ──
        st.markdown(
            f'<div style="padding-top:6px;">',
            unsafe_allow_html=True
        )
        oid = st.text_input("Officer ID", placeholder="e.g. IP2024KA001 or DEMO", key="login_id")
        pw  = st.text_input("Password",   placeholder="Your password", type="password", key="login_pw")
        st.markdown('<div style="height:2px;"></div>', unsafe_allow_html=True)

        if st.button("Log In", use_container_width=True, key="login_btn"):
            if not oid.strip() or not pw.strip():
                st.error("Please enter both Officer ID and Password.")
            else:
                officer = authenticate(oid.strip(), pw.strip())
                if officer:
                    st.session_state.update({"officer": officer, "page": "district",
                                             "chat": [], "district_info": None,
                                             "suggestion": None, "district_analysed": False})
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

        # Thin divider
        st.markdown(
            f'<hr style="border:none;border-top:1px solid {c["border"]}33;margin:8px 0 6px;">',
            unsafe_allow_html=True
        )

        if "show_demo" not in st.session_state:
            st.session_state.show_demo = False
        if st.button("Show Demo Credentials", key="toggle_demo", use_container_width=True):
            st.session_state.show_demo = not st.session_state.show_demo
        if st.session_state.show_demo:
            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
            for d in get_demo_credentials():
                a, b = st.columns([3, 2])
                with a:
                    st.markdown(f"""
                    <div style="
                        background:{c['accent']};
                        color:#FFF8F0;
                        border:2px solid {c['accent']};
                        border-radius:10px;
                        padding:14px 16px;
                        font-family:'DM Sans',sans-serif;
                        font-size:14px;
                        font-weight:600;
                        white-space:nowrap;
                        overflow:hidden;
                        text-overflow:ellipsis;
                    ">
                        {d['id']} &nbsp; / &nbsp; {d['pw']}
                    </div>
                    """, unsafe_allow_html=True)
                with b: st.markdown(
                    f"<span style='color:{c['text3']};font-size:11px;'>{d['name']}<br>{d['circle']}</span>",
                    unsafe_allow_html=True
                )

        # Thin divider
        st.markdown(
            f'<hr style="border:none;border-top:1px solid {c["border"]}33;margin:14px 0 10px;">',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="color:{c["text3"]};font-size:12px;margin-bottom:8px;text-align:center;">No account yet?</div>',
            unsafe_allow_html=True
        )
        if st.button("Create Account", key="goto_signup", use_container_width=True):
            st.session_state.page = "signup"; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)  # end card

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIGN UP
# ══════════════════════════════════════════════════════════════════════════════
SIGNUP_CSV = "signups.csv"

def save_signup(name, oid, circle, role, email):
    exists = os.path.exists(SIGNUP_CSV)
    with open(SIGNUP_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp","name","officer_id","circle","role","email"])
        if not exists: w.writeheader()
        w.writerow({"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "name": name, "officer_id": oid, "circle": circle, "role": role, "email": email})

def signup_page():
    st.markdown('<div class="pb-page">', unsafe_allow_html=True)
    c = C()

    _, col, _ = st.columns([0.65, 1.7, 0.65])
    with col:
        st.markdown(
            f'<div style="text-align:center;padding-top:0px;margin-bottom:4px;">'
            f'<div style="width:52px;height:52px;border-radius:14px;background:{c["accent"]};'
            f'display:inline-flex;align-items:center;justify-content:center;margin-bottom:12px;">'
            f'<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFF8F0" stroke-width="2.5">'
            f'<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div>'
            f'<div style="font-family:\'Playfair Display\',serif;color:{c["text"]};font-size:21px;font-weight:900;margin-bottom:3px;">Request Access</div>'
            f'<div style="color:{c["text3"]};font-size:12px;">Reviewed by Circle Admin in 2–3 working days</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── Single card: all fields + submit + divider + log in ──
        st.markdown(
            f'<div style="padding-top:6px;">',
            unsafe_allow_html=True
        )
        name   = st.text_input("Full Name",            placeholder="e.g. Ravi Kumar",         key="su_name")
        oid    = st.text_input("Requested Officer ID", placeholder="e.g. IP2024XX001",        key="su_id")
        circle = st.text_input("Circle / Region",      placeholder="e.g. Karnataka Circle",   key="su_circle")
        role   = st.text_input("Designation",          placeholder="e.g. Divisional Manager", key="su_role")
        email  = st.text_input("Official Email",       placeholder="name@indiapost.gov.in",   key="su_email")
        st.markdown('<div style="height:2px;"></div>', unsafe_allow_html=True)

        if st.button("Submit Request", use_container_width=True, key="signup_btn"):
            if not all([name.strip(), oid.strip(), circle.strip(), email.strip()]):
                st.error("Please fill in all required fields.")
            elif "@" not in email:
                st.warning("Please enter a valid email address.")
            else:
                try:
                    save_signup(name.strip(), oid.strip(), circle.strip(), role.strip(), email.strip())
                    st.success(f"Request submitted for **{name}** ({oid}). Reviewed in 2–3 working days.")
                    st.info("Tip: Use **DEMO** / **demo123** to explore right now.")
                except Exception as e:
                    st.error(f"Could not save: {e}")

        # Thin divider + log in link — all inside same card
        st.markdown(
            f'<hr style="border:none;border-top:1px solid {c["border"]}33;margin:14px 0 10px;">',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="color:{c["text3"]};font-size:12px;margin-bottom:8px;text-align:center;">Have an account?</div>',
            unsafe_allow_html=True
        )
        if st.button("Log In", key="su_login", use_container_width=True):
            st.session_state.page = "login"; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)  # end card

    st.markdown('</div>', unsafe_allow_html=True)




# ══════════════════════════════════════════════════════════════════════════════
# DISTRICT PICKER
# ══════════════════════════════════════════════════════════════════════════════
def district_page(df):
    st.markdown('<div class="pb-page">', unsafe_allow_html=True)
    c = C()
    o = st.session_state.officer

    st.markdown('<div>', unsafe_allow_html=True)

    initials = "".join([w[0].upper() for w in o["name"].split()][:2])
    st.markdown(card(
        f'<div style="display:flex;align-items:center;gap:10px;">'
        f'<div style="width:32px;height:32px;border-radius:50%;background:{c["accent"]};'
        f'display:flex;align-items:center;justify-content:center;'
        f'color:{c['bg']};font-weight:700;font-size:11px;flex-shrink:0;">{initials}</div>'
        f'<div>'
        f'<div style="color:{c["text"]};font-weight:700;font-size:14px;">Welcome, {o["name"]}</div>'
        f'<div style="color:{c["text3"]};font-size:11px;">{o["role"]} · {o.get("circle","All India")} · {o["id"]}</div>'
        f'</div></div>',
        border_left=c["accent"], pad="12px 16px", mb="16px"
    ), unsafe_allow_html=True)

    col_stats, col_sel = st.columns([1, 2])
    with col_stats:
        st.markdown(label("Overview"), unsafe_allow_html=True)
        for val, lbl in [("165,627","Total Post Offices"),("754","Districts"),("36","States & UTs"),("94.8%","National Avg")]:
            st.markdown(
                f'<div style="background:{c["card"]};border:1px solid {c["border"]}33;border-radius:8px;'
                f'padding:9px 12px;margin-bottom:5px;display:flex;justify-content:space-between;align-items:center;">'
                f'<span style="color:{c["text3"]};font-size:12px;">{lbl}</span>'
                f'<span style="color:{c["accent"]};font-family:\'Playfair Display\',serif;font-size:16px;font-weight:900;">{val}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    with col_sel:
        st.markdown(
            f'<div style="background:{c["card"]};border:1.5px solid {c["border"]}55;border-radius:10px;padding:18px;">'
            f'<div style="font-family:\'Playfair Display\',serif;color:{c["text"]};font-size:17px;font-weight:800;margin-bottom:4px;">Select District</div>',
            unsafe_allow_html=True
        )
        states = get_states(df)
        sel_st = st.selectbox("State / UT", ["— Choose a state —"] + [s.title() for s in states], key="ds_state")
        fetch_clicked = False
        sel_state = sel_dist = ""

        if sel_st != "— Choose a state —":
            sel_state = sel_st.upper()
            dists = get_districts(df, sel_state)
            sel_dt = st.selectbox(f"District ({len(dists)} available)",
                                  ["— Choose a district —"] + [d.title() for d in dists], key="ds_dist")
            if sel_dt != "— Choose a district —":
                sel_dist = sel_dt.upper()
                st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
                fetch_clicked = st.button("Analyse This District", use_container_width=True, key="ds_fetch")
        else:
            st.selectbox("District", ["— Select state first —"], disabled=True, key="ds_dist_off")
        st.markdown('</div>', unsafe_allow_html=True)

        if fetch_clicked and sel_state and sel_dist:
            info = get_district_info(df, sel_state, sel_dist)
            if info:
                sugg = calculate_suggestion(info['bo_count'], info['po_count'],
                                            info['ho_count'], info['district_delivery_rate'])
                st.session_state.district_info     = info
                st.session_state.suggestion        = sugg
                st.session_state.district_analysed = True
                st.session_state.chat = [{"role": "bot", "content": (
                    f"District loaded: **{info['district'].title()}, {info['statename'].title()}**\n\n"
                    f"Offices: {info['total_offices']} (BO: {info['bo_count']}, PO: {info['po_count']}, HO: {info['ho_count']})\n"
                    f"Delivery Rate: {info['district_delivery_rate']*100:.1f}%\n"
                    f"Tier: {get_tier(info['district_delivery_rate'])['label']}\n"
                    f"BO Ratio: {info['bo_ratio']*100:.1f}% (target: 85%)\n\nAsk me anything."
                )}]
                st.session_state.page = "chat"
                st.rerun()

    if st.session_state.district_analysed and st.session_state.district_info:
        d    = st.session_state.district_info
        tier = get_tier(d['district_delivery_rate'])
        rate = d['district_delivery_rate'] * 100
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        st.markdown(card(
            f'{label("Last Analysed")}'
            f'<div style="color:{c["text"]};font-weight:700;font-size:14px;">{d["district"].title()}, {d["statename"].title()}</div>'
            f'<div style="color:{tier["color"]};font-size:18px;font-weight:900;">{rate:.1f}% <span style="font-size:11px;font-weight:600;">{tier["label"]}</span></div>',
            border_left=tier["color"], pad="12px 16px", mb="8px"
        ), unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1:
            if st.button("Go to Chat", key="dist_back_chat", use_container_width=True):
                st.session_state.page = "chat"; st.rerun()
        with r2:
            if st.button("Go to Analysis", key="dist_back_an", use_container_width=True):
                st.session_state.page = "analysis"; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─── SEND BOT ─────────────────────────────────────────────────────────────────
POSTAL_KW = ["post","postal","delivery","district","office","branch","bo","po","ho",
             "tier","india","infrastructure","rate","recommend","improve","reach",
             "activate","ratio","add","simulation","catboost","model","circle","division"]

def is_postal(text):
    return any(k in text.lower() for k in POSTAL_KW)

def _send_bot(q):
    st.session_state.chat.append({"role": "user", "content": q})
    if not is_postal(q):
        st.session_state.chat.append({"role": "bot",
            "content": "I only help with India Post district analysis — delivery rates, branch offices, infrastructure gaps and tier performance."})
        st.rerun(); return
    with st.spinner("Thinking..."):
        reply = ask_postbot(q, st.session_state.officer, st.session_state.district_info,
                            st.session_state.suggestion, st.session_state.chat)
    if "quota" in reply.lower() or "rate_limit" in reply.lower():
        d = st.session_state.district_info; sugg = st.session_state.suggestion
        tier = get_tier(d['district_delivery_rate']); rp = round(d['district_delivery_rate']*100,1)
        reply = (f"**API limit reached.** Cached data:\n\n"
                 f"**{d['district'].title()}, {d['statename'].title()}**\n"
                 f"Rate: {rp}% — {tier['label']}\n"
                 f"BO: {d['bo_count']} | PO: {d['po_count']} | HO: {d['ho_count']}\n")
        if sugg and not sugg['already_top'] and sugg['next_tier']:
            reply += f"Add **{sugg['bo_to_add']} BOs** → **{round(sugg['expected_rate']*100,1)}%**\n"
        reply += "\n*Wait 60s and retry.*"
    st.session_state.chat.append({"role": "bot", "content": reply})
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# CHAT — Claude style
# ══════════════════════════════════════════════════════════════════════════════
def chat_page(df):
    st.markdown('<div class="pb-page">', unsafe_allow_html=True)
    c    = C()
    d    = st.session_state.district_info
    tier = get_tier(d['district_delivery_rate'])
    rp   = round(d['district_delivery_rate'] * 100, 1)
    dist_t = d['district'].title()

    # ── Context strip (unchanged layout) ─────────────────────────────────────
    st.markdown(
        f'<div style="background:{c["card"]};border-bottom:1px solid {c["border"]}33;'
        f'padding:8px 32px;display:flex;align-items:center;justify-content:space-between;">'
        f'<div><span style="color:{c["text"]};font-weight:700;font-size:13px;">'
        f'{d["district"].title()}, {d["statename"].title()}</span>'
        f'<span style="color:{c["muted"]};font-size:11px;margin-left:12px;">'
        f'BO: {d["bo_count"]} · PO: {d["po_count"]} · HO: {d["ho_count"]}</span></div>'
        f'<div style="color:{tier["color"]};font-family:\'Playfair Display\',serif;'
        f'font-size:17px;font-weight:900;">{rp}% '
        f'<span style="font-size:11px;font-weight:600;">{tier["label"]}</span></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Messages ──────────────────────────────────────────────────────────────
    st.markdown('<div style="padding:14px 5% 4px;">', unsafe_allow_html=True)
    for msg in st.session_state.chat:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="user-row"><div class="user-bubble">{msg["content"]}</div></div>',
                unsafe_allow_html=True)
        else:
            # Render avatar separately, then bot content in styled container
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:9px;margin:8px 0;">'
                f'<div class="bot-avatar">PB</div>'
                f'<div class="bot-bubble" style="flex:1;">',
                unsafe_allow_html=True)
            st.markdown(msg["content"].strip())
            st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Quick chips ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="
        text-align:left;
        margin: 6px 0 10px 4px;
        color:{c['muted']};
        font-size:12px;
        font-weight:700;
        letter-spacing:1.4px;
        text-transform:uppercase;
    ">
        Quick Questions
    </div>
    """, unsafe_allow_html=True)

    chip_q = None
    st.markdown('<div class="pb-chips">', unsafe_allow_html=True)
    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)
    with q1:
        if st.button("Add 30 BOs — new rate?", key="qc1", use_container_width=True):
            chip_q = f"If I add 30 Branch Offices to {dist_t}, what will the new delivery rate be?"
    with q2:
        if st.button("BOs needed for 95%?", key="qc2", use_container_width=True):
            chip_q = f"How many Branch Offices does {dist_t} need to reach 95% delivery rate?"
    with q3:
        if st.button("Activate inactive POs — impact?", key="qc3", use_container_width=True):
            chip_q = f"How much will the rate improve if all non-delivering Sub Post Offices in {dist_t} are activated?"
    with q4:
        if st.button(f"5-step plan for {dist_t}", key="qc4", use_container_width=True):
            chip_q = f"Give a detailed 5-step action plan to improve delivery rate in {dist_t} to the next tier."
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    if chip_q:
        _send_bot(chip_q)

    # ── Input bar ─────────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="padding:8px 10% 16px;border-top:1px solid {c["border"]}22;">',
        unsafe_allow_html=True)
    ci, cb = st.columns([8, 1])
    with ci:
        uq = st.text_input("msg", label_visibility="collapsed",
                           placeholder="Message PostBot...", key="chat_q")
    with cb:
        send = st.button("Send", use_container_width=True, key="chat_send")
    st.markdown('</div>', unsafe_allow_html=True)

    if send and uq.strip():
        _send_bot(uq.strip())

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def analysis_page():
    st.markdown('<div class="pb-page">', unsafe_allow_html=True)
    c    = C()
    d    = st.session_state.district_info
    sugg = st.session_state.suggestion
    tier = get_tier(d['district_delivery_rate'])
    rp   = round(d['district_delivery_rate'] * 100, 1)
    bop  = round(d['bo_ratio'] * 100, 1)

    st.markdown('<div>', unsafe_allow_html=True)

    # Header
    st.markdown(card(
        f'<div style="font-family:\'Playfair Display\',serif;color:{c["accent"]};font-size:18px;font-weight:800;">Full Analysis — {d["district"].title()}</div>'
        f'<div style="color:{c["text3"]};font-size:11px;margin-top:2px;">{d["statename"].title()} · {d["total_offices"]} offices · {tier["label"]}</div>',
        border_left=tier["color"], pad="12px 16px", mb="14px"
    ), unsafe_allow_html=True)

    # Counts
    st.markdown(label("Office Infrastructure"), unsafe_allow_html=True)
    bo_del = int(d['bo_count']*0.987); po_del = int(d['po_count']*0.762)
    po_no  = d['po_count'] - po_del;  ho_del = int(d['ho_count']*0.991)
    a1,a2,a3,a4 = st.columns(4)
    for col, lbl_t, val, sub in [
        (a1,"Branch Offices",  d['bo_count'],     f"{bo_del} delivering · 98.7%"),
        (a2,"Sub Post Offices",d['po_count'],      f"{po_no} NOT delivering"),
        (a3,"Head Offices",    d['ho_count'],      f"{ho_del} delivering · 99.1%"),
        (a4,"Total",           d['total_offices'], f"BO ratio: {bop}%"),
    ]:
        with col:
            st.markdown(card(
                f'{label(lbl_t)}{big_num(str(val), c["accent"])}'
                f'<div style="color:{c["text3"]};font-size:11px;">{sub}</div>',
                border_top=c["accent"], pad="13px", mb="10px"
            ), unsafe_allow_html=True)

    # Performance
    st.markdown(label("Performance"), unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        nat = 94.8; vs = round(rp-nat,1); sign = "+" if vs>=0 else ""
        nc = "#16a34a" if vs>=0 else "#c0392b"; ab = "Above" if vs>=0 else "Below"
        st.markdown(card(
            f'{label("Delivery Performance")}{big_num(str(rp)+"%", tier["color"])}'
            f'<div style="color:{tier["color"]};font-size:12px;font-weight:700;margin-bottom:3px;">{tier["label"]}</div>'
            f'<div style="color:{c["text3"]};font-size:11px;margin-bottom:6px;">{tier["description"]}</div>'
            f'<div style="background:{c["accent"]}12;border-radius:6px;padding:5px 9px;">'
            f'<span style="color:{c["text3"]};font-size:11px;">vs National avg ({nat}%): </span>'
            f'<span style="color:{nc};font-weight:700;font-size:12px;">{ab} ({sign}{vs}%)</span></div>',
            mb="10px"
        ), unsafe_allow_html=True)
    with b2:
        bns = max(0, int((0.85-d['bo_ratio'])*d['total_offices']))
        bc  = c['accent'] if d['bo_ratio']>=0.85 else c['muted']
        st.markdown(card(
            f'{label("BO Ratio — Top Predictor (r=+0.87)")}{big_num(str(bop)+"%", bc)}',
            mb="4px"
        ), unsafe_allow_html=True)
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'margin-bottom:6px;color:{c["text3"]};font-size:12px;font-weight:700;">'
            f'<span>Current: {bop}%</span><span>Target: 85%</span></div>',
            unsafe_allow_html=True)

        st.progress(min(1.0, d['bo_ratio']))
        dm = st.session_state.get("dark_mode", False)

        if d['bo_ratio'] >= 0.85:

            bg = '#16361F' if dm else '#DFF4E4'
            txt = '#7CFFA2' if dm else '#166534'
            brd = '#2D6A3D' if dm else '#A7D7B5'

            st.markdown(
                f"""
                <div style="
                    background:{bg};
                    color:{txt};
                    border:1px solid {brd};
                    border-radius:12px;
                    padding:14px 16px;
                    margin-top:10px;
                    font-size:15px;
                    font-weight:700;
                ">
                    BO ratio above 85% — strong infrastructure.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            bg = '#4A4300' if dm else '#F6F0B8'
            txt = '#FFF4A3' if dm else '#6B4F00'
            brd = '#7A6A00' if dm else '#E2D77A'

            st.markdown(
                f"""
                <div style="
                    background:{bg};
                    color:{txt};
                    border:1px solid {brd};
                    border-radius:12px;
                    padding:14px 16px;
                    margin-top:10px;
                    font-size:15px;
                    font-weight:700;
                ">
                    Need {bns} more Branch Offices to reach 85%.
                </div>
                """,
                unsafe_allow_html=True
            )

    # Recommendations
    st.markdown('<div style="height:2px;"></div>', unsafe_allow_html=True)
    st.markdown(label("AI Recommendations"), unsafe_allow_html=True)
    if sugg['already_top']:

        bg = '#12381D' if dm else '#DDF4E2'
        txt = '#59F08B' if dm else '#166534'
        brd = '#2D6A3D' if dm else '#A7D7B5'

        st.markdown(
            f"""
            <div style="
                background:{bg};
                color:{txt};
                border:1px solid {brd};
                border-radius:14px;
                padding:18px 20px;
                margin-top:6px;
                font-size:16px;
                font-weight:700;
                line-height:1.5;
            ">
                Top Tier! {d['district'].title()} is at High Performance ({rp}%).
                Maintain current quality.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        nt = sugg['next_tier']; er = round(sugg['expected_rate']*100,1); imp = sugg['improvement']
        st.info(f"**Target:** {tier['label']}  →  {nt['label']} tier")
        r1,r2,r3 = st.columns(3)
        for col, lt, val, sub in [
            (r1,"Branch Offices to Add",f"+{sugg['bo_to_add']}",f"Current {d['bo_count']} → New {sugg['new_bo']}"),
            (r2,"Expected New Rate",    f"{er}%",                f"Up from {rp}%"),
            (r3,"Improvement",          f"+{imp}%",              f"{tier['label']} → {nt['label']}"),
        ]:
            with col:
                st.markdown(card(
                    f'{label(lt)}{big_num(val, c["accent"])}'
                    f'<div style="color:{c["text3"]};font-size:11px;">{sub}</div>',
                    pad="14px", mb="10px", extra=f"border-color:{c['accent']}44;"
                ), unsafe_allow_html=True)

        ba1, mid, ba2 = st.columns([5,1,5])
        brc = round(d['bo_ratio']*100,1); bra = round(sugg.get('bo_ratio_after',0)*100,1)
        with ba1:
            st.markdown(card(
                f'<div style="color:{tier["color"]};font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">Current</div>'
                f'{big_num(str(rp)+"%", tier["color"])}'
                f'<div style="color:{c["text"]};font-size:12px;font-weight:700;margin-bottom:2px;">{tier["label"]}</div>'
                f'<div style="color:{c["text3"]};font-size:11px;">BO: {d["bo_count"]} · Ratio: {brc}%</div>',
                pad="16px"
            ), unsafe_allow_html=True)
        with mid:
            st.markdown(f'<div style="text-align:center;padding-top:50px;color:{c["accent"]};font-size:20px;font-weight:700;">→</div>', unsafe_allow_html=True)
        with ba2:
            st.markdown(card(
                f'<div style="color:{nt["color"]};font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">After +{sugg["bo_to_add"]} BOs</div>'
                f'{big_num(str(er)+"%", nt["color"])}'
                f'<div style="color:{c["text"]};font-size:12px;font-weight:700;margin-bottom:2px;">{nt["label"]}</div>'
                f'<div style="color:{c["text3"]};font-size:11px;">BO: {sugg["new_bo"]} · Ratio: {bra}%</div>',
                pad="16px"
            ), unsafe_allow_html=True)

        inactive = int(d['po_count']*0.238)
        st.markdown('<div style="height:2px;"></div>', unsafe_allow_html=True)
        st.info(f"**Quick Win:** ~**{inactive} Sub Post Offices** have no active delivery. Activating half improves rate without adding offices.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    init()
    inject_css()
    render_navbar()
    df   = load_district_data("district_aggregated.csv")
    page = st.session_state.page

    if page == "home":       home_page()
    elif page == "login":    login_page()
    elif page == "signup":   signup_page()
    elif page == "district":
        if not st.session_state.officer:
            st.session_state.page = "login"; st.rerun()
        district_page(df)
    elif page == "chat":
        if not st.session_state.district_info:
            st.session_state.page = "district"; st.rerun()
        chat_page(df)
    elif page == "analysis":
        if not st.session_state.district_info:
            st.session_state.page = "district"; st.rerun()
        analysis_page()
    else:
        st.session_state.page = "home"; st.rerun()

if __name__ == "__main__":
    main()
