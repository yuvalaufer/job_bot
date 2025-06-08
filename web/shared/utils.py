import langdetect

def contains_required_terms(text, required_terms):
    text_lower = text.lower()
    return all(term.lower() in text_lower for term in required_terms)

def is_english(text):
    try:
        lang = langdetect.detect(text)
        return lang == 'en'
    except:
        return False
