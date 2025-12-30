# import sqlite3
# import streamlit as st

# DB_PATH = "database.db"

# @st.cache_resource
# def get_conn():
#     conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#     conn.row_factory = sqlite3.Row
#     return conn


import sqlite3
import os

DB_PATH = "Database.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
