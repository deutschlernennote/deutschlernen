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
    frame = tk.Frame(root)
    frame.pack(pady=5)

    ko_entry = tk.Entry(frame, width=20)
    ko_entry.pack(side="left", padx=5)

    de_entry = tk.Entry(frame, width=20)
    de_entry.pack(side="left", padx=5)

    btn = tk.Button(frame, text="다음", command=add_row)
    btn.pack(side="left", padx=5)

    entries.append((ko_entry, de_entry))

def upload():
    new_data = []

    for ko_entry, de_entry in entries:
        ko = ko_entry.get().strip()
        de = de_entry.get().strip()

        if ko and de:
            new_data.append({"ko": ko, "de": de})

    if not new_data:
        messagebox.showwarning("경고", "유효한 입력이 없음")
        return

    # 기존 데이터 로드 (append)
    words = load_json(WORDS_FILE, [])
    words.extend(new_data)
    save_json(WORDS_FILE, words)

    # hash 갱신
    index = load_json(INDEX_FILE, {})
    new_hash = calc_hash(WORDS_FILE)

    index["words.json"] = {
        "hash": new_hash,
        "updated": datetime.now().isoformat()
    }

    save_json(INDEX_FILE, index)

    # git push
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "auto"])
    subprocess.run(["git", "push"])

    messagebox.showinfo("완료", "업로드 완료")

# GUI
root = tk.Tk()
root.title("Word Uploader")

add_row()

upload_btn = tk.Button(root, text="업로드", command=upload)
upload_btn.pack(pady=20)

root.mainloop()
