import json
from transformers import pipeline
from sklearn.metrics import precision_recall_fscore_support


def evaluate_model(json_path):
    print(f"Loading data from {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data["data"]
    print(f"Found {len(entries)} entries.")

    print("Initializing classifier...")
    try:
        classifier = pipeline(
            "text-classification",
            model="MatteoFasulo/mdeberta-v3-base-subjectivity-multilingual",
            tokenizer="microsoft/mdeberta-v3-base",
            device=-1,  # Run on CPU to avoid potential CUDA issues if not set up, or remove for auto
        )
    except Exception as e:
        print(f"Error initializing classifier: {e}")
        return

    y_true = []
    y_pred = []

    print("Running classification...")
    for i, entry in enumerate(entries):
        text = entry["source"]
        true_label = entry["checkworthy"]  # Boolean

        # Truncate text if too long for the model, though pipeline usually handles it or errors.
        # mDeBERTa usually has 512 token limit. Pipeline might truncate automatically?
        # Let's trust the pipeline for now, but handle potential errors.
        try:
            output = classifier(text, truncation=True, max_length=512)
            # Output format: [{'label': 'SUBJ', 'score': 0.99}]
            label = output[0]["label"]

            # Mapping: OBJ -> Checkworthy (True), SUBJ -> Not Checkworthy (False)
            predicted_checkworthy = label == "OBJ"

            y_true.append(true_label)
            y_pred.append(predicted_checkworthy)

            if i % 10 == 0:
                print(f"Processed {i}/{len(entries)}")

        except Exception as e:
            print(f"Error processing entry {i}: {e}")
            continue

    print("Calculating metrics...")
    # Calculate precision, recall, f1 for the positive class (True/Checkworthy)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary"
    )

    print("\nResults:")
    print(y_true)
    print(y_pred)
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")


if __name__ == "__main__":
    import sys

    filename = sys.argv[1] if len(sys.argv) > 1 else "dev_test.json"
    evaluate_model(filename)
