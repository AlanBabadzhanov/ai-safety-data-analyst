import pandas as pd


# ============================================================
# DATA TOOLS
# ============================================================

def load_data():
    return pd.read_csv("safety_dataset.csv")


def dataset_overview(df):
    return {
        "total_items": len(df),
        "categories": df["classification"].value_counts().to_dict(),
        "average_confidence": round(df["confidence"].mean(), 1),
        "human_review_count": int(
            df["human_review"]
            .astype(str)
            .str.strip()
            .str.upper()
            .eq("YES")
            .sum()
        )
    }


def find_low_confidence(df):
    return df[df["confidence"] < 70].sort_values("confidence")


def find_high_risk(df):
    risk_categories = ["Youth Safety", "Harassment"]

    return df[
        df["classification"].isin(risk_categories)
    ].sort_values("confidence")


def category_analysis(df):
    results = []

    for category in df["classification"].unique():
        category_df = df[df["classification"] == category]

        results.append({
            "category": category,
            "count": len(category_df),
            "average_confidence": round(
                category_df["confidence"].mean(), 1
            ),
            "human_review_count": int(
                category_df["human_review"]
                .astype(str)
                .str.strip()
                .str.upper()
                .eq("YES")
                .sum()
            )
        })

    return pd.DataFrame(results).sort_values(
        "average_confidence"
    )


def analyst_report(df):
    overview = dataset_overview(df)
    low_confidence = find_low_confidence(df)
    categories = category_analysis(df)

    lowest_category = categories.iloc[0]["category"]

    most_reviewed_category = (
        categories.sort_values(
            "human_review_count",
            ascending=False
        ).iloc[0]["category"]
    )

    lowest_item = low_confidence.iloc[0]

    return {
        "dataset_size": overview["total_items"],
        "average_confidence": overview["average_confidence"],
        "low_confidence_count": len(low_confidence),
        "low_confidence_rate": round(
            len(low_confidence) / len(df) * 100,
            1
        ),
        "lowest_confidence_category": lowest_category,
        "most_human_review_category": most_reviewed_category,
        "lowest_confidence_item": int(lowest_item["id"]),
        "recommended_review_priority": (
            "Review the lowest-confidence cases first."
        )
    }


# ============================================================
# AGENT ROUTING
# ============================================================

def route_request(request):
    """
    Decide which analysis tool should handle the user's request.

    More specific requests are checked BEFORE broad requests.
    This prevents phrases such as "low confidence cases in the
    dataset" from incorrectly being routed to dataset overview.
    """

    request = request.lower().strip()

    # --------------------------------------------------------
    # 1. LOW CONFIDENCE / REVIEW
    # --------------------------------------------------------
    if (
        "low confidence" in request
        or "low-confidence" in request
        or "uncertain" in request
        or "uncertainty" in request
        or (
            "confidence" in request
            and (
                "review" in request
                or "cases" in request
                or "items" in request
            )
        )
    ):
        return "low_confidence"

    # --------------------------------------------------------
    # 2. HIGH RISK
    # --------------------------------------------------------
    if (
        "high risk" in request
        or "high-risk" in request
        or "risk" in request
        or "risky" in request
        or "youth safety" in request
        or "harassment" in request
    ):
        return "high_risk"

    # --------------------------------------------------------
    # 3. CATEGORY ANALYSIS
    # --------------------------------------------------------
    if (
        "category" in request
        or "categories" in request
        or "compare" in request
        or "comparison" in request
    ):
        return "categories"

    # --------------------------------------------------------
    # 4. ANALYST REPORT
    # --------------------------------------------------------
    if (
        "report" in request
        or "summary" in request
        or "recommendation" in request
        or "recommendations" in request
    ):
        return "report"

    # --------------------------------------------------------
    # 5. DATASET OVERVIEW
    # --------------------------------------------------------
    if (
        "overview" in request
        or "dataset" in request
        or "data" in request
        or "how many" in request
        or "average" in request
    ):
        return "overview"

    # Nothing matched
    return "unknown"


