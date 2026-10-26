"""Standalone risk assessment tool for a 5x5 likelihood-consequence matrix."""


def assess_risk(likelihood, consequence):
    """Return the risk score and its classification."""
    score = likelihood * consequence

    if score <= 4:
        classification = "Low"
    elif score <= 9:
        classification = "Medium"
    elif score <= 16:
        classification = "High"
    else:
        classification = "Critical"

    return score, classification


def main():
    print("\n====== RISK ASSESSMENT ======")
    try:
        likelihood = int(input("Likelihood (1-5): "))
        consequence = int(input("Consequence (1-5): "))
    except ValueError:
        print("Enter whole numbers only.")
        return

    if not (1 <= likelihood <= 5 and 1 <= consequence <= 5):
        print("Values must be between 1 and 5.")
        return

    score, classification = assess_risk(likelihood, consequence)
    print("\nRisk score:", score)
    print("Classification:", classification)

    if classification == "High":
        print("WARNING: High risk identified. Take corrective action.")
    elif classification == "Critical":
        print("CRITICAL WARNING: Immediate risk control is required.")
    elif classification == "Medium":
        print("Notice: Apply suitable risk control measures.")
    else:
        print("Low risk: Continue monitoring the risk.")


if __name__ == "__main__":
    main()
