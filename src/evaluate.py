import sys
from trial import RedactionEngine

def evaluate():
    text = (
        "John Doe and Rashi Patil attended the meeting at Nuvama Wealth Management Ltd "
        "on 12-05-1990. Their emails are john.doe@example.com and rashhi.patil@gmail.com. "
        "You can reach John at Telephone: +91 98765 43210 or Rashi at +91 22 4009 4400. "
        "Their office is located at 123 Main Street, Andheri East, Mumbai, Maharashtra. "
        "The SSN for John is 123-45-6789 and his credit card is 4111 1111 1111 1111."
    )
    
    ground_truth = {
        "PERSON": ["John Doe", "Rashi Patil", "John", "Rashi"],
        "ORG": ["Nuvama Wealth Management Ltd"],
        "EMAIL": ["john.doe@example.com", "rashhi.patil@gmail.com"],
        "PHONE": ["+91 98765 43210", "+91 22 4009 4400"],
        "ADDRESS": ["123 Main Street, Andheri East, Mumbai, Maharashtra"],
        "SSN": ["123-45-6789"],
        "CREDIT_CARD": ["4111 1111 1111 1111"],
        "DOB": ["12-05-1990"]
    }

    engine = RedactionEngine()
    
    entities = engine.extract_entities([text])
    
    from trial import EMAIL_RE, find_phones, SSN_RE, find_credit_cards, DOB_RE
    
    detected = {
        "PERSON": list(entities.get("PERSON", [])),
        "ORG": list(entities.get("ORG", [])),
        "ADDRESS": list(entities.get("ADDRESS", [])),
        "EMAIL": [m.group() for m in EMAIL_RE.finditer(text)],
        "PHONE": [phone for _, _, phone in find_phones(text)],
        "SSN": [m.group() for m in SSN_RE.finditer(text)],
        "CREDIT_CARD": [cc for _, _, cc in find_credit_cards(text)],
        "DOB": [m.group() for m in DOB_RE.finditer(text)],
    }
    
    print("=== PII Detection Evaluation ===")
    total_true_positives = 0
    total_actual = 0
    total_detected = 0
    
    for category in ground_truth:
        actual_items = set(ground_truth[category])
        detected_items = set(detected[category])
        
        true_positives = actual_items.intersection(detected_items)
        false_positives = detected_items - actual_items
        false_negatives = actual_items - detected_items
        
        tp = len(true_positives)
        fp = len(false_positives)
        fn = len(false_negatives)
        
        total_true_positives += tp
        total_actual += len(actual_items)
        total_detected += len(detected_items)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        print(f"[{category}] Precision: {precision:.2f}, Recall: {recall:.2f}")
        if fp > 0:
            print(f"  False Positives: {false_positives}")
        if fn > 0:
            print(f"  False Negatives: {false_negatives}")

    overall_precision = total_true_positives / total_detected if total_detected > 0 else 0.0
    overall_recall = total_true_positives / total_actual if total_actual > 0 else 0.0
    overall_f1 = (2 * overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0.0
    
    print("\n=== Overall Metrics ===")
    print(f"Accuracy (F1-Score): {overall_f1:.2f}")
    print(f"Precision: {overall_precision:.2f}")
    print(f"Recall: {overall_recall:.2f}")

if __name__ == "__main__":
    evaluate()
