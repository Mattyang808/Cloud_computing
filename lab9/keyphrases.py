import boto3

def detect_key_phrases(text: str, lang: str):
    client = boto3.client("comprehend")
    resp = client.detect_key_phrases(Text=text, LanguageCode=lang)
    for kp in resp["KeyPhrases"]:
        print(f"{kp['Text']}  (score={kp['Score']:.2f})")

if __name__ == "__main__":
    samples = [
        ("en", "The French Revolution was a period of social and political upheaval in France and its colonies beginning in 1789 and ending in 1799."),
        ("es", "El Quijote es la obra más conocida de Miguel de Cervantes Saavedra. Publicada su primera parte con el título de El ingenioso hidalgo don Quijote de la Mancha a comienzos de 1605, es una de las obras más destacadas de la literatura española y la literatura universal, y una de las más traducidas. En 1615 aparecería la segunda parte del Quijote de Cervantes con el título de El ingenioso caballero don Quijote de la Mancha."),
        ("fr", "Moi je n'étais rien Et voilà qu'aujourd'hui Je suis le gardien Du sommeil de ses nuits Je l'aime à mourir Vous pouvez détruire Tout ce qu'il vous plaira Elle n'a qu'à ouvrir L'espace de ses bras Pour tout reconstruire Pour tout reconstruire Je l'aime à mourir"),
        ("it", "L'amor che move il sole e l'altre stelle."),
    ]
    for lang, t in samples:
        print(f"\n[{lang}]")
        detect_key_phrases(t, lang)

