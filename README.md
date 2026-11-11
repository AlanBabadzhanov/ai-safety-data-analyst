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
{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 \
# AI Safety Data Analyst\
\
A human-in-the-loop AI safety analytics prototype designed to prioritize content for review based on severity and model uncertainty.\
\
## Project Overview\
\
This project explores how data-driven prioritization can help reviewers identify potentially high-impact safety cases within limited review capacity.\
\
## Features\
\
- Dataset validation and quality auditing\
- Severity and uncertainty-based prioritization\
- Adjustable scoring weights\
- Random, confidence-only, severity-only, and combined ranking comparisons\
- Weight sensitivity analysis\
- Interactive Streamlit dashboard\
- Human reviewer decision workflow\
- Local reviewer decision history\
- Command-line analyst agent\
\
## Prioritization Methodology\
\
Priority Score = (Severity Weight \'d7 Severity Score + Uncertainty Weight \'d7 Uncertainty Score) \'d7 100\
\
Default configuration:\
- Severity: 60%\
- Uncertainty: 40%\
\
Uncertainty is calculated as 1 minus model confidence.\
\
## Evaluation\
\
The evaluation compares four ranking strategies using the same review budget.\
\
Independent human-reviewed outcomes are needed to establish actionable-case recall and determine whether the combined approach improves performance.\
\
## Installation\
\
Clone the repository:\
\
```bash\
git clone https://github.com/AlanBabadzhanov/ai-safety-data-analyst.git\
cd ai-safety-data-analyst\
```\
\
Install dependencies:\
\
```bash\
pip install -r requirements.txt\
```\
\
## Run the Evaluation\
\
```bash\
python3 evaluation.py\
```\
\
## Launch the Dashboard\
\
```bash\
python3 -m streamlit run dashboard.py\
```\
\
## Run the Analyst Agent\
\
```bash\
python3 agent.py\
```\
\
## Project Structure\
\
- dashboard.py: Interactive dashboard\
- evaluation.py: Shared scoring and evaluation functions\
- agent.py: Command-line analyst\
- requirements.txt: Python dependencies\
\
## Limitations\
\
This is a research prototype using demonstration data and synthetic severity mappings. It does not represent any company's internal safety policies.\
\
Independent reviewer outcomes are necessary to validate actual prioritization performance.\
\
Reviewer decisions are stored locally in CSV format.\
}
