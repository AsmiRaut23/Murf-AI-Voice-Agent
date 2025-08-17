let mediaRecorder;
    let audioChunks = [];
    let recording = false;
    const sessionId = Date.now().toString();

    const recordBtn = document.getElementById('recordBtn');
    const statusEl = document.getElementById('status');
    const statusDot = document.getElementById('statusDot');
    const voiceSel = document.getElementById('voice');
    const chatBox = document.getElementById('chatBox');
    const responseAudio = document.getElementById('responseAudio');

    const setStatus = (msg, isError=false) => {
      statusEl.textContent = msg;
      statusEl.style.color = isError ? '#ff6b6b' : '#cfd8dc';
    };

    const addMsg = (who, text) => {
      if (!text) return;
      const div = document.createElement('div');
      div.className = who === 'user' ? 'bubble user' : 'bubble ai';
      div.textContent = (who === 'user' ? 'You: ' : 'Kampra AI: ') + text;
      chatBox.appendChild(div);
      chatBox.scrollTop = chatBox.scrollHeight;
    };

    // recordBtn.addEventListener('click', () => {
    //   if (!recording) startRecording();
    //   else stopRecording();
    // });

    recordBtn.addEventListener('click', () => {
  if (!recording) {
    startRecording();
    recordBtn.classList.add('recording'); // start animation
    console.log("Recording started");
  } else {
    stopRecording();
    recordBtn.classList.remove('recording'); // stop animation
    console.log("Recording stopped");
  }
});


    function startRecording() {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          mediaRecorder = new MediaRecorder(stream);
          audioChunks = [];
          mediaRecorder.ondataavailable = e => { if (e.data.size) audioChunks.push(e.data); };
          mediaRecorder.onstop = onStopped;
          mediaRecorder.start();

          recording = true;
          recordBtn.classList.add('recording');
          statusDot.classList.add('on');
          setStatus('Listening…');
        })
        .catch(err => {
          console.error('Mic error:', err);
          setStatus('Microphone access denied', true);
        });
    }

    function stopRecording() {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        recording = false;
        recordBtn.classList.remove('recording');
        statusDot.classList.remove('on');
        setStatus('Processing…');
      }
    }

    function onStopped() {
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      const form = new FormData();
      form.append('audio', blob, 'input.webm');
      form.append('voice_id', voiceSel.value);

fetch(`/agent/chat/${sessionId}`, { method: 'POST', body: form })

        .then(async res => {
          console.log("Response status:", res.status);
          console.log("Headers:", [...res.headers.entries()]);

          const transcript = res.headers.get('X-Transcript') || '';
          const reply = res.headers.get('X-Reply') || '';
          console.log("Transcript:", transcript);
          console.log("Reply:", reply);

          if (transcript) addMsg('user', transcript);
          if (reply) addMsg('ai', reply);

          if (!res.ok) throw new Error('Server error');

          const audioBlob = await res.blob();
          const url = URL.createObjectURL(audioBlob);
          responseAudio.src = url;
          responseAudio.play();

          setStatus('Ready');
        })




        









        .catch(err => {
          console.error(err);
          addMsg('ai', "I'm having trouble connecting right now.");
          setStatus('Trouble connecting', true);
        });
    }
