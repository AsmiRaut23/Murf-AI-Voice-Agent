# 🎙 Murf AI Voice Agent Challenge 
# Kampra AI 


**Kampra AI** is an interactive voice-based conversational agent built using **Murf AI**, **Gemini API**, and **AssemblyAI**, powered by a Flask backend and a sleek web UI.
It listens to your voice, understands your intent, and responds back with natural, human-like speech — all in real time.

---

## 📌 Features


🎤 **Speech-to-Text (STT)**: Converts your speech into text using **AssemblyAI**

🤖 **AI-Powered Conversations**: Generates smart, context-aware responses via **Google Gemini API**

🗣 **Text-to-Speech (TTS)**: Speaks responses aloud using **Murf AI’s high-quality voices**

🎨 **Premium UI**: Clean, responsive interface with animated record button

🔄 **Seamless Flow**: Automatic audio playback without needing manual clicks

⚡ **Single Dynamic Button**: **Start/stop** recording with one button that updates in real time

---

## 🏗 Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **APIs**:
  - Murf AI (Text-to-Speech)
  - AssemblyAI (Speech-to-Text)
  - Google Gemini (LLM for conversation)

---

## 🖼 Architecture Overview

**User speaks** → Audio recorded in browser

**Speech-to-Text (STT)** → Sent to AssemblyAI for transcription

**AI Response** → Gemini API processes transcription and generates a reply

**Text-to-Speech (TTS)** → Murf AI converts reply into speech

**Audio Playback** → Plays automatically in the browser


---

## 📸 Screenshots
  ![alt text](image.png)
- 🚀 Now the voice agent **feels like a real app**, not just a prototype



---

## API Keys

Create a .env file in the project root and set the following:


```env
MURF_API_KEY = your_murf_api_key
ASSEMBLYAI_API_KEY = your_assemblyai_api_key
GEMINI_API_KEY = your_gemini_api_key
```

---


## ⚙️ Setup & Installation


1️⃣ Clone the Repository
```
git clone https://github.com/AsmiRaut23/Murf-AI-Voice-Agent.git
cd Murf-AI-Voice-Agent
```


2️⃣ Create and activate virtual environment
Windows
```
python -m venv .venv
.venv\Scripts\activate
```


4️⃣ Install Dependencies


```
pip install -r requirements.txt
```



5️⃣ Run the Flask Server


```
python app.py
```
Server will start at: http://127.0.0.1:5000

---



## 🙌 Special Thanks

A heartfelt thank you to **Murf AI** for hosting this incredible challenge and inspiring creators to dive into the world of voice-first interfaces.
Your tools are empowering the next generation of interactive agents 


