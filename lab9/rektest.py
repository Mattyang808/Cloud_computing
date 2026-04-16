import boto3
BUCKET = "24181422-lab9"   # <-- same bucket as above

rek = boto3.client("rekognition")

def labels(key):
    resp = rek.detect_labels(Image={"S3Object": {"Bucket": BUCKET, "Name": key}}, MaxLabels=20)
    print(f"\n=== LABELS for {key} ===")
    for l in resp["Labels"]:
        print(f"{l['Name']}: {l['Confidence']:.1f}%")

def moderation(key):
    resp = rek.detect_moderation_labels(Image={"S3Object": {"Bucket": BUCKET, "Name": key}})
    print(f"\n=== MODERATION for {key} ===")
    if not resp["ModerationLabels"]:
        print("No moderation labels detected.")
    else:
        for l in resp["ModerationLabels"]:
            print(f"{l['Name']} ({l['ParentName']}): {l['Confidence']:.1f}%")

def faces(key):
    resp = rek.detect_faces(Image={"S3Object": {"Bucket": BUCKET, "Name": key}}, Attributes=["ALL"])
    print(f"\n=== FACES for {key} ===")
    print(f"FaceCount: {len(resp['FaceDetails'])}")
    for i, fd in enumerate(resp["FaceDetails"], 1):
        print(f"- Face {i}: Age {fd['AgeRange']['Low']}-{fd['AgeRange']['High']}, "
              f"Gender {fd['Gender']['Value']}({fd['Gender']['Confidence']:.0f}%), "
              f"Smile {fd['Smile']['Value']}, Eyeglasses {fd['Eyeglasses']['Value']}")

def text_detect(key):
    resp = rek.detect_text(Image={"S3Object": {"Bucket": BUCKET, "Name": key}})
    print(f"\n=== TEXT for {key} ===")
    for d in resp["TextDetections"]:
        if d["Type"] == "LINE":
            print(d["DetectedText"])

if __name__ == "__main__":
    labels("urban.jpg")          # 1) Label recognition
    moderation("beach.jpg")      # 2) Image moderation
    faces("faces.jpg")           # 3) Facial analysis
    text_detect("text.jpg")      # 4) Text extraction

