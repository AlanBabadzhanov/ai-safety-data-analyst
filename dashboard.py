
import streamlit as st
import pandas as pd
from pathlib import Path

from evaluation import (
    load_data,
    calculate_priority,
    evaluate_methods,
    analyze_weights
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Safety Data Analyst",
    page_icon="🛡️",
    layout="wide"
)

DATA_FILE = "safety_dataset_priority.csv"
DECISIONS_FILE = Path("reviewer_decisions.csv")

st.title("🛡️ AI Safety Data Analyst")

st.caption(
    "Human-in-the-loop safety prioritization, "
    "evaluation, and reviewer workflow."
)

# ============================================================
# LOAD DATA
# ============================================================

try:

    df = load_data(DATA_FILE)

except Exception as e:

    st.error(f"Dataset error: {e}")
    st.stop()

# ============================================================
# SIDEBAR SETTINGS
# ============================================================

st.sidebar.header("Review Settings")

budget = st.sidebar.slider(
    "Reviewer Capacity",
    min_value=1,
    max_value=len(df),
    value=min(20, len(df))
)

severity_weight = st.sidebar.slider(
    "Severity Weight",
    min_value=0.0,
    max_value=1.0,
    value=0.60,
    step=0.05
)

uncertainty_weight = 1 - severity_weight

st.sidebar.write(
    f"Uncertainty Weight: {uncertainty_weight:.0%}"
)

# ============================================================
# CALCULATE PRIORITY
# ============================================================

df = calculate_priority(
    df,
    severity_weight
)

# ============================================================
# LOAD REVIEWER DECISIONS
# ============================================================

def load_decisions():

    if DECISIONS_FILE.exists():

        decisions = pd.read_csv(
            DECISIONS_FILE,
            dtype={"id": str}
        )

        return decisions

    return pd.DataFrame(
        columns=[
            "id",
            "decision",
            "resolved",
            "notes"
        ]
    )


decisions = load_decisions()

# ============================================================
# RESOLVED CASES
# ============================================================

if not decisions.empty:

    resolved_ids = set(
        decisions.loc[
            decisions["resolved"]
            .astype(str)
            .str.lower()
            .eq("true"),
            "id"
        ].astype(str)
    )

else:

    resolved_ids = set()

pending = df[
    ~df["id"].astype(str).isin(resolved_ids)
]

# ============================================================
# DATASET OVERVIEW
# ============================================================

st.divider()

st.subheader("📊 Dataset Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Cases",
    len(df)
)

c2.metric(
    "Average Confidence",
    f"{df['confidence'].mean():.1f}%"
)

c3.metric(
    "Review Budget",
    budget
)

c4.metric(
    "Resolved Cases",
    len(resolved_ids)
)

# ============================================================
# PRIORITY SCORING
# ============================================================

st.divider()

st.subheader("⚖️ Priority Scoring")

st.write(
    f"**Priority Score = "
    f"{severity_weight:.0%} Severity + "
    f"{uncertainty_weight:.0%} Uncertainty**"
)

st.write(
    "Severity represents potential impact. "
    "Uncertainty is calculated as 1 minus confidence."
)

st.caption(
    "The severity mapping is a demonstration policy "
    "and does not represent Meta's internal safety policy."
)

# ============================================================
# PRIORITIZED QUEUE
# ============================================================

st.divider()

st.subheader("🚨 Prioritized Human Review Queue")

queue = pending.sort_values(
    "priority_score",
    ascending=False
).head(budget)

st.write(
    f"Showing {len(queue)} unresolved cases "
    f"within the review budget."
)

st.dataframe(
    queue[
        [
            "id",
            "classification",
            "severity",
            "confidence",
            "priority_score"
        ]
    ],
    use_container_width=True
)

# ============================================================
# RANKING EVALUATION
# ============================================================

st.divider()

st.subheader("📈 Ranking Strategy Evaluation")

st.write(
    "Comparison of four ranking approaches "
    "using the same review budget."
)

comparison = evaluate_methods(
    df,
    budget=budget
)

st.dataframe(
    comparison,
    use_container_width=True
)

st.bar_chart(
    comparison.set_index("method")[
        "average_youth_safety"
    ]
)

st.info(
    "Youth Safety representation and legacy review flags "
    "are descriptive metrics. They do not establish "
    "which method identifies more actionable cases."
)

# ============================================================
# WEIGHT SENSITIVITY
# ============================================================

st.divider()

st.subheader("⚖️ Weight Sensitivity Analysis")

sensitivity = analyze_weights(
    df,
    budget=budget
)

st.dataframe(
    sensitivity,
    use_container_width=True
)

st.line_chart(
    sensitivity.set_index("severity_weight")[
        "youth_safety_cases"
    ]
)

# ============================================================
# REVIEWER WORKFLOW
# ============================================================

st.divider()

st.subheader("👤 Human Reviewer Workflow")

if queue.empty:

    st.success(
        "No unresolved cases currently in the queue."
    )

else:

    selected_id = st.selectbox(
        "Select a case to review:",
        queue["id"].tolist()
    )

    selected = queue[
        queue["id"] == selected_id
    ].iloc[0]

    st.write(
        f"**Classification:** {selected['classification']}"
    )

    st.write(
        f"**Severity:** {selected['severity']}"
    )

    st.write(
        f"**Confidence:** {selected['confidence']}%"
    )

    st.write(
        f"**Priority Score:** {selected['priority_score']}"
    )

    if "content" in df.columns:

        st.write("**Content:**")
        st.write(selected["content"])

    decision = st.selectbox(
        "Reviewer Decision:",
        [
            "Needs Action",
            "No Action Needed",
            "Escalate",
            "Uncertain"
        ]
    )

    notes = st.text_area(
        "Reviewer Notes:"
    )

    resolved = st.checkbox(
        "Mark this case as resolved"
    )

    if st.button(
        "Save Review Decision",
        type="primary"
    ):

        new_record = pd.DataFrame([{
            "id": str(selected_id),
            "decision": decision,
            "resolved": resolved,
            "notes": notes
        }])

        updated = decisions[
            decisions["id"].astype(str)
            != str(selected_id)
        ]

        updated = pd.concat(
            [updated, new_record],
            ignore_index=True
        )

        updated.to_csv(
            DECISIONS_FILE,
            index=False
        )

        st.success(
            "Reviewer decision saved successfully."
        )

        st.rerun()

# ============================================================
# REVIEW HISTORY
# ============================================================

st.divider()

st.subheader("📋 Review History")

if not decisions.empty:

    st.dataframe(
        decisions,
        use_container_width=True
    )

    st.download_button(
        "Download Reviewer Decisions",
        decisions.to_csv(index=False),
        "reviewer_decisions.csv",
        "text/csv"
    )

else:

    st.info(
        "No reviewer decisions have been recorded yet."
    )

# ============================================================
# EXPORT
# ============================================================

st.divider()

st.subheader("📤 Export Prioritized Queue")

st.download_button(
    "Download Priority Queue",
    queue.to_csv(index=False),
    "priority_queue.csv",
    "text/csv"
)

st.caption(
    "AI Safety Data Analyst | Research Prototype"
)
