
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# SETTINGS
# ============================================================

SEVERITY_WEIGHTS = {
    "low": 0.25,
    "medium": 0.50,
    "high": 0.75,
    "critical": 1.00
}

DEFAULT_SEVERITY_WEIGHT = 0.60
RANDOM_TRIALS = 1000


# ============================================================
# LOAD AND VALIDATE DATA
# ============================================================

def load_data(file_path="safety_dataset_priority.csv"):

    df = pd.read_csv(
        file_path,
        encoding="utf-8-sig"
    )

    required = [
        "id",
        "classification",
        "confidence",
        "severity"
    ]

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    if df.empty:
        raise ValueError("Dataset is empty.")

    if df["id"].isna().any():
        raise ValueError("Missing IDs found.")

    if df["id"].duplicated().any():
        raise ValueError("Duplicate IDs found.")

    df["confidence"] = pd.to_numeric(
        df["confidence"],
        errors="coerce"
    )

    if df["confidence"].isna().any():
        raise ValueError("Invalid confidence values.")

    if not df["confidence"].between(0, 100).all():
        raise ValueError(
            "Confidence must be between 0 and 100."
        )

    df["severity_normalized"] = (
        df["severity"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    invalid = (
        set(df["severity_normalized"].unique())
        - set(SEVERITY_WEIGHTS.keys())
    )

    if invalid:
        raise ValueError(
            f"Invalid severity values: {invalid}"
        )

    df["severity_score"] = (
        df["severity_normalized"]
        .map(SEVERITY_WEIGHTS)
    )

    df["uncertainty_score"] = (
        1 - df["confidence"] / 100
    )

    return df


# ============================================================
# PRIORITY CALCULATION
# ============================================================

def calculate_priority(
    df,
    severity_weight=DEFAULT_SEVERITY_WEIGHT
):

    if not 0 <= severity_weight <= 1:
        raise ValueError(
            "Severity weight must be between 0 and 1."
        )

    result = df.copy()

    uncertainty_weight = 1 - severity_weight

    result["priority_score"] = (
        severity_weight * result["severity_score"]
        +
        uncertainty_weight * result["uncertainty_score"]
    ) * 100

    result["priority_score"] = (
        result["priority_score"].round(1)
    )

    return result


# ============================================================
# RANKING METHODS
# ============================================================

def rank_items(
    df,
    method,
    severity_weight=DEFAULT_SEVERITY_WEIGHT,
    random_seed=42
):

    if method == "combined":

        ranked = calculate_priority(
            df,
            severity_weight
        )

        return ranked.sort_values(
            "priority_score",
            ascending=False
        )

    elif method == "severity":

        return df.sort_values(
            "severity_score",
            ascending=False
        )

    elif method == "confidence":

        return df.sort_values(
            "confidence",
            ascending=True
        )

    elif method == "random":

        return df.sample(
            frac=1,
            random_state=random_seed
        )

    else:
        raise ValueError(
            f"Unknown ranking method: {method}"
        )


# ============================================================
# LEGACY REVIEW FLAGS
# ============================================================

def count_legacy_reviews(df):

    if "human_review" not in df.columns:
        return None

    flags = (
        df["human_review"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return int(
        flags.isin(["YES", "TRUE", "1"]).sum()
    )


# ============================================================
# INDEPENDENT REVIEW OUTCOMES
# ============================================================

def convert_outcomes(series):

    mapping = {
        "1": 1,
        "true": 1,
        "yes": 1,
        "actionable": 1,
        "0": 0,
        "false": 0,
        "no": 0,
        "not actionable": 0,
        "not_actionable": 0
    }

    values = (
        series.astype(str)
        .str.strip()
        .str.lower()
    )

    converted = values.map(mapping)

    if converted.isna().any():
        raise ValueError(
            "Outcome values must be binary."
        )

    return converted.astype(int)


# ============================================================
# EVALUATE RANKING METHODS
# ============================================================

def evaluate_methods(
    df,
    budget=20,
    random_trials=RANDOM_TRIALS,
    outcome_column=None
):

    methods = [
        "random",
        "confidence",
        "severity",
        "combined"
    ]

    results = []

    if outcome_column:

        if outcome_column not in df.columns:
            raise ValueError(
                f"Missing outcome column: {outcome_column}"
            )

        outcomes = convert_outcomes(
            df[outcome_column]
        )

        outcome_lookup = dict(
            zip(df["id"], outcomes)
        )

    else:
        outcome_lookup = None

    actual_budget = min(budget, len(df))

    for method in methods:

        trials = (
            random_trials
            if method == "random"
            else 1
        )

        youth_counts = []
        legacy_counts = []
        actionable_counts = []

        for trial in range(trials):

            ranked = rank_items(
                df,
                method,
                random_seed=42 + trial
            )

            top_items = ranked.head(actual_budget)

            youth_count = (
                top_items["classification"]
                .eq("Youth Safety")
                .sum()
            )

            youth_counts.append(youth_count)

            legacy_count = count_legacy_reviews(
                top_items
            )

            if legacy_count is not None:
                legacy_counts.append(legacy_count)

            if outcome_lookup is not None:

                actionable_count = sum(
                    outcome_lookup[item_id]
                    for item_id in top_items["id"]
                )

                actionable_counts.append(
                    actionable_count
                )

        result = {
            "method": method,
            "review_budget": actual_budget,
            "average_youth_safety": round(
                np.mean(youth_counts), 2
            ),
            "legacy_review_flags": (
                round(np.mean(legacy_counts), 2)
                if legacy_counts else None
            )
        }

        if method == "random":

            result["random_min"] = min(youth_counts)
            result["random_max"] = max(youth_counts)

        if actionable_counts:

            result["actionable_cases"] = (
                actionable_counts[0]
            )

            result["actionable_rate"] = round(
                actionable_counts[0]
                / actual_budget * 100,
                2
            )

        results.append(result)

    return pd.DataFrame(results)


# ============================================================
# WEIGHT SENSITIVITY
# ============================================================

def analyze_weights(df, budget=20):

    weights = [
        0.00,
        0.20,
        0.40,
        0.50,
        0.60,
        0.80,
        1.00
    ]

    results = []

    for weight in weights:

        ranked = rank_items(
            df,
            "combined",
            severity_weight=weight
        )

        top_items = ranked.head(budget)

        results.append({

            "severity_weight": weight * 100,

            "uncertainty_weight": (
                1 - weight
            ) * 100,

            "youth_safety_cases": (
                top_items["classification"]
                .eq("Youth Safety")
                .sum()
            ),

            "high_critical_cases": (
                top_items["severity_normalized"]
                .isin(["high", "critical"])
                .sum()
            ),

            "legacy_review_flags": (
                count_legacy_reviews(top_items)
            )
        })

    return pd.DataFrame(results)


# ============================================================
# RUN EVALUATION
# ============================================================

def run_evaluation(
    file_path="safety_dataset_priority.csv",
    budget=20
):

    print("\n" + "=" * 60)
    print("AI SAFETY DATA ANALYST - EVALUATION")
    print("=" * 60)

    df = load_data(file_path)

    print(f"\nDataset size: {len(df)}")
    print(f"Review budget: {budget}")

    comparison = evaluate_methods(
        df,
        budget=budget
    )

    print("\nRANKING COMPARISON")
    print("-" * 60)

    print(comparison.to_string(index=False))

    sensitivity = analyze_weights(
        df,
        budget=budget
    )

    print("\nWEIGHT SENSITIVITY")
    print("-" * 60)

    print(sensitivity.to_string(index=False))

    output_folder = Path("evaluation_outputs")

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    comparison.to_csv(
        output_folder / "ranking_comparison.csv",
        index=False
    )

    sensitivity.to_csv(
        output_folder / "weight_sensitivity.csv",
        index=False
    )

    print("\nEVALUATION COMPLETE")

    print(
        f"Reports saved in: {output_folder.resolve()}"
    )

    print("\nLIMITATION:")
    print(
        "Independent reviewer outcomes are needed "
        "to establish actual actionable-case recall."
    )


if __name__ == "__main__":

    run_evaluation(
        file_path="safety_dataset_priority.csv",
        budget=20
    )
