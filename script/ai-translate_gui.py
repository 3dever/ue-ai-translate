import os
import time
import asyncio
from pathlib import Path
from tkinter import Tk, ttk, StringVar, messagebox, Label, Button, Entry, Checkbutton, BooleanVar, Text
from openai import OpenAI
import polib
from dotenv import load_dotenv
from datetime import datetime

# BASE PATH
BASE_DIR = Path(__file__).parent.resolve()
env_path = BASE_DIR / "ai_translate.key"

# LOAD .env
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)

# VARIABLES
DEFAULT_MODEL = "gpt-4o-mini"
MODEL_OPTIONS = ["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini"]
REQUEST_DELAY = 1.0
categories = [f.name for f in BASE_DIR.iterdir() if f.is_dir() and any((f / x).is_dir() for x in os.listdir(f))]

# GUI INIT
root = Tk()
root.title("PO AI Translate")
root.geometry("600x400")
root.resizable(False, False)
root.eval('tk::PlaceWindow . center')

selected_category = StringVar()
selected_file = StringVar()
file_info = StringVar()
api_key = StringVar(value=os.getenv("OPENAI_API_KEY") or "")
batch_size_var = StringVar(value="100")
selected_model = StringVar(value=DEFAULT_MODEL)
translate_all_langs = BooleanVar(value=False)

# GUI CALLBACKS
def update_file_list(*args):
    cat = selected_category.get()
    files = []
    if cat:
        category_path = BASE_DIR / cat
        for lang_dir in category_path.iterdir():
            if lang_dir.is_dir():
                for file in lang_dir.glob("*.po"):
                    rel_path = file.relative_to(BASE_DIR)
                    files.append(str(rel_path))
    file_combo['values'] = files
    if files:
        selected_file.set(files[0])
        update_file_info()

def update_file_info(*args):
    po_path = BASE_DIR / selected_file.get()
    if po_path.exists():
        size_kb = round(po_path.stat().st_size / 1024, 1)
        mod_time = datetime.fromtimestamp(po_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        file_info.set(f"{po_path.name} ({size_kb} KB, modified {mod_time})")
    else:
        file_info.set("")

def on_confirm():
    key = api_key.get().strip()
    if not key.startswith("sk-"):
        messagebox.showerror("Error", "Invalid or missing OpenAI API key.")
        return

    try:
        client = OpenAI(api_key=key)
        _ = client.models.list()
    except Exception as e:
        messagebox.showerror("API Error", f"API Key check failed: {e}")
        return

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"OPENAI_API_KEY={key}\n")

    try:
        batch_size = int(batch_size_var.get())
        if batch_size <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Batch size must be a positive integer.")
        return

    root.destroy()
    asyncio.run(start_translation(key, batch_size, selected_model.get()))

