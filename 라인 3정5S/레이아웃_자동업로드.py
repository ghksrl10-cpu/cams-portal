# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import base64, json
import requests
from PIL import Image, ImageGrab

PROJECT = "cams-torque"
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/settings/fivees_layout"

def compress(img, max_dim=1400, quality=55):
    w, h = img.size
    if w >= h and w > max_dim:
        h = round(h * max_dim / w); w = max_dim
    elif h > w and h > max_dim:
        w = round(w * max_dim / h); h = max_dim
    img = img.resize((w, h), Image.LANCZOS).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue(), w, h

def upload(data_url):
    body = {"fields": {"layout": {"stringValue": data_url}}}
    r = requests.patch(FIRESTORE_URL, json=body, timeout=30)
    r.raise_for_status()

print("=" * 50)
print("  레이아웃 이미지 업로드")
print("=" * 50)

# 1) 클립보드에서 이미지 가져오기
print("\n클립보드 이미지 확인 중...")
img = ImageGrab.grabclipboard()
if img is None:
    print("\n[X] 클립보드에 이미지가 없습니다.")
    print("   채팅에서 이미지를 우클릭 → '이미지 복사' 후 다시 실행하세요.")
    input("\n엔터를 누르면 종료합니다...")
    sys.exit(1)

print(f"[OK] 이미지 감지됨  ({img.width}×{img.height}px)")

# 2) 압축
print("압축 중...")
raw, w, h = compress(img)
b64 = "data:image/jpeg;base64," + base64.b64encode(raw).decode()
print(f"[OK] 압축 완료  {w}×{h}px  {len(raw)//1024}KB → base64 {len(b64)//1024}KB")

# 3) Firebase 업로드
print("Firebase 업로드 중...")
try:
    upload(b64)
    print("\n[OK] 업로드 성공!")
    print("   앱을 새로고침하면 메인 화면에 레이아웃이 표시됩니다.")
except Exception as e:
    print(f"\n[X] 업로드 실패: {e}")

input("\n엔터를 누르면 종료합니다...")
