def contains_offensive_language(text: str) -> bool:
    offensive_words = ["urat", "prost", "idiot", "nesimtit", "cretin"]
    text_lower = text.lower()
    return any(word in text_lower for word in offensive_words)