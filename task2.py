def run_task2(example: dict) -> list:
    """
    Baseline claim extraction for Task 2.
    Splits the comment into chunks of 50 characters.
    """
    text = example.get("source", "")
    return [text[i:i+50] for i in range(0, len(text), 50)]
