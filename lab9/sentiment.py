import boto3

def analyze(text: str, lang: str = "en"):
    client = boto3.client("comprehend")
    resp = client.detect_sentiment(Text=text, LanguageCode=lang)
    print(f"Sentiment: {resp['Sentiment']}")
    for k,v in resp["SentimentScore"].items():
        print(f"  {k}: {v:.3f}")

if __name__ == "__main__":
    texts = [
        ("en", "The French Revolution was a period of social and political upheaval in France and its colonies beginning in 1789 and ending in 1799."),
        ("es", "El Quijote es la obra más conocida de Miguel de Cervantes Saavedra. Publicada su primera parte con el título de El ingenioso hidalgo don Quijote de la Mancha a comienzos de 1605, es una de las obras más destacadas de la literatura española y la literatura universal, y una de las más traducidas. En 1615 aparecería la segunda parte del Quijote de Cervantes con el título de El ingenioso caballero don Quijote de la Mancha."),
        ("fr", "Moi je n'étais rien Et voilà qu'aujourd'hui Je suis le gardien Du sommeil de ses nuits Je l'aime à mourir Vous pouvez détruire Tout ce qu'il vous plaira Elle n'a qu'à ouvrir L'espace de ses bras Pour tout reconstruire Pour tout reconstruire Je l'aime à mourir"),
        ("it", "L'amor che move il sole e l'altre stelle."),
    ]
    for lang, t in texts:
        print(f"\n[{lang}]")
        analyze(t, lang)

