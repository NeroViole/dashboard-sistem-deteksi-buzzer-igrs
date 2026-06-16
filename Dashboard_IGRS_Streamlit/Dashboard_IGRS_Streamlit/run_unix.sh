#!/usr/bin/env bash
# Jalankan dashboard IGRS (macOS / Linux)
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
