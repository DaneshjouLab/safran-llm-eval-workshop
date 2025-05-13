#!/bin/bash

# ===============================
# Setup Script for Streamlit Evaluation App
# ===============================

# Set a name for the virtual environment
ENV_NAME="eval_env"

echo "🔧 Creating virtual environment: $ENV_NAME"
python3 -m venv $ENV_NAME

echo "✅ Virtual environment created."

# Activate the virtual environment
source $ENV_NAME/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install streamlit pandas openpyxl

echo "✅ Dependencies installed."

echo "🚀 Launching Streamlit App..."
streamlit run eval_app.py

# Deactivate after exit
deactivate
