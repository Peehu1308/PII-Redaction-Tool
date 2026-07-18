import re

# Regex for credit card matching
CC_RE = re.compile(r'\b(?:\d[ -]*?){13,19}\b')

def luhn_valid(card_number):
    """
    Validates a credit card number using the Luhn algorithm.
    """
    digits = [int(c) for c in str(card_number) if c.isdigit()]
    if not digits:
        return False
    
    checksum = 0
    for i, d in enumerate(digits[::-1]):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0

EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
IP_RE = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
SSN_RE = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
DOB_RE = re.compile(
    r'\b(?:'
    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|'
    r'(?:January|February|March|April|May|June|July|August|'
    r'September|October|November|December)\s+\d{1,2},\s+\d{4}'
    r')\b',
    re.IGNORECASE
)
CIN_RE = re.compile(r'\b[A-Z]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b')
PAN_RE = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')
GST_RE = re.compile(r'\b\d{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[A-Z0-9]\b')
DIN_RE = re.compile(r'\b\d{8}\b')

ADDRESS_CUE_WORDS = (
    "road", "street", "lane", "village", "taluka",
    "district", "tower", "centre", "office",
    "marg", "complex", "phase", "park",
    "baner", "mumbai", "pune", "maharashtra",
    "india"
)

def looks_like_address(text):
    t = text.lower()
    return (
        any(word in t for word in ADDRESS_CUE_WORDS)
        and len(text.split()) >= 4
    )

def safe_replace(text, original, replacement):
    pattern = r'\b{}\b'.format(re.escape(original))
    return re.sub(pattern, replacement, text)


ORG_STOPLIST = {
    "sebi", "bse", "nse", "bse limited", "national stock exchange of india limited",
    "roc", "registrar of companies", "icai", "companies act", "sebi icdr regulations",
    "sebi act", "scra", "scrr", "depositories act", "rbi", "sebi ltd",
    "sebi complaints redressal mechanism", "scores", "asba", "upi", "npci",
    "life insurance companies", "pension fund", "mutual funds", "qibs",
    "niis", "riis", "financial express", "jansatta", "loksatta",
    "insurance regulatory and development authority of india",
    "pension fund regulatory and development authority",
    "companies act, 2013", "companies act, 1956",
    "book building process", "offer", "the offer", "fresh issue",
    "offer for sale", "red herring prospectus", "draft red herring prospectus",
}

PERSON_STOPLIST = {
    "bidders", "bidder", "allottee", "promoter", "promoters", "director",
    "directors", "auditors", "shareholders", "investors", "anchor investors",
}

ORG_GENERIC_SUFFIX_ONLY = re.compile(
    r"^(the )?(company|board|offer|committee|trust|fund|portion|account|"
    r"process|price|period|form|agreement|shares?)$", re.IGNORECASE
)


def is_probably_real_org(text):
    t = text.strip().lower()
    if t in ORG_STOPLIST:
        return False
    if ORG_GENERIC_SUFFIX_ONLY.match(t):
        return False
    if len(t) < 4:
        return False
    return True


def is_probably_real_person(text):
    t = text.strip().lower()
    if t in PERSON_STOPLIST:
        return False
    tokens = [w for w in re.split(r"\s+", text.strip()) if w.isalpha()]
    if len(tokens) < 2:
        return False
    return True


PHONE_CUE_RE = re.compile(r"(tel|telephone|phone|contact|fax)\s*[:\-]?\s*$", re.IGNORECASE)
PHONE_RE = re.compile(
    r"(?<!\d)(\+?\d{1,3}[\s\-]?)?(\(?\d{2,5}\)?[\s\-]?){1,4}\d{3,5}(?!\d)"
)


def find_phones(text):
    results = []
    for m in PHONE_RE.finditer(text):
        span_text = m.group()
        start = m.start()
        window_before = text[max(0, start - 20):start]
        has_plus = span_text.strip().startswith("+") or "+" in text[max(0, start - 2):start]
        has_cue = bool(PHONE_CUE_RE.search(window_before))
        digit_count = len(re.sub(r"\D", "", span_text))
        if (has_plus or has_cue) and 8 <= digit_count <= 13:
            results.append((start, m.end(), span_text.strip()))
    return results


def find_credit_cards(text):
    results = []
    for m in CC_RE.finditer(text):
        candidate = m.group()
        digits = re.sub(r"\D", "", candidate)
        if len(digits) in (13, 14, 15, 16, 17, 18, 19) and luhn_valid(candidate):
            results.append((m.start(), m.end(), candidate))
    return results
