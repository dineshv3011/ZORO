// ── ZORO Frontend JS ──────────────────────────────────────────────────────
// Connects browser voice recognition → Flask backend (brain.py + Groq)
// NO "I heard that" — straight to answering

const orb         = document.getElementById('orb');
const orbIcon     = document.getElementById('orbIcon');
const voiceBars   = document.getElementById('voiceBars');
const thinkDots   = document.getElementById('thinkDots');
const statusDot   = document.getElementById('statusDot');
const statusLabel = document.getElementById('statusLabel');
const statusHint  = document.getElementById('statusHint');
const statusCard  = document.getElementById('statusCard');
const zoroTitle   = document.getElementById('zoroTitle');
const zoroSub     = document.getElementById('zoroSub');
const bgGlow      = document.getElementById('bgGlow');
const orbWrapper  = document.querySelector('.orb-wrapper');
const transcriptBox = document.getElementById('transcriptBox');
const transcriptText = document.getElementById('transcriptText');
const convBody    = document.getElementById('convBody');
const modelName   = document.getElementById('modelName');

// ── State ────────────────────────────────────────────────────────────────
let isAwake     = false;
let isListening = false;
let isBusy      = false;   // true while thinking or speaking
let isSpeaking  = false;   // true only while TTS audio is playing
let micMuted    = false;   // mic paused during TTS to prevent echo
let recognition = null;
const synth     = window.speechSynthesis;

const WAKE_WORDS  = ['wake up', 'wakeup', 'hey zoro', 'hi zoro', 'zoro wake', 'wake'];
const SLEEP_WORDS = ['sleep', 'sleep zoro', 'go to sleep', 'goodbye', 'bye zoro', 'goodnight'];

// ── Particles (ambient) ──────────────────────────────────────────────────
function spawnParticles() {
  const container = document.getElementById('particles');
  for (let i = 0; i < 18; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left     = Math.random() * 100 + 'vw';
    p.style.animationDuration = (8 + Math.random() * 14) + 's';
    p.style.animationDelay   = (Math.random() * 12) + 's';
    p.style.opacity  = (Math.random() * .4 + .1).toString();
    container.appendChild(p);
  }
}

// ── UI State ─────────────────────────────────────────────────────────────
function applyState(state) {
  // Reset
  ['awake','think','speak'].forEach(c => {
    orb.classList.remove(c);
    statusDot.classList.remove(c);
    bgGlow.classList.remove(c);
    orbWrapper.classList.remove(c);
    statusCard.classList.remove(c);
    zoroTitle.classList.remove(c);
  });
  voiceBars.classList.remove('show');
  thinkDots.classList.remove('show');
  orbIcon.style.display = '';
  transcriptBox.classList.remove('active');

  switch(state) {
    case 'sleep':
      statusLabel.textContent = 'Sleeping';
      statusHint.textContent  = 'Say "Wake up" to activate';
      zoroSub.textContent     = 'Say "Wake up" to activate';
      transcriptText.textContent = 'Waiting for wake word...';
      break;

    case 'awake':
      ['awake'].forEach(c => {
        orb.classList.add(c); statusDot.classList.add(c);
        bgGlow.classList.add(c); orbWrapper.classList.add(c);
        statusCard.classList.add(c); zoroTitle.classList.add(c);
      });
      statusLabel.textContent = 'Awake';
      statusHint.textContent  = 'Listening for your command';
      zoroSub.textContent     = 'Listening — ask me anything';
      transcriptText.textContent = 'Speak your command...';
      transcriptBox.classList.add('active');
      break;

    case 'think':
      orb.classList.add('think'); statusDot.classList.add('think');
      bgGlow.classList.add('think'); statusCard.classList.add('think');
      zoroTitle.classList.add('think');
      thinkDots.classList.add('show');
      orbIcon.style.display = 'none';
      statusLabel.textContent = 'Thinking';
      statusHint.textContent  = 'Processing your request...';
      zoroSub.textContent     = 'Processing...';
      break;

    case 'speak':
      orb.classList.add('speak'); statusDot.classList.add('speak');
      bgGlow.classList.add('speak'); statusCard.classList.add('speak');
      zoroTitle.classList.add('speak');
      voiceBars.classList.add('show');
      orbIcon.style.display = 'none';
      statusLabel.textContent = 'Speaking';
      statusHint.textContent  = 'ZORO is responding...';
      zoroSub.textContent     = 'Speaking...';
      break;
  }
}

// ── Chat messages ────────────────────────────────────────────────────────
function addMsg(text, role) {
  const div = document.createElement('div');
  div.className = `msg ${role === 'user' ? 'user-msg' : 'zoro-msg'}`;
  if (role === 'zoro') {
    div.innerHTML = `<span class="msg-label">ZORO</span>${text}`;
  } else {
    div.textContent = text;
  }
  convBody.appendChild(div);
  convBody.scrollTop = convBody.scrollHeight;
}

function clearChat() {
  convBody.innerHTML = `
    <div class="msg zoro-msg">
      <span class="msg-label">ZORO</span>
      Conversation cleared. Say "Wake up" to start again.
    </div>`;
}

// ── Mic mute / unmute ────────────────────────────────────────────────────
function muteMic() {
  // Stop recognition so it cannot hear ZORO's voice
  if (recognition && !micMuted) {
    micMuted = true;
    isListening = false;
    try { recognition.stop(); } catch(e) {}
  }
}

