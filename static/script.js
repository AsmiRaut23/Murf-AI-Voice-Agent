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

//         .catch(err => {
//           console.error(err);
//           addMsg('ai', "I'm having trouble connecting right now.");
//           setStatus('Trouble connecting', true);
//         });
//     }




// console.log("✅ script.js loaded");

// // =========================
// // Global variables
// // =========================
// const micBtn = document.getElementById("mic-btn");
// const modal = document.getElementById("settingsModal");
// const btn = document.getElementById("settingsBtn");
// const span = document.getElementById("closeModal");

// let socket = null;            // WebSocket connection
// let mediaRecorder = null;     // Browser media recorder for mic
// let isRecording = false;      // Mic state
// let murfChunks = [];          // Buffer for TTS audio chunks
// let turnIndex = 1;            // Current dialogue turn
// let chunkCount = 0;           // Count of Murf chunks received

// // 🎵 Background music element
// const bgMusic = new Audio("/static/a-pirate-343849.mp3");
// bgMusic.loop = true;
// bgMusic.volume = 0.1;
// bgMusic.preload = "auto";

// // =========================
// // WebSocket setup
// // =========================
// window.addEventListener("load", () => {
//   const protocol = window.location.protocol === "https:" ? "wss" : "ws";
//   socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

//   socket.onopen = () => console.log("🔌 WebSocket OPEN (page load)");
//   socket.onclose = () => console.log("🔌 WebSocket CLOSED");

//   socket.onmessage = (event) => {
//     let data;
//     try {
//       data = JSON.parse(event.data);
//       console.log("📩 Got message:", data);
//     } catch (e) {
//       console.error("⚠ Bad WS message:", event.data);
//       return;
//     }

//     if (data.transcript !== undefined && data.end_of_turn) {
//       appendMessage("You", data.transcript);
//     } else if (data.type === "gemini_response" && data.text) {
//       appendMessage("Captain", data.text);
//     } else if (data.type === "murf_audio") {
//       murfChunks.push(data.audio);
//       console.log(`🎵 Received audio chunk for turn ${turnIndex}`);
//       ++chunkCount;
//     } else if (data.type === "murf_audio_end") {
//       playMurfAudioFromChunks();
//     } else {
//       console.log("ℹ Unknown WS message:", data);
//     }
//   };
// });

// // =========================
// // Modal logic
// // =========================
// btn.onclick = () => (modal.style.display = "block");
// span.onclick = () => (modal.style.display = "none");
// window.onclick = (event) => {
//   if (event.target === modal) modal.style.display = "none";
// };

// document.getElementById("apiKeyForm").addEventListener("submit", async (e) => {
//   e.preventDefault();
//   const formData = new FormData(e.target);
//   const keys = {};
//   formData.forEach((value, key) => (keys[key] = value));

//   const res = await fetch("/save_keys", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify(keys),
//   });

//   const data = await res.json();
//   console.log("✅ /save_keys response:", data);
//   alert(data.message || "Keys saved successfully!");
//   modal.style.display = "none";
// });

// // =========================
// // Chat message rendering
// // =========================
// function appendMessage(who, text) {
//   const chat = document.getElementById("chat");
//   const div = document.createElement("div");
//   div.className = who === "You" ? "msg you" : "msg ai";

//   const label = document.createElement("div");
//   label.className = "label";
//   label.innerText = who + ":";

//   const body = document.createElement("div");
//   body.innerText = text;

//   div.appendChild(label);
//   div.appendChild(body);
//   chat.appendChild(div);
//   chat.scrollTop = chat.scrollHeight;
// }

// // =========================
// // Murf audio handling
// // =========================
// async function playMurfAudioFromChunks() {
//   if (murfChunks.length === 0) return;

//   const arrays = murfChunks.map((b64) => {
//     const raw = atob(b64);
//     const arr = new Uint8Array(raw.length);
//     for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
//     return arr;
//   });

//   murfChunks = [];

//   const blob = new Blob(arrays, { type: "audio/mpeg" });
//   const url = URL.createObjectURL(blob);

//   const audio = new Audio(url);
//   audio.oncanplaythrough = () => audio.play();
//   audio.onended = () => URL.revokeObjectURL(url);
// }

// // =========================
// // Mic button handling
// // =========================
// micBtn.onclick = async () => {
//   // ✅ Step 1: Check API keys
//   const murfKey = document.querySelector("input[name='MURF_KEY']").value.trim();
//   const geminiKey = document.querySelector("input[name='GEMINI_KEY']").value.trim();
//   const assemblyKey = document.querySelector("input[name='ASSEMBLY_KEY']").value.trim();

