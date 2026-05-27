"""
auth.py — India Post Officer Login System
Secure version using Streamlit Secrets
"""

import hashlib
import streamlit as st


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# ── Passwords from Streamlit Secrets ─────────────────────────────────────────
PASSWORDS = st.secrets["credentials"]


# ── Officer Database (NON-SENSITIVE DATA ONLY) ──────────────────────────────
OFFICERS = {

    "IP2026KA101": {
        "name":   "Anil Verma",
        "circle": "Karnataka",
        "role":   "Divisional Manager",
        "email":  "anil.verma@indiapost.gov.in",
    },

    "IP2026MH102": {
        "name":   "Sneha Patil",
        "circle": "Maharashtra",
        "role":   "Postmaster General",
        "email":  "sneha.patil@indiapost.gov.in",
    },

    "IP2026TN103": {
        "name":   "Karthik Raman",
        "circle": "Tamil Nadu",
        "role":   "Assistant Superintendent",
        "email":  "karthik.raman@indiapost.gov.in",
    },

    "IP2026UP104": {
        "name":   "Vikram Yadav",
        "circle": "Uttar Pradesh",
        "role":   "Inspector of Posts",
        "email":  "vikram.yadav@indiapost.gov.in",
    },

    "IP2026GJ105": {
        "name":   "Mehul Trivedi",
        "circle": "Gujarat",
        "role":   "Senior Postmaster",
        "email":  "mehul.trivedi@indiapost.gov.in",
    },

    "IP2026RJ106": {
        "name":   "Deepak Chouhan",
        "circle": "Rajasthan",
        "role":   "Regional Manager",
        "email":  "deepak.chouhan@indiapost.gov.in",
    },

    "IP2026DL107": {
        "name":   "Pooja Malhotra",
        "circle": "Delhi",
        "role":   "Operations Head",
        "email":  "pooja.malhotra@indiapost.gov.in",
    },

    "DEMO2026": {
        "name":   "Testing Officer",
        "circle": "All India",
        "role":   "System Analyst",
        "email":  "testing.officer@indiapost.gov.in",
    },
}


def authenticate(officer_id: str, password: str):
    """
    Returns officer dict if credentials are valid, else None.
    """

    officer_id = officer_id.strip().upper()

    officer = OFFICERS.get(officer_id)

    if not officer:
        return None

    stored_password = PASSWORDS.get(officer_id)

    if stored_password and _hash(stored_password) == _hash(password):

        return {
            "id":     officer_id,
            "name":   officer["name"],
            "circle": officer["circle"],
            "role":   officer["role"],
            "email":  officer["email"],
        }

    return None


def get_demo_credentials():
    """Return list of demo credentials for display on login page."""

    return [

        {
            "id": "IP2026KA101",
            "pw": PASSWORDS["IP2026KA101"],
            "name": "Anil Verma",
            "circle": "Karnataka",
        },

        {
            "id": "IP2026MH102",
            "pw": PASSWORDS["IP2026MH102"],
            "name": "Sneha Patil",
            "circle": "Maharashtra",
        },

        {
            "id": "IP2026TN103",
            "pw": PASSWORDS["IP2026TN103"],
            "name": "Karthik Raman",
            "circle": "Tamil Nadu",
        },

        {
            "id": "IP2026DL107",
            "pw": PASSWORDS["IP2026DL107"],
            "name": "Pooja Malhotra",
            "circle": "Delhi",
        },

        {
            "id": "DEMO2026",
            "pw": PASSWORDS["DEMO2026"],
            "name": "Testing Officer",
            "circle": "All India",
        },
    ]