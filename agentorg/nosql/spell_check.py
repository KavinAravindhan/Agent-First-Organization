class SpellChecker:
    """
    A minimal, dummy spell checker to illustrate the approach.
    You can integrate a library like 'textblob' or 'pyspellchecker' if desired.
    """

    def __init__(self):
        try:
            from spellchecker import SpellChecker as PySpellChecker
            self.spellchecker = PySpellChecker()
        except ImportError:
            self.spellchecker = None
            print("Warning: 'pyspellchecker' is not installed. The correct_spelling method will return the text as is.")

    def correct_spelling(self, text: str) -> str:
        """
        Splits the sentence into words, attempts to correct each word using pyspellchecker,
        and then rejoins them. If pyspellchecker is unavailable, returns the original text.
        """
        if not self.spellchecker:
            return text

        words = text.split()
        corrected_words = []
        for word in words:
            # 'correction()' gives the most probable corrected word
            corrected = self.spellchecker.correction(word)
            # If correction is None or empty, use the original word
            corrected_words.append(corrected if corrected else word)

        # Reconstruct the sentence
        return " ".join(corrected_words)


# EXAMPLE USAGE

# if __name__ == "__main__":
#     sc = SpellChecker()
#     text = "I am verry happi to se this speling checker worrking!"
#     corrected = sc.correct_spelling(text)
#     print("Original:", text)
#     print("Corrected:", corrected)

# EXAMPLE OUTPUT

# Original: I am verry happi to se this speling checker worrking!
# Corrected: I am very happy to see this spelling checker working!

