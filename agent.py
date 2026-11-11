
import pandas as pd

from evaluation import (
    load_data,
    calculate_priority,
    evaluate_methods,
    analyze_weights
)

DATA_FILE = "safety_dataset_priority.csv"
DECISIONS_FILE = "reviewer_decisions.csv"


# ============================================================
# LOAD REVIEWER DECISIONS
# ============================================================

def load_resolved_ids():

    try:

        decisions = pd.read_csv(
            DECISIONS_FILE,
            dtype={"id": str}
        )

        resolved = decisions[
            decisions["resolved"]
            .astype(str)
            .str.lower()
            .eq("true")
        ]

        return set(
            resolved["id"]
        )

    except FileNotFoundError:

        return set()


# ============================================================
# ANALYST AGENT
# ============================================================

def agent(request):

    df = load_data(DATA_FILE)

    df = calculate_priority(
        df,
        severity_weight=0.60
    )

    request = request.lower().strip()

    print("\n" + "=" * 60)
    print("AI SAFETY DATA ANALYST")
    print("=" * 60)

    # --------------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------------

    if "overview" in request:

        print(f"\nTotal cases: {len(df)}")

        print(
            f"Average confidence: "
            f"{df['confidence'].mean():.1f}%"
        )

        print("\nCategories:")

        print(
            df["classification"].value_counts()
        )

    # --------------------------------------------------------
    # PRIORITY QUEUE
    # --------------------------------------------------------

    elif "priority" in request or "queue" in request:

        resolved_ids = load_resolved_ids()

        pending = df[
            ~df["id"].astype(str).isin(
                resolved_ids
            )
        ]

        ranked = pending.sort_values(
            "priority_score",
            ascending=False
        )

        print("\nTOP PRIORITY CASES")

        print(
            ranked[
                [
                    "id",
                    "classification",
                    "severity",
                    "confidence",
                    "priority_score"
                ]
            ].head(20).to_string(index=False)
        )

    # --------------------------------------------------------
    # EVALUATION
    # --------------------------------------------------------

    elif "compare" in request or "evaluation" in request:

        results = evaluate_methods(
            df,
            budget=20
        )

        print("\nRANKING COMPARISON")

        print(
            results.to_string(index=False)
        )

    # --------------------------------------------------------
    # WEIGHT SENSITIVITY
    # --------------------------------------------------------

    elif "weight" in request or "sensitivity" in request:

        results = analyze_weights(
            df,
            budget=20
        )

        print("\nWEIGHT SENSITIVITY")

        print(
            results.to_string(index=False)
        )

    # --------------------------------------------------------
    # ANALYST REPORT
    # --------------------------------------------------------

    elif "report" in request:

        ranked = df.sort_values(
            "priority_score",
            ascending=False
        )

        print("\nANALYST REPORT")

        print(f"Dataset size: {len(df)}")

        print(
            f"Average confidence: "
            f"{df['confidence'].mean():.1f}%"
        )

        print("\nHighest priority cases:")

        print(
            ranked[
                [
                    "id",
                    "classification",
                    "priority_score"
                ]
            ].head(10).to_string(index=False)
        )

        print(
            "\nRecommendation: Review the highest "
            "priority unresolved cases first."
        )

        print(
            "\nLimitation: Independent reviewer outcomes "
            "are required to establish whether the "
            "ranking improves results."
        )

    else:

        print("\nAvailable commands:")

        print("- overview")
        print("- priority queue")
        print("- compare rankings")
        print("- weight sensitivity")
        print("- analyst report")


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\nAI SAFETY DATA ANALYST")

    while True:

        request = input(
            "\nWhat would you like to investigate? "
        )

        if request.lower().strip() in [
            "exit",
            "quit",
            "q"
        ]:
            print("Agent shutting down.")
            break

        try:

            agent(request)

        except Exception as e:

            print(f"Error: {e}")
