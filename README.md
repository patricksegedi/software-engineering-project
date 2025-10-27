# 🧠 Software Engineering Project  
**Hanyang University** — for *Software Engineering* and *AI & Application* courses.

---

## 🛠️ Environment Setup

Follow these steps to set up your local development environment.

---

### 1. Clone the Repository
```bash
git clone https://github.com/patricksegedi/software-engineering-project.git
cd software-engineering-project
```

---

### 2. Set Up the Environment

You can use either **Conda** or **Python venv** to create your environment.

#### Option 1 — Conda
```bash
conda create -n SmarterSpeaker python=3.10 -y
conda activate SmarterSpeaker
```

#### Option 2 — venv (if you don’t use Conda)
```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# or (Windows):
# venv\Scripts\activate
```

---

### 3. Install Prerequisites (macOS only)
```bash
xcode-select --install        # Needed to compile some Python packages
brew install ffmpeg           # Required by faster-whisper for audio processing
```

Windows users should install **FFmpeg** manually and add it to PATH.

#### Windows
1. Go to the official FFmpeg website:  
   👉 https://ffmpeg.org/download.html  
2. Under **Windows**, click the link to **gyan.dev builds** (or another recommended source).  
3. Download the latest **full build ZIP** (e.g., `ffmpeg-release-full.zip`).  
4. Extract it to a folder, for example:  
   `C:\ffmpeg`  
5. Add `C:\ffmpeg\bin` to your **PATH** environment variable:  
   - Press **Win + S**, search for **“Edit the system environment variables”**.  
   - Click **Environment Variables** → under *System variables*, find `Path` → click **Edit**.  
   - Click **New**, and paste:  
     ```
     C:\ffmpeg\bin
     ```
   - Click **OK** to save and close all windows.  
6. Restart your terminal and test it by running:  
   ```bash
   ffmpeg -version
   ```
   If it prints FFmpeg version info — you’re done ✅.

---

### 4. Install Dependencies
```bash
# Install PyTorch (CPU version) — version 2.7.0 for compatibility
pip install "torch==2.7.0" "torchaudio==2.7.0" --index-url https://download.pytorch.org/whl/cpu

```

**Python packages used in this project:**
- **faster-whisper** – Speech-to-text transcription (optimized Whisper model)  
- **speechbrain** – Speaker verification and general speech processing  
- **sounddevice** – Records audio from the microphone  
- **wavio** – Saves recordings as `.wav` files  
- **soundfile** – Reads and writes audio files  
- **playsound** – Plays `.mp3` or `.wav` files  
- **webrtcvad** – Detects when someone is speaking (voice activity detection)  
- **pyttsx3** – Converts text to speech (TTS)  
- **numpy** – Numerical operations and array handling  

Install them all together:
```bash
pip install faster-whisper speechbrain sounddevice wavio webrtcvad pyttsx3 numpy soundfile playsound
```

---

### 5. Run the Project
```bash
python main.py
```