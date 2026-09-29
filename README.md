# 🪽 Hermes: The Real-Time Voice Proxy

**Hermes** is a bidirectional AI voice proxy that eliminates language barriers in remote IT meetings (Zoom, Teams, Google Meet, etc.). It intercepts system audio to generate real-time translated subtitles and transmits your translated voice back to the meeting using a virtual microphone.

Built by Team **Digueti** 🐙 for the **[AssemblyAI Voice Agent Hackathon](https://lablab.ai/)**.

![Hermes UI Preview](logo.png) *(Note: Add a screenshot of the UI here)*

---

## ✨ Features

*   **Real-Time Subtitles:** Transcribes incoming speech (e.g., from Zoom) and translates it to your native language in real-time.
*   **Bidirectional Voice Proxy:** Hold a button to speak in your native language. Hermes will transcribe, translate, and synthesize your voice into the target language, piping it directly back to the meeting via a Virtual Audio Cable.
*   **Multi-Language Support:** Easily switch the meeting's target language (English, French, German) from the UI dropdown.
*   **Full-Duplex Architecture:** Listen and speak simultaneously without audio collisions or UI freezing.
*   **Cyberpunk UI:** Built-in chat history log, device monitoring, and aesthetic visual feedback for AI processing states.

## 🏗️ Architecture & Technologies

*   **[AssemblyAI (Streaming API v3)](https://www.assemblyai.com/):** Powers the ultra-low latency real-time transcription of the incoming meeting audio, using automatic language detection.
*   **[AssemblyAI (Async/Sync API)](https://www.assemblyai.com/):** Transcribes the user's microphone input with high precision.
*   **[Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/):** Handles the lightning-fast, context-aware IT technical translations between languages.
*   **Edge-TTS:** Synthesizes natural-sounding neural voices with native accents for the translated output.
*   **PyAudioWPatch & Pygame:** Manages Windows WASAPI loopback capture and precise audio routing to Virtual Cables.
*   **Tkinter:** Lightweight, standalone Python GUI.

---

## 🚀 Setup & Installation

### 1. Prerequisites
*   Windows OS (Required for WASAPI Loopback).
*   Python 3.10+
*   [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) installed.

### 2. Audio Configuration
1.  Install **VB-Audio Virtual Cable**.
2.  In Zoom/Teams/Meet, set your **Microphone** to `CABLE Output (VB-Audio Virtual Cable)`.
3.  Set your **Speaker** to your normal headphones/speakers.

### 3. Clone and Install
```bash
git clone https://github.com/your-username/hermes-voice-proxy.git
cd hermes-voice-proxy
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root directory and add your API keys:
```env
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run the Application
```bash
python main_fase2.py
```

## 📦 Building the Executable

To compile Hermes into a single portable `.exe` file for distribution:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "logo.png;." --name "Hermes" main_fase2.py
```
The executable will be available in the `dist/` folder.

---
*Created with ❤️ by Digueti*