# ============================================================
# AGENT
# ============================================================

def agent(request):
    df = load_data()

    tool = route_request(request)

    print("\n" + "=" * 60)
    print("AI SAFETY DATA ANALYST")
    print("=" * 60)

    print(f"\nRequest: {request}")
    print(f"Selected analysis: {tool}")

    # --------------------------------------------------------
    # LOW CONFIDENCE
    # --------------------------------------------------------
    if tool == "low_confidence":
        results = find_low_confidence(df)

        print("\nLOW CONFIDENCE CASES")
        print("-" * 60)

        if results.empty:
            print("No low-confidence cases found.")
        else:
            print(
                results[
                    [
                        "id",
                        "classification",
                        "confidence",
                        "human_review"
                    ]
                ].to_string(index=False)
            )

    # --------------------------------------------------------
    # HIGH RISK
    # --------------------------------------------------------
    elif tool == "high_risk":
        results = find_high_risk(df)

        print("\nHIGH RISK CASES")
        print("-" * 60)

        if results.empty:
            print("No high-risk cases found.")
        else:
            print(
                results[
                    [
                        "id",
                        "classification",
                        "confidence",
                        "human_review"
                    ]
                ].to_string(index=False)
            )

    # --------------------------------------------------------
    # CATEGORY ANALYSIS
    # --------------------------------------------------------
    elif tool == "categories":
        results = category_analysis(df)

        print("\nCATEGORY ANALYSIS")
        print("-" * 60)
        print(results.to_string(index=False))

    # --------------------------------------------------------
    # ANALYST REPORT
    # --------------------------------------------------------
    elif tool == "report":
        report = analyst_report(df)

        print("\nANALYST REPORT")
        print("-" * 60)

        print(f"Dataset size: {report['dataset_size']}")
        print(
            f"Average confidence: "
            f"{report['average_confidence']}%"
        )
        print(
            f"Low-confidence cases: "
            f"{report['low_confidence_count']}"
        )
        print(
            f"Low-confidence rate: "
            f"{report['low_confidence_rate']}%"
        )
        print(
            f"Lowest-confidence category: "
            f"{report['lowest_confidence_category']}"
        )
        print(
            f"Category with most human-review cases: "
            f"{report['most_human_review_category']}"
        )
        print(
            f"Lowest-confidence item: "
            f"ID {report['lowest_confidence_item']}"
        )
        print(
            f"Recommendation: "
            f"{report['recommended_review_priority']}"
        )

    # --------------------------------------------------------
    # DATASET OVERVIEW
    # --------------------------------------------------------
    elif tool == "overview":
        results = dataset_overview(df)

        print("\nDATASET OVERVIEW")
        print("-" * 60)

        print(f"Total items: {results['total_items']}")
        print(
            f"Average confidence: "
            f"{results['average_confidence']}%"
        )
        print(
            f"Human-review items: "
            f"{results['human_review_count']}"
        )

        print("\nCategories:")

        for category, count in results["categories"].items():
            print(f"  {category}: {count}")

    # --------------------------------------------------------
    # UNKNOWN REQUEST
    # --------------------------------------------------------
    else:
        print("\nI don't know which analysis you want yet.")

        print("\nTry asking:")
        print('  - "Give me an overview"')
        print('  - "Show me the low confidence cases"')
        print('  - "Find the high risk cases"')
        print('  - "Compare the categories"')
        print('  - "Give me an analyst report"')


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("AI SAFETY DATA AGENT")
    print("=" * 60)

    print("\nI can analyze the safety dataset.")

    while True:

        request = input(
            "\nWhat would you like me to investigate? "
        )

        if request.lower().strip() in [
            "exit",
            "quit",
            "q"
        ]:
            print("\nAgent shutting down.")
            break

        agent(request)
