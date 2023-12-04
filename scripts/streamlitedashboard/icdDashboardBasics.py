"""
# My first app
Here's our first attempt at using data to create a table:
"""

# streamlit run ./scripts/streamlitedashboard/icdDashboardBasics.py

import streamlit as st
import pandas as pd

df = pd.read_csv('C:/Users/pauloricardolb/OneDrive - Universidade de Aveiro/TRABALHO_AULAS/AL20232024/ICD/projICD/data/interim/df_results_list_records.csv')

df