async def start_translation(api_key_value, batch_size, model):
    client = OpenAI(api_key=api_key_value)
    files = []

    if translate_all_langs.get():
        cat_path = BASE_DIR / selected_category.get()
        for lang_dir in cat_path.iterdir():
            if lang_dir.is_dir() and lang_dir.name.lower() != "en":
                for po_file in lang_dir.glob("*.po"):
                    files.append(po_file)
    else:
        files.append(BASE_DIR / selected_file.get())

    total_requests = 0
    stats = []

    progress = Tk()
    progress.title("Translation in Progress")
    progress.geometry("700x340")
    progress.eval('tk::PlaceWindow . center')
    progress_box = Text(progress, height=17, width=90, wrap="word")
    progress_box.pack(padx=10, pady=10)

    def plog(m):
        progress_box.insert("end", m + "\n")
        progress_box.see("end")
        progress_box.update()

    for po_path in files:
        lang_code = po_path.parent.name
        po = polib.pofile(str(po_path))
        untranslated_entries = [e for e in po if not e.translated() and e.msgid.strip() and not e.msgstr.strip()]
        total = len(untranslated_entries)
        translated = 0
        errors = 0

        rel_path = po_path.relative_to(BASE_DIR)
        plog(f"\nTranslating: {rel_path} → {lang_code} using model {model} ({total} entries)")

        for i in range(0, total, batch_size):
            batch = untranslated_entries[i:i+batch_size]
            prompts = [f"{idx+1}. {entry.msgid}" for idx, entry in enumerate(batch)]
            prompt = (
                f"Translate ONLY the following English phrases to {lang_code}.\n"
                f"Respond with EXACTLY one numbered translation per line, without any introduction, notes, or comments.\n"
                f"Keep the order. Start each line with its number and a dot, like '1. ...'\n\n"
                + "\n".join(prompts)
            )

            try:
                response = await asyncio.to_thread(
                    client.chat.completions.create,
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                total_requests += 1
                lines = response.choices[0].message.content.strip().splitlines()

                filtered_lines = [line for line in lines if line.strip().split(".", 1)[0].isdigit()]
                if not filtered_lines:
                    lines = [line for line in lines if ". " in line][:len(batch)]
                else:
                    lines = filtered_lines[:len(batch)]

                for entry, line in zip(batch, lines):
                    translated_text = line.split(". ", 1)[-1].strip()
                    if not entry.msgstr.strip():
                        entry.msgstr = translated_text
                        translated += 1
            except Exception as e:
                for entry in batch:
                    if not entry.msgstr.strip():
                        entry.msgstr = f"[ERROR: {e}]"
                        errors += 1
                plog(f"Error in batch starting at {i+1}: {e}")

            plog(f"Translated entries {i+1} to {min(i+batch_size, total)}")
            await asyncio.sleep(REQUEST_DELAY)

        if translated > 0 or errors > 0:
            out_path = po_path.with_name(f"{po_path.stem}.po")
            po.wrapwidth = 0
            po.save(str(out_path))
            plog(f"Saved as {out_path.name} ({translated} translated, {errors} errors, {total - translated - errors} skipped)")
        else:
            plog(f"No changes made to {rel_path} (all entries already translated)")

        stats.append((rel_path, translated, errors, total - translated - errors))

    plog("\n=== Summary ===")
    for name, tr, er, sk in stats:
        plog(f"{name}: {tr} translated, {er} errors, {sk} skipped")
    plog(f"Total OpenAI requests: {total_requests}")

    Button(progress, text="Close", command=progress.destroy).pack(pady=10)
    progress.mainloop()

# GUI LAYOUT
Label(root, text="OpenAI API Key:").pack(pady=(8, 0))
Entry(root, textvariable=api_key, width=70).pack()

Label(root, text="Model:").pack(pady=(8, 0))
model_combo = ttk.Combobox(root, values=MODEL_OPTIONS, textvariable=selected_model, state="readonly", width=40)
model_combo.pack()

Label(root, text="Select Category:").pack(pady=(12, 0))
cat_combo = ttk.Combobox(root, values=categories, textvariable=selected_category, state="readonly", width=60)
cat_combo.pack()

Checkbutton(root, text="Translate all languages in this category (except English)", variable=translate_all_langs).pack(pady=(6, 0))

Label(root, text="Select PO File:").pack(pady=(10, 0))
file_combo = ttk.Combobox(root, values=[], textvariable=selected_file, state="readonly", width=60)
file_combo.pack()

Label(root, textvariable=file_info, foreground="gray").pack(pady=(2, 0))

Label(root, text="Batch Size (number of entries per request):").pack(pady=(12, 0))
Entry(root, textvariable=batch_size_var, width=10).pack()

Button(root, text="Start Translation", command=on_confirm).pack(pady=12)

selected_category.trace_add("write", update_file_list)
selected_file.trace_add("write", update_file_info)

def toggle_file_selection(*args):
    file_combo.configure(state="disabled" if translate_all_langs.get() else "readonly")

translate_all_langs.trace_add("write", toggle_file_selection)

root.mainloop()
