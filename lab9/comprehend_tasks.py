# comprehend_tasks.py
import boto3
from collections import Counter

# Texts
ENGLISH = """The French Revolution was a period of social and political upheaval in France and its colonies beginning in 1789 and ending in 1799."""
SPANISH = """El Quijote es la obra más conocida de Miguel de Cervantes Saavedra. Publicada su primera parte con el título de El ingenioso hidalgo don Quijote de la Mancha a comienzos de 1605, es una de las obras más destacadas de la literatura española y la literatura universal, y una de las más traducidas. En 1615 aparecería la segunda parte del Quijote de Cervantes con el título de El ingenioso caballero don Quijote de la Mancha."""
FRENCH  = """Moi je n'étais rien Et voilà qu'aujourd'hui Je suis le gardien Du sommeil de ses nuits Je l'aime à mourir Vous pouvez détruire Tout ce qu'il vous plaira Elle n'a qu'à ouvrir L'espace de ses bras Pour tout reconstruire Pour tout reconstruire Je l'aime à mourir"""
ITALIAN = """L'amor che move il sole e l'altre stelle."""
ALL_TEXTS = {"English": ENGLISH, "Spanish": SPANISH, "French": FRENCH, "Italian": ITALIAN}

LANG_NAME = {"en": "English", "es": "Spanish", "fr": "French", "it": "Italian"}
SYNTAX_OK = {"en", "es", "fr", "it"}  

comprehend = boto3.client("comprehend")

def main():
    for label, text in ALL_TEXTS.items():
        print("=" * 70)
        print(f"Input: {label}")

        # Language
        langs = comprehend.detect_dominant_language(Text=text)["Languages"]
        best = max(langs, key=lambda x: x["Score"])
        code, conf = best["LanguageCode"], best["Score"]
        print(f"{LANG_NAME.get(code, code)} was detected with {conf*100:.0f}% confidence")

        # Sentiment
        s = comprehend.detect_sentiment(Text=text, LanguageCode=code)
        print("Sentiment:", s["Sentiment"], s["SentimentScore"])

        # Entities
        ents = comprehend.detect_entities(Text=text, LanguageCode=code)["Entities"]
        print("Entities:", [(e["Text"], e["Type"]) for e in ents][:10] or "None")

        # Key phrases
        kps = comprehend.detect_key_phrases(Text=text, LanguageCode=code)["KeyPhrases"]
        print("Key phrases:", [k["Text"] for k in kps][:10] or "None")

        # Syntax (POS counts)
        if code in SYNTAX_OK:
            toks = comprehend.detect_syntax(Text=text, LanguageCode=code)["SyntaxTokens"]
            pos_counts = Counter(t["PartOfSpeech"]["Tag"] for t in toks)
            print("Syntax POS counts:", dict(pos_counts))
        else:
            print("Syntax: skipped (language not in minimal set)")

if __name__ == "__main__":
    main()
