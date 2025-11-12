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
      <p v-if="responseURL" class="text-sm text-gray-400">Generated audio:</p>
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
const MIN_QUEUE_SEC = 5.0; // aim to keep at least ~5s buffered

// captured buffers for replay/export
const capturedBuffers: AudioBuffer[] = [];

function playBufferedAudio() {
  // Optionally pass `flush=true` to force scheduling of all remaining buffers
  // (used when we receive an audio_end signal).
  return playBufferedAudioInternal(false);
}

function playBufferedAudioInternal(flush: boolean) {
  if (!audioCtx || bufferQueue.length === 0) return;

  const current = audioCtx.currentTime;
  if (nextStartTime < current) nextStartTime = current;

  // seconds already scheduled for playback
  let bufferedSec = nextStartTime - current;

  // compute how many seconds are queued but not yet scheduled
  const queuedSec = bufferQueue.reduce((s, b) => s + b.duration, 0);

  const START_THRESHOLD_SEC = MIN_QUEUE_SEC; // start playing once we have this much queued

  // If we're still buffering, only start once we've accumulated a small threshold
  if (buffering) {
    if (!flush && queuedSec < START_THRESHOLD_SEC) {
      // still buffering, not enough to start
      return;
    }
    // we've met the start threshold (or are flushing) -> start playback
    buffering = false;
    status.value = "Playing audio…";
  }

  // Schedule buffers while we need more scheduled audio, or schedule everything if flushing
  while (bufferQueue.length > 0 && (flush || bufferedSec < MIN_QUEUE_SEC)) {
    const buffer = bufferQueue.shift()!;
    const src = audioCtx.createBufferSource();
    src.buffer = buffer;
    src.connect(audioCtx.destination);
    src.start(nextStartTime);
    nextStartTime += buffer.duration;
    bufferedSec += buffer.duration;
  }

  // If we flushed everything, reset buffering so subsequent streams start in buffering mode
  if (flush && bufferQueue.length === 0) buffering = true;
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
              // clear any previous captured buffers for a fresh replay
              capturedBuffers.length = 0;
              if (responseURL.value) {
                URL.revokeObjectURL(responseURL.value);
                responseURL.value = "";
              }
          status.value = "Receiving audio…";
          break;
        case "audio_end":
          // flush remaining buffers even if we don't have MIN_QUEUE_SEC
          playBufferedAudioInternal(true);
          // automatically export captured audio so the audio player appears
          try {
            exportCaptured();
          } catch (e) {
            // exportCaptured already logs errors; ignore here
          }
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
    // also save for replay
    capturedBuffers.push(buf);
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

/* ---------- Capture / Export Replay ---------- */

function floatTo16BitPCM(output: DataView, offset: number, input: Float32Array) {
  for (let i = 0; i < input.length; i++, offset += 2) {
    const v = input[i] ?? 0;
    const s = Math.max(-1, Math.min(1, v));
    output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
}

function writeString(view: DataView, offset: number, str: string) {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i));
  }
}

function audioBuffersToWav(buffers: AudioBuffer[]): Blob {
  if (buffers.length === 0) throw new Error("No buffers to export");

  const first = buffers[0]!;
  const sampleRate = first.sampleRate;
  const totalLength = buffers.reduce((s, b) => s + b.length, 0);

  const bytesPerSample = 2;
  const blockAlign = 1 * bytesPerSample; // mono
  const byteRate = sampleRate * blockAlign;
  const dataSize = totalLength * bytesPerSample;
  const buffer = new ArrayBuffer(44 + dataSize);
  const view = new DataView(buffer);

  /* RIFF identifier */
  writeString(view, 0, 'RIFF');
  /* file length */
  view.setUint32(4, 36 + dataSize, true);
  /* RIFF type */
  writeString(view, 8, 'WAVE');
  /* format chunk identifier */
  writeString(view, 12, 'fmt ');
  /* format chunk length */
  view.setUint32(16, 16, true);
  /* sample format (raw) */
  view.setUint16(20, 1, true);
  /* channel count */
  view.setUint16(22, 1, true);
  /* sample rate */
  view.setUint32(24, sampleRate, true);
  /* byte rate (sample rate * block align) */
  view.setUint32(28, byteRate, true);
  /* block align (channel count * bytes per sample) */
  view.setUint16(32, blockAlign, true);
  /* bits per sample */
  view.setUint16(34, 16, true);
  /* data chunk identifier */
  writeString(view, 36, 'data');
  /* data chunk length */
  view.setUint32(40, dataSize, true);

  // write PCM samples
  let offset = 44;
  for (const b of buffers) {
    const ch = b.getChannelData(0);
    floatTo16BitPCM(view, offset, ch);
    offset += ch.length * bytesPerSample;
  }

  return new Blob([view], { type: 'audio/wav' });
}

function exportCaptured() {
  try {
    if (capturedBuffers.length === 0) {
      console.warn('No captured audio to export');
      return;
    }
    const wav = audioBuffersToWav(capturedBuffers);
    if (responseURL.value) URL.revokeObjectURL(responseURL.value);
    responseURL.value = URL.createObjectURL(wav);
    status.value = 'Replay saved';
  } catch (e) {
    console.error('Failed to export captured audio', e);
    status.value = 'Export failed';
  }
}
</script>

<style scoped>
button {
  transition: background-color 0.2s ease;
}
</style>