//   if (!murfKey || !geminiKey || !assemblyKey) {
//     alert("⚠️ Please fill in all required API keys before using the mic.");
//     return;
//   }

//   // ✅ Step 2: Toggle mic
//   if (!isRecording) {
//     try {
//       // Stop previous recorder if active
//       if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
//       if (socket && socket.readyState === WebSocket.OPEN) {
//         socket.send(JSON.stringify({ type: "end_of_audio" }));
//       }

//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//       console.log("🎤 Microphone access granted");

//       mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

//       mediaRecorder.onstart = () => {
//         console.log("▶️ Recording started");
//         if (socket && socket.readyState === WebSocket.OPEN) {
//           socket.send(JSON.stringify({ type: "start_recording" })); // ✅ notify server
//         }
//       };
//       mediaRecorder.onstop = () => {
//         console.log("⏹️ Recording stopped");
//         if (socket && socket.readyState === WebSocket.OPEN) {
//           socket.send(JSON.stringify({ type: "stop_recording" })); // ✅ notify server
//         }
//       };

//       mediaRecorder.ondataavailable = (e) => {
//         if (e.data.size > 0 && socket && socket.readyState === WebSocket.OPEN) {
//           e.data.arrayBuffer().then((buf) => {
//             const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
//             socket.send(JSON.stringify({ type: "audio_chunk", data: b64 }));
//           });
//         }
//       };

//       mediaRecorder.start(250);
//       micBtn.classList.add("active");
//       isRecording = true;

//       // 🎵 Start background music
//       bgMusic.play().catch(err => console.log("⚠️ Music play blocked:", err));

//     } catch (e) {
//       console.log("❌ Mic error: " + e.message);
//     }
//   } else {
//     // Stop recording
//     if (mediaRecorder && mediaRecorder.state !== "inactive") {
//       mediaRecorder.stop();
//       if (socket && socket.readyState === WebSocket.OPEN) {
//         socket.send(JSON.stringify({ type: "end_of_audio" }));
//       }
//     }
//     micBtn.classList.remove("active");
//     isRecording = false;

//     // 🎵 Stop background music
//     bgMusic.pause();
//     bgMusic.currentTime = 0;
//   }
// };

// // =========================
// // Cleanup on page unload
// // =========================
// window.addEventListener("beforeunload", () => {
//   if (socket && socket.readyState === WebSocket.OPEN) {
//     socket.send(JSON.stringify({ type: "end_of_audio" }));
//     socket.close();
//   }
// });














// // console.log("✅ script.js loaded");

// // =========================
// // Global variables
// // =========================
// const micBtn = document.getElementById("mic-btn");
// const modal = document.getElementById("settingsModal");
// const btn = document.getElementById("settingsBtn");
// const span = document.getElementById("closeModal");

// let socket = null;
// let mediaRecorder = null;
// let isRecording = false;
// let murfChunks = []; // buffer all chunks until finished



// // 🎵 Background music element
// const bgMusic = new Audio("/static/a-pirate-343849.mp3");
// bgMusic.loop = true;
// bgMusic.volume = 0.1;
// bgMusic.preload = "auto";

// // =========================
// // WebSocket setup
// // =========================
// window.addEventListener("load", () => {
//   const protocol = window.location.protocol === "https:" ? "wss" : "ws";
//   socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

//   socket.onopen = () => console.log("🔌 WebSocket OPEN (page load)");
//   socket.onclose = () => console.log("🔌 WebSocket CLOSED");

//   socket.onmessage = (event) => {
//     let data;
//     try {
//       data = JSON.parse(event.data);
//       console.log("📩 Got message:", data);
//     } catch (e) {
//       console.error("⚠ Bad WS message:", event.data);
//       return;
//     }

//     // ✅ Handle message types from backend
//     if (data.type === "final_transcript") {
//       appendMessage("You", data.text);
//     } else if (data.type === "gemini_response") {
//       appendMessage("Captain", data.text);
//     } else if (data.type === "murf_audio") {
//       enqueueMurfChunk(data.audio); // play each chunk sequentially
//     } else if (data.type === "murf_audio_end") {
//       console.log("🎵 Murf audio stream finished");
//       // if (murfChunks.length > 0) {
//       //   const combinedB64 = murfChunks.join(""); // merge into 1 base64 string
//       //   playMurfAudioOnce(combinedB64);          // play as single audio
//       //   murfChunks = [];
//       // }
//     } else {
//     console.log("ℹ Unknown WS message:", data);
//     }
//   };
// });

// // =========================
// // Modal logic
// // =========================
// btn.onclick = () => (modal.style.display = "block");
// span.onclick = () => (modal.style.display = "none");
// window.onclick = (event) => {
//   if (event.target === modal) modal.style.display = "none";
// };

