import streamlit as st
import pandas as pd


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Safety Data Analyst",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# SETTINGS
# ============================================================

REQUIRED_COLUMNS = [
    "id",
    "classification",
    "confidence",
    "human_review",
    "severity"
]


SEVERITY_WEIGHTS = {
    "low": 0.25,
    "medium": 0.50,
    "high": 0.75,
    "critical": 1.00
}


# ============================================================
# FUNCTIONS
# ============================================================

def calculate_priority(df):

    result = df.copy()

    result["confidence"] = pd.to_numeric(
        result["confidence"]
    )

    result["severity_normalized"] = (
        result["severity"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    result["severity_score"] = (
        result["severity_normalized"]
        .map(SEVERITY_WEIGHTS)
    )

    # Confidence of 100 = no uncertainty
    # Confidence of 0 = maximum uncertainty
    result["uncertainty_score"] = (
        1 - result["confidence"] / 100
    )

    # Priority combines potential impact and uncertainty.
    result["priority_score"] = (
        0.60 * result["severity_score"]
        +
        0.40 * result["uncertainty_score"]
    )

    result["priority_score"] = (
        result["priority_score"] * 100
    ).round(1)

    return result


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ AI Safety Data Analyst")

st.caption(
    "Human-in-the-loop analytics and prioritization "
    "for AI safety datasets."
)

st.divider()


# ============================================================
# FILE UPLOAD
# ============================================================

st.subheader("📁 Dataset")

uploaded_file = st.file_uploader(
    "Upload a CSV dataset",
    type=["csv"]
)


# ============================================================
# LOAD DATA
# ============================================================

if uploaded_file is not None:

    try:

        df = pd.read_csv(uploaded_file)

        st.success(
            f"Successfully loaded {len(df):,} records."
        )

    except Exception as e:

        st.error(
            f"Could not read the CSV file: {e}"
        )

        st.stop()

else:

    try:

        df = pd.read_csv(
            "safety_dataset_priority.csv"
        )

        st.info(
            "Using the upgraded demonstration dataset."
        )

    except Exception as e:

        st.error(
            f"Could not load the demonstration dataset: {e}"
        )

        st.stop()


# ============================================================
# DATASET VALIDATION
# ============================================================

st.subheader("🔎 Dataset Validation")

validation_errors = []


# Empty dataset
if df.empty:

    validation_errors.append(
        "The dataset is empty. Please upload a CSV containing at least one record."
    )


# Required columns
missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if missing_columns:

    validation_errors.append(
        "Missing required column(s): "
        + ", ".join(missing_columns)
    )


# Confidence validation
if "confidence" in df.columns:

    confidence_numeric = pd.to_numeric(
        df["confidence"],
        errors="coerce"
    )

    if confidence_numeric.isna().any():

        validation_errors.append(
            "The confidence column contains "
            "non-numeric or missing values."
        )

    elif (
        (confidence_numeric < 0).any()
        or
        (confidence_numeric > 100).any()
    ):

        validation_errors.append(
            "Confidence values must be between 0 and 100."
        )


# ID validation
if "id" in df.columns and not df.empty:

    if df["id"].isna().any():

        validation_errors.append(
            "The id column contains missing values."
        )

    if df["id"].duplicated().any():

        validation_errors.append(
            "The id column contains duplicate IDs."
        )


# Severity validation
if "severity" in df.columns and not df.empty:

    valid_severities = set(
        SEVERITY_WEIGHTS.keys()
    )

    actual_severities = set(
        df["severity"]
        .astype(str)
        .str.strip()
        .str.lower()
        .unique()
    )

    invalid_severities = (
        actual_severities - valid_severities
    )

    if invalid_severities:

        validation_errors.append(
            "Invalid severity value(s): "
            + ", ".join(sorted(invalid_severities))
            + ". Use Low, Medium, High, or Critical."
        )


# Classification validation
if "classification" in df.columns and not df.empty:

    if df["classification"].isna().any():

        validation_errors.append(
            "The classification column contains missing values."
        )


# ============================================================
# VALIDATION RESULTS
# ============================================================

if validation_errors:

    st.error("Dataset validation failed.")

    for error in validation_errors:

        st.write(
            f"❌ {error}"
        )

    st.info(
        "Please fix the dataset and upload it again."
    )

    st.stop()


st.success(
    "Dataset passed validation."
)


# ============================================================
# DATA PREPARATION
# ============================================================

df["confidence"] = pd.to_numeric(
    df["confidence"]
)


# Calculate priority
df = calculate_priority(df)


# ============================================================
# DATASET QUALITY AUDIT
# ============================================================

st.subheader("🔍 Dataset Quality Audit")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Rows",
        len(df)
    )

with col2:

    st.metric(
        "Columns",
        len(df.columns)
    )

with col3:

    st.metric(
        "Missing Values",
        int(df.isna().sum().sum())
    )

with col4:

    st.metric(
        "Duplicate Rows",
        int(df.duplicated().sum())
    )


# ============================================================
# DATASET PREVIEW
# ============================================================

st.subheader("📊 Dataset Preview")

st.dataframe(
    df,
    use_container_width=True
)


# ============================================================
# REVIEW BUDGET
# ============================================================

st.subheader("👤 Reviewer Capacity")

max_budget = min(
    20,
    len(df)
)

review_budget = st.slider(
    "How many items can the reviewer inspect?",
    min_value=1,
    max_value=max_budget,
    value=max_budget
)


# ============================================================
# PRIORITY QUEUE
# ============================================================

review_queue = (
    df.sort_values(
        "priority_score",
        ascending=False
    )
    .head(review_budget)
    .copy()
)


# ============================================================
# SAFETY ANALYTICS
# ============================================================

st.subheader("🛡️ Safety Analytics")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Items",
        len(df)
    )

