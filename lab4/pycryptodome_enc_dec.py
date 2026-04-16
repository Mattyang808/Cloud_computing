
import struct, hashlib, json, base64
import boto3
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

REGION    = "ap-south-1"
BUCKET    = "24181422-cloudstorage"
PREFIX    = ""  
PASSWORD  = "kitty and the kat"

BLOCK_SIZE = 16
CHUNK_SIZE = 64 * 1024

s3 = boto3.client("s3", region_name=REGION)

def _key_from_password(pw: str) -> bytes:
    return hashlib.sha256(pw.encode("utf-8")).digest()

def encrypt_bytes(password: str, plaintext: bytes) -> bytes:
    key = _key_from_password(password)
    iv = get_random_bytes(BLOCK_SIZE)
    encryptor = AES.new(key, AES.MODE_CBC, iv)

    pad_len = (-len(plaintext)) % BLOCK_SIZE
    if pad_len:
        plaintext += b" " * pad_len

    header = struct.pack("<Q", len(plaintext) - pad_len) + iv
    return header + encryptor.encrypt(plaintext)

def decrypt_bytes(password: str, blob: bytes) -> bytes:
    orig_size = struct.unpack("<Q", blob[:8])[0]
    iv = blob[8:24]
    ciphertext = blob[24:]

    key = _key_from_password(password)
    decryptor = AES.new(key, AES.MODE_CBC, iv)
    pt_padded = decryptor.decrypt(ciphertext)
    return pt_padded[:orig_size]

def to_text(b: bytes) -> str:
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        # fallback preview for binary
        return "(binary)\nhex:" + b[:64].hex() + ("..." if len(b) > 64 else "")

# Walk S3 and process each object
p = s3.get_paginator("list_objects_v2")
for page in p.paginate(Bucket=BUCKET, Prefix=PREFIX):
    for obj in page.get("Contents", []):
        key = obj["Key"]
        # skip "folders" and outputs we create
        if key.endswith("/") or key.endswith(".lenc") or key.endswith(".ldec"):
            continue

        # 1) download original
        body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()

        # 2) encrypt -> write <key>.lenc
        enc_blob = encrypt_bytes(PASSWORD, body)
        s3.put_object(Bucket=BUCKET, Key=key + ".lenc", Body=enc_blob)
        print(f"\n=== {key} ===")
        print("--- ORIGINAL (utf-8 or hex preview) ---")
        print(to_text(body))

        # show encrypted as base64 for readability
        print("\n--- ENCRYPTED (.lenc) base64 ---")
        print(base64.b64encode(enc_blob).decode("ascii"))
        print("Encrypted ->", f"s3://{BUCKET}/{key}.lenc")

        # 3) decrypt -> write <key>.ldec 
        dec_plain = decrypt_bytes(PASSWORD, enc_blob)
        s3.put_object(Bucket=BUCKET, Key=key + ".ldec", Body=dec_plain)

        print("\n--- DECRYPTED (utf-8 or hex preview) ---")
        print(to_text(dec_plain))
        print("Decrypted ->", f"s3://{BUCKET}/{key}.ldec")

