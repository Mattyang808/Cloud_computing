# lab4/KMS_encrypt_decrypt.py
import boto3, base64

REGION     = "ap-south-1"
BUCKET     = "24181422-cloudstorage"
PREFIX     = ""   
KMS_KEY_ID = "0d980fb4-43c8-4aea-ae5e-a5939310872f"  

s3  = boto3.client("s3")
kms = boto3.client("kms", region_name=REGION)

def to_text(b: bytes) -> str:
    # best-effort display for plaintext; if binary, show a short hex preview
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return "(binary)\nhex:" + b[:64].hex() + ("..." if len(b) > 64 else "")

p = s3.get_paginator("list_objects_v2")
for page in p.paginate(Bucket=BUCKET, Prefix=PREFIX):
    for obj in page.get("Contents", []):
        key = obj["Key"]
        if key.endswith("/") or key.endswith(".kenc") or key.endswith(".kdec"):
            continue

        # download original plaintext
        body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
        if len(body) > 4096:
            print(f"\n=== {key} ===")
            print(f"SKIP (>4KB): {len(body)} bytes")
            continue

        # encrypt with KMS (direct)
        enc = kms.encrypt(KeyId=KMS_KEY_ID, Plaintext=body, EncryptionAlgorithm="SYMMETRIC_DEFAULT")
        cipher_blob = enc["CiphertextBlob"]  # bytes
        s3.put_object(Bucket=BUCKET, Key=key + ".kenc", Body=cipher_blob)

        # decrypt back
        pt = kms.decrypt(CiphertextBlob=cipher_blob, EncryptionAlgorithm="SYMMETRIC_DEFAULT")["Plaintext"]
        s3.put_object(Bucket=BUCKET, Key=key + ".kdec", Body=pt)

        # ---- display contents ----
        print(f"\n=== {key} ===")
        print("--- ORIGINAL (utf-8 or hex preview) ---")
        print(to_text(body))

        print("\n--- ENCRYPTED (.kenc) base64 ---")
        print(base64.b64encode(cipher_blob).decode("ascii"))

        print("\n--- DECRYPTED (utf-8 or hex preview) ---")
        print(to_text(pt))

        print(f"\nWrote: s3://{BUCKET}/{key}.kenc")
        print(f"Wrote: s3://{BUCKET}/{key}.kdec")