// document.getElementById("apiKeyForm").addEventListener("submit", async (e) => {
//   e.preventDefault();
//   const formData = new FormData(e.target);
//   const keys = {};
//   formData.forEach((value, key) => (keys[key] = value));

//   const res = await fetch("/save_keys", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify(keys),
//   });

//   const data = await res.json();
//   console.log("✅ /save_keys response:", data);
//   alert(data.message || "Keys saved successfully!");
//   modal.style.display = "none";
// });

// // =========================
// // Chat message rendering
// // =========================
// function appendMessage(who, text) {
//   const chat = document.getElementById("chat");
//   const div = document.createElement("div");
//   div.className = who === "You" ? "msg you" : "msg ai";

//   const label = document.createElement("div");
//   label.className = "label";
//   label.innerText = who + ":";

//   const body = document.createElement("div");
//   body.innerText = text;

//   div.appendChild(label);
//   div.appendChild(body);
//   chat.appendChild(div);
//   chat.scrollTop = chat.scrollHeight;
// }

// // =========================
// // Murf audio handling
// // =========================
// // =========================
// // Murf sequential audio playback
// // =========================
// let murfAudioQueue = [];
// let murfPlaying = false;

// function enqueueMurfChunk(base64Chunk) {
//   murfAudioQueue.push(base64Chunk);
//   if (!murfPlaying) playNextMurfChunk();
// }

// function playNextMurfChunk() {
//   if (murfAudioQueue.length === 0) {
//     murfPlaying = false;
//     return;
//   }

//   murfPlaying = true;
//   const chunk = murfAudioQueue.shift();

//   const raw = atob(chunk);
//   const arr = new Uint8Array(raw.length);
//   for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);

//   const blob = new Blob([arr], { type: "audio/mpeg" });
//   const url = URL.createObjectURL(blob);

//   const audio = new Audio(url);
//   audio.oncanplaythrough = () => audio.play();
//   audio.onended = () => {
//     URL.revokeObjectURL(url);
//     playNextMurfChunk();
//   };
// }




// // =========================
// // Mic button handling
// // =========================
// micBtn.onclick = async () => {
//   // ✅ Step 1: Check API keys
//   const murfKey = document.querySelector("input[name='MURF_KEY']").value.trim();
//   const geminiKey = document.querySelector("input[name='GEMINI_KEY']").value.trim();
//   const assemblyKey = document.querySelector("input[name='ASSEMBLY_KEY']").value.trim();

//   if (!murfKey || !geminiKey || !assemblyKey) {
//     alert("⚠️ Please fill in all required API keys before using the mic.");
//     return;
//   }

//   // ✅ Step 2: Toggle mic
//   if (!isRecording) {
//     try {
//       if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
//       if (socket && socket.readyState === WebSocket.OPEN) {
//         socket.send(JSON.stringify({ type: "end_of_audio" }));
//       }

//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//       console.log("🎤 Microphone access granted");

//       mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

//       mediaRecorder.onstart = () => {
//         console.log("▶️ Recording started");
//         if (socket && socket.readyState === WebSocket.OPEN) {
//           socket.send(JSON.stringify({ type: "start_recording" }));
//         }
//       };
//       mediaRecorder.onstop = () => {
//         console.log("⏹️ Recording stopped");
//         if (socket && socket.readyState === WebSocket.OPEN) {
//           socket.send(JSON.stringify({ type: "stop_recording" }));
//         }
//       };

//       mediaRecorder.ondataavailable = (e) => {
//         if (e.data.size > 0 && socket && socket.readyState === WebSocket.OPEN) {
//           e.data.arrayBuffer().then((buf) => {
//             const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
//             socket.send(JSON.stringify({ type: "audio_chunk", data: b64 }));
//           });
//         }
//       };

//       mediaRecorder.start(250);
//       micBtn.classList.add("active");
//       isRecording = true;

//       // 🎵 Start background music
//       bgMusic.play().catch(err => console.log("⚠️ Music play blocked:", err));

//     } catch (e) {
//       console.log("❌ Mic error: " + e.message);
//     }
//   } else {
//     if (mediaRecorder && mediaRecorder.state !== "inactive") {
//       mediaRecorder.stop();
//       if (socket && socket.readyState === WebSocket.OPEN) {
//         socket.send(JSON.stringify({ type: "end_of_audio" }));
//       }
//     }
//     micBtn.classList.remove("active");
//     isRecording = false;

//     // 🎵 Stop background music
//     bgMusic.pause();
//     bgMusic.currentTime = 0;
//   }
// };

