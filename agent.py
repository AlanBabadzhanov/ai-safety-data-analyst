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
            .str.upper()
            .eq("YES")
            .sum()
        ),
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
        category_df = df[
            df["classification"] == category
        ]

        results.append({
            "category": category,
            "items": len(category_df),
            "average_confidence": round(
                category_df["confidence"].mean(), 1
            ),
            "human_review": int(
                category_df["human_review"]
                .astype(str)
                .str.upper()
                .eq("YES")
                .sum()
            )
        })

    return pd.DataFrame(results)

# ============================================================
# REPORT GENERATOR
# ============================================================

def generate_report(df):

    total_items = len(df)

    average_confidence = df["confidence"].mean()

    review_items = df[
        df["human_review"]
        .astype(str)
        .str.upper()
        .eq("YES")
    ]

    review_rate = len(review_items) / total_items * 100

    category_stats = (
        df.groupby("classification")
        .agg(
            items=("id", "count"),
            average_confidence=("confidence", "mean"),
            human_reviews=(
                "human_review",
                lambda x: (
                    x.astype(str)
                    .str.upper()
                    .eq("YES")
                    .sum()
                )
            )
        )
        .reset_index()
    )

    lowest_confidence_category = (
        category_stats
        .sort_values("average_confidence")
        .iloc[0]
    )

    highest_review_category = (
        category_stats
        .sort_values("human_reviews", ascending=False)
        .iloc[0]
    )

    lowest_confidence_item = (
        df.sort_values("confidence")
        .iloc[0]
    )

    print("\n")
    print("================================================")
    print("           AI SAFETY ANALYST REPORT")
    print("================================================")

    print("\nEXECUTIVE SUMMARY")
    print("------------------")

    print(
        f"The dataset contains {total_items} items "
        f"with an average model confidence of "
        f"{average_confidence:.1f}%."
    )

    print(
        f"{len(review_items)} items "
        f"({review_rate:.1f}%) are currently "
        f"marked for human review."
    )

    print("\nKEY FINDINGS")
    print("------------")

    print(
        f"• {lowest_confidence_category['classification']} "
        f"has the lowest average confidence at "
        f"{lowest_confidence_category['average_confidence']:.1f}%."
    )

    print(
        f"• {highest_review_category['classification']} "
        f"has the most human-review cases "
        f"({int(highest_review_category['human_reviews'])})."
    )

    print(
        f"• The lowest-confidence item is ID "
        f"{lowest_confidence_item['id']} "
        f"at {lowest_confidence_item['confidence']}%."
    )

    print("\nRECOMMENDED REVIEW PRIORITY")
    print("----------------------------")

    priority = (
        df[df["confidence"] < 70]
        .sort_values("confidence")
    )

    if len(priority) > 0:

        for _, row in priority.iterrows():

            print(
                f"• ID {row['id']} | "
                f"{row['classification']} | "
                f"{row['confidence']}% confidence"
            )

    else:

        print("No immediate review priorities identified.")

    print("\n================================================")
    print("Report complete.")
    print("================================================")

# ============================================================
# AGENT
# ============================================================

def agent(request):
    """
    Decide which analysis tool should be used
    based on the user's request.
    """

    df = load_data()

    request = request.lower()

    print("\n🤖 AGENT DECISION")
    print("-----------------")

    # Tool 1: Overview
    if any(word in request for word in [
        "overview",
        "summary",
        "summarize",
        "dataset",
        "everything"
    ]):

        print("Selected tool: Dataset Overview")

        results = dataset_overview(df)

        print("\n📊 DATASET OVERVIEW")
        print("-------------------")
        print(f"Total items: {results['total_items']}")
        print(
            f"Average confidence: "
            f"{results['average_confidence']}%"
        )

        print(
            f"Human review items: "
            f"{results['human_review_count']}"
        )

        print("\nCategories:")

        for category, count in results["categories"].items():
            print(f"  • {category}: {count}")


    # Tool 2: Low confidence
    elif any(word in request for word in [
        "low confidence",
        "uncertain",
        "unclear",
        "review",
        "human"
    ]):

        print("Selected tool: Human Review Queue")

        results = find_low_confidence(df)

        print("\n⚠️ HUMAN REVIEW QUEUE")
        print("---------------------")

        if len(results) == 0:
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


    # Tool 3: Risk
    elif any(word in request for word in [
        "risk",
        "risky",
        "danger",
        "dangerous"
    ]):

        print("Selected tool: Risk Analysis")

        results = find_high_risk(df)

        print("\n🚨 POTENTIAL HIGH-RISK ITEMS")
        print("----------------------------")

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

    # Tool 4: Analyst Report
    elif any(word in request for word in [
        "report",
        "findings",
        "recommendations",
        "insights",
        "analyze everything"
    ]):

        print("Selected tool: Analyst Report")

        generate_report(df)

    # Tool 4: Categories
    elif any(word in request for word in [
        "category",
        "categories",
        "breakdown",
        "compare"
    ]):

        print("Selected tool: Category Analysis")

        results = category_analysis(df)

        print("\n📈 CATEGORY ANALYSIS")
        print("--------------------")

        print(
            results.to_string(index=False)
        )


    else:

        print("I don't know which analysis you want yet.")

        print("\nTry asking:")
        print("  • Give me an overview")
        print("  • Show me low confidence cases")
        print("  • Find the riskiest cases")
        print("  • Compare the categories")


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n======================================")
    print("       AI SAFETY DATA AGENT")
    print("======================================")

    print("\nI can analyze the safety dataset.")

    while True:

        request = input(
            "\nWhat would you like me to investigate? "
        )

        if request.lower() in [
            "exit",
            "quit",
            "q"
        ]:
            print("\nAgent shutting down.")
            break

        agent(request)