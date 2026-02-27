def run_task1(example: dict) -> bool:
    """
    Baseline checkworthiness prediction for Task 1.
    False if < 10 chars or contains subjective phrases.
    """
    text = example.get("source", "").lower()
    if len(text) < 10:
        return False
    
    subjective_phrases = ["imo", "myslim si", "podle mne", "muj nazor", "ja"]
    if any(phrase in text for phrase in subjective_phrases):
        return False
    
    return True
