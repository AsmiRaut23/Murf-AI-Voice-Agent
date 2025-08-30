// let mediaRecorder;
//     let audioChunks = [];
//     let recording = false;
//     const sessionId = Date.now().toString();

//     const recordBtn = document.getElementById('recordBtn');
//     const statusEl = document.getElementById('status');
//     const statusDot = document.getElementById('statusDot');
//     const voiceSel = document.getElementById('voice');
//     const chatBox = document.getElementById('chatBox');
//     const responseAudio = document.getElementById('responseAudio');

//     const setStatus = (msg, isError=false) => {
//       statusEl.textContent = msg;
//       statusEl.style.color = isError ? '#ff6b6b' : '#cfd8dc';
//     };

//     const addMsg = (who, text) => {
//       if (!text) return;
//       const div = document.createElement('div');
//       div.className = who === 'user' ? 'bubble user' : 'bubble ai';
//       div.textContent = (who === 'user' ? 'You: ' : 'Kampra AI: ') + text;
//       chatBox.appendChild(div);
//       chatBox.scrollTop = chatBox.scrollHeight;
//     };

//     // recordBtn.addEventListener('click', () => {
//     //   if (!recording) startRecording();
//     //   else stopRecording();
//     // });

//     recordBtn.addEventListener('click', () => {
//   if (!recording) {
//     startRecording();
//     recordBtn.classList.add('recording'); // start animation
//     console.log("Recording started");
//   } else {
//     stopRecording();
//     recordBtn.classList.remove('recording'); // stop animation
//     console.log("Recording stopped");
//   }
// });


//     function startRecording() {
//       navigator.mediaDevices.getUserMedia({ audio: true })
//         .then(stream => {
//           mediaRecorder = new MediaRecorder(stream);
//           audioChunks = [];
//           mediaRecorder.ondataavailable = e => { if (e.data.size) audioChunks.push(e.data); };
//           mediaRecorder.onstop = onStopped;
//           mediaRecorder.start();

//           recording = true;
//           recordBtn.classList.add('recording');
//           statusDot.classList.add('on');
//           setStatus('Listening…');
//         })
//         .catch(err => {
//           console.error('Mic error:', err);
//           setStatus('Microphone access denied', true);
//         });
//     }

//     function stopRecording() {
//       if (mediaRecorder && mediaRecorder.state !== 'inactive') {
//         mediaRecorder.stop();
//         recording = false;
//         recordBtn.classList.remove('recording');
//         statusDot.classList.remove('on');
//         setStatus('Processing…');
//       }
//     }

//     function onStopped() {
//       const blob = new Blob(audioChunks, { type: 'audio/webm' });
//       const form = new FormData();
//       form.append('audio', blob, 'input.webm');
//       form.append('voice_id', voiceSel.value);

// fetch(`/agent/chat/${sessionId}`, { method: 'POST', body: form })

//         .then(async res => {
//           console.log("Response status:", res.status);
//           console.log("Headers:", [...res.headers.entries()]);

//           const transcript = res.headers.get('X-Transcript') || '';
//           const reply = res.headers.get('X-Reply') || '';
//           console.log("Transcript:", transcript);
//           console.log("Reply:", reply);

//           if (transcript) addMsg('user', transcript);
//           if (reply) addMsg('ai', reply);

//           if (!res.ok) throw new Error('Server error');

//           const audioBlob = await res.blob();
//           const url = URL.createObjectURL(audioBlob);
//           responseAudio.src = url;
//           responseAudio.play();

//           setStatus('Ready');
//         })


    //     .catch(err => {
    //       console.error(err);
    //       addMsg('ai', "I'm having trouble connecting right now.");
    //       setStatus('Trouble connecting', true);
    //     });
    // }




        













console.log("✅ script.js loaded");
    // =========================
// Global variables
// =========================
const micBtn = document.getElementById("mic-btn");
const modal = document.getElementById("settingsModal");
const btn = document.getElementById("settingsBtn");
const span = document.getElementById("closeModal");

let socket = null;            // WebSocket connection
let mediaRecorder = null;     // Browser media recorder for mic
let isRecording = false;      // Mic state
let murfChunks = [];          // Buffer for TTS audio chunks
let turnIndex = 1;            // Current dialogue turn
let chunkCount = 0;           // Count of Murf chunks received

