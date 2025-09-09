# 🎙 Kampra AI – Murf AI Voice Agent Challenge

*Kampra AI* is an interactive, voice-based conversational agent built using *Murf AI, **Gemini API, and **AssemblyAI*, powered by a Flask backend and a sleek web UI.  
It listens to your voice, understands your intent, and responds back with natural, human-like speech — all in real time.

---

## 📌 Key Highlights

- 🎤 *Speech-to-Text (STT): Converts speech into text via **AssemblyAI*  
- 🤖 *AI-Powered Conversations: Context-aware responses with **Google Gemini*  
- 🗣 *Text-to-Speech (TTS): Speaks responses aloud using **Murf AI* voices  
- 🎨 *Premium UI*: Clean, responsive interface with animated mic button  
- ⚡ *One-Tap Control*: Start/stop recording with a single button  
- 🔄 *Seamless Flow*: Automatic voice playback — no clicks needed  
- 🎭 *Pirate Persona*: AI replies role-played as a Pirate Captain 🏴‍☠  

---

## 🧠 Special Skills (Beyond Voice & Chat)

### 🌙 Moon Tracking (via IP Geolocation API)
- Auto-detects user location (no manual input needed)  
- Provides:  
  - Moon’s altitude (height in the sky)  
  - Azimuth (direction in degrees + compass point)  
  - Rise & set times for the day  
  - Phase & distance from Earth  
- Example:  
  > “The moon is 287° toward the West, 45° above the horizon.”

### ⛅ Weather Forecast (via OpenWeather API)
- Real-time city-based weather forecasts  
- Example:  
  > “What’s the weather in Paris?”  
- Responds with:  
  - Temperature 🌡  
  - Conditions (clear, cloudy, rain, etc.)  
  - Local forecast details  

### 🔮 Horoscope Reader (via API Ninjas)
- Daily zodiac readings for all 12 signs  
- Example:  
  > “Tell me today’s horoscope for Leo”  
- Delivered in Pirate persona ⚓ with Murf TTS voice 🎶  
- Example Output:  
  > “Arrr! Fer Leo, today it be sayin’: Beware the tides of fortune…”

---

## 🏗 Technology Stack

- *Frontend*: HTML, CSS, JavaScript  
- *Backend*: Python (Flask)  
- *APIs Used*:  
  - 🎤 AssemblyAI → Speech-to-Text  
  - 🗣 Murf AI → Text-to-Speech  
  - 🤖 Google Gemini → AI-powered responses  
  - ⛅ OpenWeatherMap → Real-time weather data  
  - 🌙 IP Geolocation → Moon position & astronomy data  
  - 🔮 API Ninjas → Daily horoscopes  

---

## 🖼 Architecture Overview

*User Interaction* → Audio input recorded in browser  

*Speech-to-Text (STT)* → Audio sent to *AssemblyAI* for transcription  

*AI Processing (LLM)* → Transcribed text sent to *Google Gemini* for context-aware response  

*Special Skills Handling* → Depending on user query:
- *Weather Forecast* → Query sent to *OpenWeather API* for city-based weather
- *Moon Position* → Query sent to *IP Geolocation API* for moon altitude, azimuth, rise/set, phase, distance
- *Horoscope Reader* → Query sent to *API Ninjas* for daily zodiac reading

*Text-to-Speech (TTS)* → Response text (from Gemini or skills) converted to speech via *Murf AI*  

*Audio Playback* → Plays automatically in the browser  

*Session & Memory* → Chat history stored using session_id for contextual AI conversations  

*UI & Controls* → Single dynamic button for start/stop recording, settings modal for API keys  

---

## 📂 Project Structure


├── Murf-AI-Voice-Agent
│
├── app.py                  # Flask entry point
├── 📂services/
│   ├── __init__.py
│   ├── stt_service.py      # STT (AssemblyAI)
│   ├── tts_service.py      # TTS (Murf AI)
│   ├── gemini_service.py      # Gemini integration
│   ├── weather_service.py  # Weather API integration
│   ├── moon_service.py     # Moon/Astronomy API
│   └── horoscope_service.py# Horoscope API
│
├── 📂models/
│   ├── __init__.py
│   └── schemas.py   # Pydantic schemas for request/response
│
├── 📂utils/
│   ├── logger.py           # Logging configuration
│   └── __init__.py
│
├── 📂templates/
│   └── index.html          # Main UI
│
├── 📂static/
│   ├── script.js           # Frontend logic
│   ├── style.css           # Styling
│   └── mic.png
│
├── config.json             # Stores API keys after user input
├── requirements.txt        # Dependencies
└── README.md               # Project documentation


---

## 🔑 API Key Handling

Kampra AI requires *6 API keys* for full functionality:

| Service | Key Name | Provider |
|---------|----------|----------|
| Murf AI (TTS) | MURF_KEY | [murf.ai](https://murf.ai/) |
| AssemblyAI (STT) | ASSEMBLY_KEY | [assemblyai.com](https://www.assemblyai.com/) |
| Gemini (LLM) | GEMINI_KEY | [aistudio.google.com](https://aistudio.google.com/) |
| Weather API | WEATHER_KEY | [openweathermap.org](https://openweathermap.org) |
| Moon Tracking | MOON_KEY | [ipgeolocation.io](https://ipgeolocation.io) |
| Horoscope API | HOROSCOPE_KEY | [api-ninjas.com](https://www.api-ninjas.com/) |

*How Keys Are Used*  
- *First Run*: User fills them in via Settings modal in the UI  
- *Save*: Keys are written to config.json  
- *Subsequent Runs*: Keys auto-load into the UI from config.json  
- *No config.json Present*: Treated as first-time user → must input keys  

---

## ⚙ Setup & Installation

1️⃣ *Clone the Repository*

bash
git clone https://github.com/AsmiRaut23/Murf-AI-Voice-Agent.git
cd Murf-AI-Voice-Agent







2️⃣ Create & Activate Virtual Environment (Windows example)

python -m venv .venv
.venv\Scripts\activate


3️⃣ Install Dependencies

pip install -r requirements.txt


4️⃣ Run the Flask Server

python app.py


Server will start at: http://127.0.0.1:5000
## 🎤 Demo Usage (Try Asking These!)

You can interact with *Kampra AI* by voice or text. Here are some examples:

*General Chat (Gemini LLM):*
- “Tell me a pirate joke.”
- “What is AI?”

*Weather (OpenWeather API):*
- “What’s the weather in Germany?”
- “what is the temperature in Bhutan?”

*Moon Position (IP Geolocation API):*
- “Where is the moon right now?”
- “What direction is the moon from my location?”

*Horoscope (API Ninjas):*
- “Tell me today’s horoscope for Leo.”
- “What’s my Aries horoscope?”

*Persona Roleplay (Pirate Mode):*
- “Arrr! Tell me the weather in London!”
- “Captain, where be the moon tonight?”

---

## 🙌 Appreciation

A big thank you to *Murf AI* for organizing this inspiring challenge and empowering creators to dive into the world of voice-first interfaces. Your innovative tools are driving the future of interactive AI agents — truly appreciated!  


🔥 With voice, skills, and persona combined, *Kampra AI* has evolved into a multi-skilled voice-first assistant — not just a prototype, but a fully functional app!