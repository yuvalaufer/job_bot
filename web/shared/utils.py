import langdetect

def contains_required_terms(text, required_terms):
    """
    Return True if all required terms appear in the text (case-insensitive).
    """
    text_lower = text.lower()
    return all(term.lower() in text_lower for term in required_terms)

def is_english(text):
    """
    Try to detect language — accept only english.
    """
    try:
        lang = langdetect.detect(text)
        return lang == 'en'
    except:
        return False

