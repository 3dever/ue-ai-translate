# ue-ai-translate — OpenAI Translation Tool for Unreal Engine `.po` Files

A Python-based GUI tool for batch-translating Unreal Engine localization files (`.po`) using OpenAI's GPT models.

The provided `.bat` files are for **Windows**, but the Python script also works on **Linux** - just make sure all dependencies are installed.

![image](https://github.com/user-attachments/assets/2b2de679-55f6-48eb-9a08-40f8e835859a)


---

## 📁 Setup
![image](https://github.com/user-attachments/assets/8a63d777-1e29-4b78-8dc2-33c6cf75d358)

1. Download or clone this repository.
2. Place all files from **script** folder to your Unreal Engine localization folder (e.g., `Content/Localization`).
3. Run the setup script:

```bat
ai-translate_install.bat
```

This will:
- Install Python (if not already installed).
- Install required packages: `openai`, `polib`, `python-dotenv`.

If Python is already installed, you can launch directly using:

```bat
ai-translate.bat
```

For Linux:

Make sure that **tkinter** is installed
```install
sudo apt-get install python3-tk
```

---

## 🔑 Getting an OpenAI API Key

1. Log in or sign up to https://platform.openai.com/.
2. Add $ to your balance
3. Visit [OpenAI API Keys](https://platform.openai.com/account/api-keys).
4. Click **Create new secret key**.
5. Copy the key (starting with `sk-...`).
6. Paste it into the GUI when prompted.

Your key will be saved to a local `ai_translate.key` file (add it to git ignore files if you need to keep it privately in your repo).

---

## 🚀 How to Use

1. Enter your **OpenAI API key**.
2. Choose a **model** (`gpt-4o-mini`, `gpt-4`, `gpt-3.5-turbo`, etc.).
3. Select a **localization category** (e.g., `Game`).
4. Choose to:
   - Translate **all `.po` files** in that category (excluding English), **or**
   - Select a specific `.po` file.
5. Set the **batch size** (number of entries per GPT request).
6. Click **Start Translation**.

---

## 📊 Output & Logs

![image](https://github.com/user-attachments/assets/fed00989-f572-457c-9d39-d87bc6cbd4a8)
![image](https://github.com/user-attachments/assets/3304f916-5467-440a-9bcf-0b9ec095bfff)

- Only untranslated lines are modified.
- Process summary and OpenAI token usage are shown after completion.
- Translations are written back to the same `.po` file.

---

## 🛡️ Notes

- Supports `.po` format used by Unreal Engine.
- Designed to work inside `Content/Localization/YourProject` structure.