// =========================
// WebSocket setup
// =========================
window.addEventListener("load", () => {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

  socket.onopen = () => console.log("🔌 WebSocket OPEN (page load)");
  socket.onclose = () => console.log("🔌 WebSocket CLOSED");

  /**
   * Handle incoming WebSocket messages from backend
   * @param {MessageEvent} event
   */
  socket.onmessage = (event) => {
    let data;
    try {
      data = JSON.parse(event.data);
    } catch (e) {
      console.error("⚠ Bad WS message:", event.data);
      return;
    }

    // Handle transcript
    if (data.transcript !== undefined) {
      if (data.end_of_turn) appendMessage("You", data.transcript);
    }
    // Handle Gemini response
    else if (data.type === "gemini_response" && data.text) {
      appendMessage("Captain", data.text);
    }
    // Handle Murf audio chunks
    else if (data.type === "murf_audio") {
      murfChunks.push(data.audio);
      console.log(`🎵 Received audio chunk for turn ${turnIndex}`);
      ++chunkCount;
    }
    // Handle Murf audio completion
    else if (data.type === "murf_audio_end") {
      playMurfAudioFromChunks();
    }
    // Unknown message
    else {
      console.log("ℹ Unknown WS message:", data);
    }
  };
});

// =========================
// Modal logic
// =========================

// Open/close modal
btn.onclick = () => (modal.style.display = "block");
span.onclick = () => (modal.style.display = "none");
window.onclick = (event) => {
  if (event.target === modal) modal.style.display = "none";
};

/**
 * Handle API key form submission
 * Sends updated keys to backend via POST /save_keys
 */
document.getElementById("apiKeyForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const keys = {};
  formData.forEach((value, key) => (keys[key] = value));

  const res = await fetch("/save_keys", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(keys),
  });

  const data = await res.json();
  alert(data.message);
  modal.style.display = "none";
});

// =========================
// Chat message rendering
// =========================

/**
 * Append a chat message to UI
 * @param {string} who - "You" or "Captain"
 * @param {string} text - Message text
 */
function appendMessage(who, text) {
  const chat = document.getElementById("chat");
  const div = document.createElement("div");
  div.className = who === "You" ? "msg you" : "msg ai";

  const label = document.createElement("div");
  label.className = "label";
  label.innerText = who + ":";

  const body = document.createElement("div");
  body.innerText = text;

  div.appendChild(label);
  div.appendChild(body);
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

// =========================
// Murf audio handling
// =========================

/**
 * Combine buffered base64 audio chunks from Murf TTS
 * into a playable audio file, then play it.
 */
async function playMurfAudioFromChunks() {
  if (murfChunks.length === 0) return;

  // Convert each base64 chunk into a Uint8Array
  const arrays = murfChunks.map((b64) => {
    const raw = atob(b64);
    const arr = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
    return arr;
  });

  murfChunks = []; // reset buffer

  // Create a single audio Blob
  const blob = new Blob(arrays, { type: "audio/mpeg" });
  const url = URL.createObjectURL(blob);

  // Play the audio
  const audio = new Audio(url);
  audio.oncanplaythrough = () => audio.play();
  audio.onended = () => URL.revokeObjectURL(url);
}

// =========================
// Mic button handling
// =========================

/**
 * Handle mic button click
 * Starts/stops recording and streams audio to backend
 */
micBtn.onclick = async () => {
  if (!isRecording) {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log("🎤 Microphone access granted");

      mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      // mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.onstart = () => console.log("▶️ Recording started");
      mediaRecorder.onstop = () => console.log("⏹️ Recording stopped");
      /**
       * Send recorded audio chunks to backend via WebSocket
       */
      mediaRecorder.ondataavailable = (e) => {
        console.log("📦 Got audio chunk", e.data.size);
        if (e.data.size > 0 && socket && socket.readyState === WebSocket.OPEN) {
          e.data.arrayBuffer().then((buf) => {
            const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
            socket.send(JSON.stringify({ type: "audio_chunk", data: b64 }));
          });
        }
      };

      mediaRecorder.start(250); // record in 250ms chunks
      micBtn.classList.add("active");
      isRecording = true;
    } catch (e) {
      console.log("❌ Mic error: " + e.message);
    }
  } else {
    // Stop recording
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
      console.log("🛑 Recording stopped (sent final audio)");
    }
    micBtn.classList.remove("active");
    isRecording = false;
  }
};
