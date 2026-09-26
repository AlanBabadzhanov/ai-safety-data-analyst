# 🛡️ AI Safety Data Analyst

An agentic data analytics prototype designed to analyze AI safety datasets, identify uncertainty, audit data quality, and prioritize cases for human review.

## 🚀 Overview

AI systems often operate on large datasets where classification confidence and data quality can vary significantly.

This project explores a human-in-the-loop approach:

**Dataset → Agent → Analysis → Risk Signals → Human Review**

Rather than treating model outputs as automatically correct, the system identifies uncertain cases and surfaces them for additional investigation.

## ✨ Features

### 📊 Dataset Analytics
- Dataset size and structure
- Average model confidence
- Classification breakdown
- Human-review rate

### 🔍 Data Quality Audit
- Missing-value detection
- Duplicate-row detection
- Dataset preview
- Schema validation

### ⚠️ Human Review Prioritization
Automatically identifies low-confidence cases and creates a review queue.

### 📈 Category Analysis
Compares confidence and review activity across classification categories.

### 🔎 Content Explorer
Allows individual records to be inspected directly from the dashboard.

### 📥 Export
Human-review queues can be exported as CSV for further investigation.

## 🧠 Agent Architecture

The project is designed around an agent-style workflow in which different analytical tools can be selected based on the user's request.

```text
                    USER
                     │
                     ▼
              ┌─────────────┐
              │ AI ANALYST  │
              └──────┬──────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       REVIEW      RISK      CATEGORY
       ANALYSIS   ANALYSIS    ANALYSIS
          │          │          │
          └──────────┼──────────┘
                     ▼
                DATASET
                     │
                     ▼
              ANALYTICAL
                OUTPUT
                     │
                     ▼
              HUMAN REVIEW


## ▶️ Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/AlanBabadzhanov/ai-safety-data-analyst.git
cd ai-safety-data-analyst

Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

Install dependencies
pip install pandas streamlit openai

Launch the dashboard
streamlit run dashboard.py

The application will open at:

http://localhost:8501