with col2:

    st.metric(
        "Average Confidence",
        f"{df['confidence'].mean():.1f}%"
    )

with col3:

    st.metric(
        "Review Budget",
        review_budget
    )

with col4:

    st.metric(
        "Queue Coverage",
        f"{review_budget / len(df) * 100:.1f}%"
    )


st.caption(
    "The review queue is now ranked by priority rather than "
    "using a simple confidence cutoff."
)


# ============================================================
# PRIORITY EXPLANATION
# ============================================================

st.subheader("📐 Priority Scoring")

st.write(
    "**Priority Score = 60% Severity + 40% Uncertainty**"
)

st.write(
    "Severity represents the potential impact of a harmful "
    "classification decision. Uncertainty is calculated as "
    "1 − confidence."
)

st.write(
    "This is a transparent demonstration policy. "
    "The severity mapping is synthetic and does not represent "
    "Meta's internal safety policy."
)


# ============================================================
# REVIEW QUEUE
# ============================================================

st.subheader("🚨 Prioritized Human Review Queue")

st.write(
    f"The reviewer has capacity to inspect "
    f"**{review_budget} item(s)**."
)

st.dataframe(
    review_queue[
        [
            "id",
            "classification",
            "severity",
            "confidence",
            "uncertainty_score",
            "priority_score",
            "human_review"
        ]
    ],
    use_container_width=True
)


# ============================================================
# HIGH-SEVERITY CASES
# ============================================================

st.subheader("⚠️ High-Impact Cases")

high_impact = df[
    df["severity"]
    .astype(str)
    .str.lower()
    .isin(["high", "critical"])
].sort_values(
    "priority_score",
    ascending=False
)

st.dataframe(
    high_impact[
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
# CATEGORY ANALYSIS
# ============================================================

st.subheader("📂 Category Analysis")

category_analysis = (
    df.groupby("classification")
    .agg(
        items=("id", "count"),
        average_confidence=("confidence", "mean"),
        average_priority=("priority_score", "mean")
    )
    .reset_index()
)

category_analysis[
    "average_confidence"
] = category_analysis[
    "average_confidence"
].round(1)

category_analysis[
    "average_priority"
] = category_analysis[
    "average_priority"
].round(1)

category_analysis = category_analysis.sort_values(
    "average_priority",
    ascending=False
)

st.dataframe(
    category_analysis,
    use_container_width=True
)


# ============================================================
# CONFIDENCE CHART
# ============================================================

st.subheader("📈 Confidence Distribution")

st.bar_chart(
    df.set_index("id")["confidence"]
)


# ============================================================
# AUTOMATED FINDINGS
# ============================================================

st.subheader("🤖 Automated Findings")

highest_priority_item = review_queue.iloc[0]

st.write(
    f"**Highest-priority item:** "
    f"ID {highest_priority_item['id']} "
    f"({highest_priority_item['classification']}) "
    f"with a priority score of "
    f"{highest_priority_item['priority_score']:.1f}."
)

st.write(
    f"**Severity:** "
    f"{highest_priority_item['severity']}"
)

st.write(
    f"**Model confidence:** "
    f"{highest_priority_item['confidence']:.0f}%"
)

st.write(
    "**Recommendation:** "
    "Review the highest-priority cases first because they "
    "combine potential impact with model uncertainty."
)


# ============================================================
# CONTENT EXPLORER
# ============================================================

st.subheader("🔎 Content Explorer")

selected_id = st.selectbox(
    "Select an item:",
    df["id"].tolist()
)

selected_item = df[
    df["id"] == selected_id
].iloc[0]


st.write(
    f"**Classification:** "
    f"{selected_item['classification']}"
)

st.write(
    f"**Severity:** "
    f"{selected_item['severity']}"
)

st.write(
    f"**Confidence:** "
    f"{selected_item['confidence']:.0f}%"
)

st.write(
    f"**Priority Score:** "
    f"{selected_item['priority_score']:.1f}"
)

st.write(
    f"**Existing Human Review Flag:** "
    f"{selected_item['human_review']}"
)

if "content" in df.columns:

    st.write("**Content:**")

    st.write(
        selected_item["content"]
    )


# ============================================================
# EXPORT
# ============================================================

st.subheader("📤 Export Analysis")

csv_export = review_queue.to_csv(
    index=False
)

st.download_button(
    label="Download Prioritized Review Queue",
    data=csv_export,
    file_name="prioritized_review_queue.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Safety Data Analyst — Prototype"
)