function unmuteMic(delay = 900) {
  // Restart recognition after a short delay (lets speaker echo fade out)
  setTimeout(() => {
    micMuted    = false;
    isListening = true;
    try { recognition.start(); } catch(e) {}
  }, delay);
}

// ── Text-to-Speech ───────────────────────────────────────────────────────
function speak(text, onDone) {
  synth.cancel();

  // 🔇 Stop mic BEFORE speaking to prevent echo
  muteMic();

  const utter = new SpeechSynthesisUtterance(text);
  utter.rate   = 1.05;
  utter.pitch  = 1.0;
  utter.volume = 1.0;

  const voices = synth.getVoices();
  const pick = voices.find(v => v.name.includes('Google UK') || v.name.includes('Google US'))
            || voices.find(v => v.lang === 'en-US' || v.lang === 'en-GB')
            || voices[0];
  if (pick) utter.voice = pick;

  utter.onstart = () => {
    isBusy     = true;
    isSpeaking = true;
    applyState('speak');
  };

  utter.onend = () => {
    isBusy     = false;
    isSpeaking = false;
    applyState(isAwake ? 'awake' : 'sleep');
    // 🎤 Restart mic only AFTER speaking ends + extra delay
    unmuteMic(900);
    if (onDone) onDone();
  };

  utter.onerror = () => {
    isBusy     = false;
    isSpeaking = false;
    applyState(isAwake ? 'awake' : 'sleep');
    unmuteMic(900);
  };

  synth.speak(utter);
}

// ── Backend call ─────────────────────────────────────────────────────────
async function askZORO(text) {
  isBusy = true;
  applyState('think');

  try {
    const res  = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();

    if (data.error) {
      const err = 'Sorry, I ran into a problem. Please try again.';
      addMsg(err, 'zoro');
      speak(err);
      return;
    }

    addMsg(data.reply, 'zoro');
    speak(data.reply);

  } catch(e) {
    const err = 'Cannot reach the server. Make sure web_server.py is running.';
    addMsg(err, 'zoro');
    speak(err);
    console.error(e);
    isBusy = false;
    applyState(isAwake ? 'awake' : 'sleep');
  }
}

// ── Wake / Sleep ─────────────────────────────────────────────────────────
function wakeUp() {
  isAwake = true;
  applyState('awake');
  const greet = 'Hello! I am ZORO, your personal AI assistant. How can I help you today?';
  addMsg(greet, 'zoro');
  speak(greet);
}

function goSleep() {
  isAwake = false;
  const bye = 'Going to sleep. Say wake up whenever you need me.';
  addMsg(bye, 'zoro');
  speak(bye, () => applyState('sleep'));
}

// ── Speech Recognition ───────────────────────────────────────────────────
function startRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    addMsg('Voice recognition requires Google Chrome. Please open in Chrome!', 'zoro');
    return;
  }

  recognition = new SR();
  recognition.continuous     = true;
  recognition.interimResults = true;   // show live transcript
  recognition.lang           = 'en-US';

  recognition.onresult = (e) => {
    // 🚫 Ignore all input while ZORO is speaking or mic is muted
    if (isSpeaking || micMuted) return;

    let interim = '';
    let final   = '';

    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) final += t;
      else interim += t;
    }

    // Show live transcript
    if (interim) transcriptText.textContent = interim;

    if (!final) return;

    const text = final.trim().toLowerCase();
    console.log('Final:', text);
    transcriptText.textContent = final.trim();

    // ── While sleeping: only wake words
    if (!isAwake) {
      if (WAKE_WORDS.some(w => text.includes(w))) wakeUp();
      return;
    }

    // ── While busy (thinking/speaking): ignore
    if (isBusy) return;

    // ── Sleep words
    if (SLEEP_WORDS.some(w => text.includes(w))) {
      goSleep();
      return;
    }

    // ── Regular command → send to backend
    addMsg(final.trim(), 'user');
    askZORO(final.trim());
  };

  recognition.onerror = (e) => {
    console.warn('SR error:', e.error);
    if (e.error === 'not-allowed') {
      addMsg('Microphone blocked. Please allow mic access in Chrome.', 'zoro');
    }
  };

  recognition.onend = () => {
    // Always restart to keep listening
    if (isListening) setTimeout(() => { try { recognition.start(); } catch(e) {} }, 400);
  };

  isListening = true;
  try { recognition.start(); } catch(e) { console.warn(e); }
}

// ── Load model name from backend ─────────────────────────────────────────
async function loadStatus() {
  try {
    const res  = await fetch('/status');
    const data = await res.json();
    modelName.textContent = `Groq — ${data.model}`;
  } catch(e) {
    modelName.textContent = 'Server offline';
  }
}

// ── Text input send ───────────────────────────────────────────────────────
function sendText() {
  const input = document.getElementById('textInput');
  const text  = input.value.trim();
  if (!text) return;
  input.value = '';

  // Wake ZORO automatically if sleeping
  if (!isAwake) {
    isAwake = true;
    applyState('awake');
  }

  addMsg(text, 'user');
  askZORO(text);
}

// Enter key support
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('textInput');
  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') sendText();
    });
  }
});
window.addEventListener('load', () => {
  spawnParticles();
  applyState('sleep');
  synth.getVoices();
  speechSynthesis.onvoiceschanged = () => synth.getVoices();
  startRecognition();
  loadStatus();
});