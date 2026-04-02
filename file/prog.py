import json
import hashlib
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

WORDS_FILE = "data/words.json"
INDEX_FILE = "index.json"

entries = []

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calc_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def add_row():
    frame = tk.Frame(rows_container)
    frame.pack(pady=5)

    ko_entry = tk.Entry(frame, width=20)
    ko_entry.pack(side="left", padx=5)

    de_entry = tk.Entry(frame, width=20)
    de_entry.pack(side="left", padx=5)

    btn = tk.Button(frame, text="다음", command=add_row)
    btn.pack(side="left", padx=5)

    entries.append((ko_entry, de_entry))

def upload():
    filename = filename_entry.get().strip()

    if not filename:
        messagebox.showwarning("경고", "파일명 입력 필요")
        return

    filepath = f"data/{filename}.json"

    new_data = []
    for ko_entry, de_entry in entries:
        ko = ko_entry.get().strip()
        de = de_entry.get().strip()
        if ko and de:
            new_data.append({"ko": ko, "de": de})

    if not new_data:
        messagebox.showwarning("경고", "유효한 입력 없음")
        return

    # 기존 파일 로드 (없으면 새로 생성)
    words = load_json(filepath, [])
    words.extend(new_data)
    save_json(filepath, words)

    # hash 갱신
    index = load_json(INDEX_FILE, {})
    new_hash = calc_hash(filepath)

    index[f"{filename}.json"] = {
        "hash": new_hash,
        "updated": datetime.now().isoformat()
    }

    save_json(INDEX_FILE, index)

    # git push
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "auto"])
    subprocess.run(["git", "push"])

    messagebox.showinfo("완료", "업로드 완료")

# ===== GUI =====
root = tk.Tk()
root.title("Word Uploader")

# 🔹 상단 고정 영역
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

filename_entry = tk.Entry(top_frame, width=20)
filename_entry.pack(side="left", padx=5)
filename_entry.insert(0, "words")  # 기본값

upload_btn = tk.Button(top_frame, text="업로드", command=upload)
upload_btn.pack(side="left", padx=5)

# 🔹 입력 rows 영역
rows_container = tk.Frame(root)
rows_container.pack(pady=10)

add_row()

root.mainloop()