// // =========================
// // Cleanup on page unload
// // =========================
// window.addEventListener("beforeunload", () => {
//   if (socket && socket.readyState === WebSocket.OPEN) {
//     socket.send(JSON.stringify({ type: "end_of_audio" }));
//     socket.close();
//   }
// });










// =========================
// Global variables
// =========================
const micBtn = document.getElementById("mic-btn");
const modal = document.getElementById("settingsModal");
const btn = document.getElementById("settingsBtn");
const span = document.getElementById("closeModal");

let socket = null;
let mediaRecorder = null;
let isRecording = false;
let murfChunks = []; // buffer Murf audio chunks
let audioContext = new (window.AudioContext || window.webkitAudioContext)();

// 🎵 Background music element
const bgMusic = new Audio("/static/a-pirate-343849.mp3");
bgMusic.loop = true;
bgMusic.volume = 0.1;
bgMusic.preload = "auto";

// =========================
// WebSocket setup
// =========================
window.addEventListener("load", () => {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

  socket.onopen = () => console.log("🔌 WebSocket OPEN (page load)");
  socket.onclose = () => console.log("🔌 WebSocket CLOSED");

  socket.onmessage = async (event) => {
    let data;
    try {
      data = JSON.parse(event.data);
      console.log("📩 Got message:", data);
    } catch (e) {
      console.error("⚠ Bad WS message:", event.data);
      return;
    }

    // ✅ Handle message types
    if (data.type === "final_transcript") {
      appendMessage("You", data.text);
    } else if (data.type === "gemini_response") {
      appendMessage("Captain", data.text);
    } else if (data.type === "murf_audio") {
      murfChunks.push(data.audio);
    } else if (data.type === "murf_audio_end") {
      if (murfChunks.length > 0) {
        playMurfChunksGapless(murfChunks);
        murfChunks = [];
      }
    } else {
      console.log("ℹ Unknown WS message:", data);
    }
  };
});

// =========================
// Modal logic
// =========================
btn.onclick = () => (modal.style.display = "block");
span.onclick = () => (modal.style.display = "none");
window.onclick = (event) => {
  if (event.target === modal) modal.style.display = "none";
};

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
  console.log("✅ /save_keys response:", data);
  alert(data.message || "Keys saved successfully!");
  modal.style.display = "none";
});

// =========================
// Chat message rendering
// =========================
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
// Gapless Murf audio playback
// =========================
async function playMurfChunksGapless(chunks) {
  let currentTime = audioContext.currentTime;

  for (let chunk of chunks) {
    const raw = atob(chunk);
    const arr = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);

    try {
      const audioBuffer = await audioContext.decodeAudioData(arr.buffer);
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);
      source.start(currentTime);
      currentTime += audioBuffer.duration;
    } catch (err) {
      console.error("⚠ Failed to decode Murf chunk:", err);
    }
  }
}

// =========================
// Mic button handling
// =========================
micBtn.onclick = async () => {
  const murfKey = document.querySelector("input[name='MURF_KEY']").value.trim();
  const geminiKey = document.querySelector("input[name='GEMINI_KEY']").value.trim();
  const assemblyKey = document.querySelector("input[name='ASSEMBLY_KEY']").value.trim();

  if (!murfKey || !geminiKey || !assemblyKey) {
    alert("⚠️ Please fill in all required API keys before using the mic.");
    return;
  }

  if (!isRecording) {
    try {
      if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "end_of_audio" }));
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log("🎤 Microphone access granted");

      mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

      mediaRecorder.onstart = () => {
        console.log("▶️ Recording started");
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: "start_recording" }));
        }
      };

      mediaRecorder.onstop = () => {
        console.log("⏹️ Recording stopped");
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: "stop_recording" }));
        }
      };

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0 && socket.readyState === WebSocket.OPEN) {
          e.data.arrayBuffer().then((buf) => {
            const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
            socket.send(JSON.stringify({ type: "audio_chunk", data: b64 }));
          });
        }
      };

      mediaRecorder.start(250);
      micBtn.classList.add("active");
      isRecording = true;

      bgMusic.play().catch(err => console.log("⚠️ Music play blocked:", err));
    } catch (err) {
      console.log("❌ Mic error:", err);
    }
  } else {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "end_of_audio" }));
      }
      // 🔥 Properly release the mic hardware
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      mediaRecorder = null;
    }
    
    micBtn.classList.remove("active");
    isRecording = false;
    bgMusic.pause();
    bgMusic.currentTime = 0;
  }
};

// =========================
// Cleanup on page unload
// =========================
window.addEventListener("beforeunload", () => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: "end_of_audio" }));
    socket.close();
  }
});
