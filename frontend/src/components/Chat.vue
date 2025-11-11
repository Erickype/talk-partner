<template>
  <div class="p-4 flex flex-col items-center space-y-3">
    <p :class="isConnected ? 'text-green-400' : 'text-gray-400'">
      {{ status }}
    </p>

    <p v-if="userText"><strong>You said:</strong> {{ userText }}</p>
    <p v-if="aiText"><strong>AI replied:</strong> {{ aiText }}</p>

    <button @click="sendMessage" class="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600">
      Send Audio
    </button>

    <div v-if="audioUrl" class="mt-4">
      <p class="text-sm text-gray-400">Recorded audio:</p>
      <audio :src="audioUrl" controls></audio>
      <audio v-if="responseURL" :src="responseURL" controls></audio>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";

/* ---------- Reactive State ---------- */
const props = defineProps<{ audioUrl?: string | null }>();

const isConnected = ref(false);
const status = ref("Disconnected");
const userText = ref("");
const aiText = ref("");
const responseURL = ref("");

let ws: WebSocket | null = null;
let audioCtx: AudioContext | null = null;
let nextStartTime = 0;

/* ---------- Audio Setup ---------- */
function initAudio() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext ||
      (window as any).webkitAudioContext)();
  }
}

async function pcmToAudioBuffer(pcmData: ArrayBuffer): Promise<AudioBuffer> {
  if (!audioCtx) initAudio();

  const int16 = new Int16Array(pcmData);
  const float32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) float32[i] = int16[i]! / 32768;

  const buffer = audioCtx!.createBuffer(1, float32.length, 24000);
  buffer.getChannelData(0).set(float32);
  return buffer;
}

function playChunk(buffer: AudioBuffer) {
  if (!audioCtx || !buffer) return;
  const src = audioCtx.createBufferSource();
  src.buffer = buffer;
  src.connect(audioCtx.destination);

  const current = audioCtx.currentTime;
  if (nextStartTime < current) nextStartTime = current;
  src.start(nextStartTime);
  nextStartTime += buffer.duration;
}

/* ---------- Playback Queue with Pre-buffer ---------- */
let bufferQueue: AudioBuffer[] = [];
let buffering = true; // initially buffering until ~0.25s of audio is ready
const MIN_QUEUE_SEC = 3.0; // aim to keep at least 3s buffered
const SAFE_MARGIN_SEC = 0.15; // if less than 150ms left, queue more

function playBufferedAudio() {
  if (!audioCtx || bufferQueue.length === 0) return;

  const bufferedSec = nextStartTime - audioCtx.currentTime;

  // If not enough audio is scheduled, push more
  while (bufferQueue.length > MIN_QUEUE_SEC && bufferedSec < SAFE_MARGIN_SEC) {
    const buffer = bufferQueue.shift()!;
    const src = audioCtx.createBufferSource();
    src.buffer = buffer;
    src.connect(audioCtx.destination);
    src.start(nextStartTime);
    nextStartTime += buffer.duration;
  }
}

/* ---------- WebSocket Handling ---------- */
function connect() {
  initAudio();
  ws = new WebSocket("ws://localhost:8000/talk/ws/talk");

  ws.onopen = () => {
    isConnected.value = true;
    status.value = "Connected to server";
    console.log("✅ WebSocket connected");
  };

  ws.onmessage = async (event) => {
    if (typeof event.data === "string") {
      const msg = JSON.parse(event.data);
      switch (msg.type) {
        case "transcription":
          userText.value = msg.text;
          break;
        case "reply_text":
          aiText.value = msg.text;
          break;
        case "audio_start":
          nextStartTime = audioCtx!.currentTime;
          bufferQueue = [];
          buffering = true;
          status.value = "Receiving audio…";
          break;
        case "audio_end":
          playBufferedAudio(); // flush remaining
          status.value = "Playback complete";
          break;
      }
      return;
    }

    // Binary PCM audio data
    if (event.data instanceof Blob) {
      const arr = await event.data.arrayBuffer();
      const buf = await pcmToAudioBuffer(arr);
      bufferQueue.push(buf);
      playBufferedAudio(); // check if enough audio to start
    }
  };

  ws.onerror = (e) => {
    console.error("❌ WebSocket error:", e);
    status.value = "Error";
  };

  ws.onclose = () => {
    isConnected.value = false;
    status.value = "Disconnected";
    console.log("🔌 WebSocket closed");
  };
}

/* ---------- Audio Upload ---------- */
async function sendAudio(blob: Blob) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    console.warn("Socket not open, cannot send.");
    return;
  }
  ws.send(await blob.arrayBuffer());
}

/* ---------- Button: Send Current Audio ---------- */
async function sendMessage() {
  if (!props.audioUrl) {
    console.warn("No audio to send");
    return;
  }

  const res = await fetch(props.audioUrl);
  const blob = await res.blob();
  await sendAudio(blob);
}

/* ---------- Lifecycle ---------- */
onMounted(connect);
onUnmounted(() => {
  ws?.close();
  audioCtx?.close();
});
</script>

<style scoped>
button {
  transition: background-color 0.2s ease;
}
</style>
