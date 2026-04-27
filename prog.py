import json
import hashlib
import subprocess
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# =========================
# 설정
# =========================
NOTES_DIR = "./notes"
INDEX_FILE = "./index.json"

entries = []


# =========================
# 공통 함수
# =========================
def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def calc_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# =========================
# 입력 행 추가
# =========================
def add_row():
    frame = tk.Frame(rows_container)
    frame.pack(pady=4)

    ko_entry = tk.Entry(frame, width=28)
    ko_entry.pack(side="left", padx=5)

    de_entry = tk.Entry(frame, width=28)
    de_entry.pack(side="left", padx=5)

    btn = tk.Button(frame, text="다음", command=add_row)
    btn.pack(side="left", padx=5)

    entries.append((ko_entry, de_entry))


# =========================
# 업로드
# =========================
def upload():
    filename = filename_entry.get().strip()

    if not filename:
        messagebox.showwarning("경고", "파일명을 입력하세요.\n예: Gram/A1")
        return

    # 확장자 제거 방지
    if filename.endswith(".json"):
        filename = filename[:-5]

    filepath = f"{NOTES_DIR}/{filename}.json"

    # 폴더 자동 생성
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # 입력 수집
    new_data = []

    for ko_entry, de_entry in entries:
        ko = ko_entry.get().strip()
        de = de_entry.get().strip()

        if ko and de:
            new_data.append({
                "ko": ko,
                "de": de
            })

    if not new_data:
        messagebox.showwarning("경고", "유효한 입력이 없습니다.")
        return

    # 기존 파일 append
    words = load_json(filepath, [])
    words.extend(new_data)
    save_json(filepath, words)

    # index 갱신
    index = load_json(INDEX_FILE, {})

    rel_path = f"{filename}.json"

    index[rel_path] = {
        "hash": calc_hash(filepath),
        "updated": datetime.now().isoformat()
    }

    save_json(INDEX_FILE, index)

    # git push
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "auto"])
    subprocess.run(["git", "push"])

    messagebox.showinfo(
        "완료",
        f"업로드 완료\n{rel_path}"
    )

    # 입력창 초기화
    for ko_entry, de_entry in entries:
        ko_entry.delete(0, tk.END)
        de_entry.delete(0, tk.END)


# =========================
# GUI
# =========================
root = tk.Tk()
root.title("Deutsch Note Uploader")
root.geometry("760x600")

# 상단 바
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

filename_entry = tk.Entry(top_frame, width=32)
filename_entry.pack(side="left", padx=5)
filename_entry.insert(0, "Gram/A1")

upload_btn = tk.Button(
    top_frame,
    text="업로드",
    command=upload
)
upload_btn.pack(side="left", padx=5)

# 안내 문구
guide = tk.Label(
    root,
    text="파일명 예시: Gram/A1   Wort/Test   B1/Lesson3"
)
guide.pack(pady=5)

# 입력 영역
rows_container = tk.Frame(root)
rows_container.pack(pady=10)

# 첫 줄 생성
add_row()

root.mainloop()
