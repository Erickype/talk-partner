<script setup>
import { ref } from 'vue'

const isRecording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const userText = ref('')
const aiReply = ref('')
const aiAudio = ref(null)

const audioContext = ref(null);
let audioQueue = [];
let isPlaying = false;
let startTime = 0;

// Initialize AudioContext on user interaction for browser compatibility
const initAudioContext = () => {
    if (!audioContext.value) {
        audioContext.value = new (window.AudioContext || window.webkitAudioContext)();
        // Ensure the audio context is running (it might be suspended initially)
        if (audioContext.value.state === 'suspended') {
            audioContext.value.resume();
        }
    }
};

async function toggleRecording() {
    if (!isRecording.value) {
        // Start recording
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        mediaRecorder.value = new MediaRecorder(stream)
        audioChunks.value = []

        mediaRecorder.value.ondataavailable = (e) => {
            if (e.data.size > 0) audioChunks.value.push(e.data)
        }

        mediaRecorder.value.onstop = handleStop

        mediaRecorder.value.start()
        isRecording.value = true
    } else {
        // Stop recording
        mediaRecorder.value.stop()
        isRecording.value = false
    }
}

async function handleStop() {
    initAudioContext();
    let audioBlob = new Blob(audioChunks.value, { type: "audio/wav" });
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");

    const response = await fetch("http://localhost:8000/talk/voice", {
        method: "POST",
        body: formData,
    });

    userText.value = response.headers.get("X-User-Text") || "";
    aiReply.value = response.headers.get("X-Reply-Text") || "";

    if (!response.body) return;

    const reader = response.body.getReader();
    const processChunks = async () => {
        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                console.log("Stream complete");
                // Wait for the remaining queue to play
                await onPlaybackDone();
                break;
            }
            // Value is a Uint8Array of bytes (your audio chunks)
            audioQueue.push(value);
            if (!isPlaying) {
                playNextChunk();
            }
        }
    };

    processChunks();
}

const playNextChunk = async () => {
    if (audioQueue.length === 0) {
        isPlaying = false;
        return;
    }

    isPlaying = true;
    const chunk = audioQueue.shift();

    // Assuming the FastAPI endpoint is sending raw PCM (Int16) as specified in your function
    // Convert Uint8Array to an AudioBuffer for playback
    const audioBuffer = await decodeAudioData(chunk);

    // Schedule the audio chunk to play after the previous one finishes
    const source = audioContext.value.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.value.destination);

    // Play immediately if it's the first chunk, otherwise schedule at the end of the previous one
    if (startTime === 0) {
        startTime = audioContext.value.currentTime;
    }

    source.start(startTime);
    startTime += source.buffer.duration; // Update the start time for the next chunk

    source.onended = () => {
        playNextChunk(); // Play the next chunk when this one ends
    };
};

const decodeAudioData = async (uint8Array) => {
    // Convert the Uint8Array to an Int16Array, then to a Float32Array (Web Audio API format)
    const int16Array = new Int16Array(uint8Array.buffer);
    const float32Array = new Float32Array(int16Array.length);
    for (let i = 0; i < int16Array.length; i++) {
        float32Array[i] = int16Array[i] / 0x7FFF; // Normalize to -1.0 to 1.0
    }

    // Create an AudioBuffer from the Float32Array
    // You need the correct sample rate (e.g., 22050 Hz or 44100 Hz) from your tts_model
    const sampleRate = 22050; // <--- **IMPORTANT: Replace with your actual sample rate**
    const audioBuffer = audioContext.value.createBuffer(1, float32Array.length, sampleRate);
    audioBuffer.copyToChannel(float32Array, 0);
    return audioBuffer;
};

// Utility to ensure all audio plays before resolving
const onPlaybackDone = () => {
    return new Promise(resolve => {
        const checkQueue = setInterval(() => {
            if (audioQueue.length === 0 && !isPlaying) {
                clearInterval(checkQueue);
                startTime = 0; // Reset start time for next stream
                resolve();
            }
        }, 100);
    });
};

</script>

<template>
    <div class="p-4 flex flex-col items-center space-y-4">
        <div>
            <button @click="toggleRecording" class="px-6 py-3 rounded-xl font-semibold"
                :class="isRecording ? 'bg-red-500 text-white' : 'bg-green-500 text-white'">
                {{ isRecording ? 'Stop Recording' : 'Start Speaking' }}
            </button>
        </div>

        <div v-if="userText" class="text-center">
            <p class="text-gray-300 text-sm">You said:</p>
            <p class="text-xl font-semibold text-white">{{ userText }}</p>
        </div>

        <div v-if="aiReply" class="text-center">
            <p class="text-gray-300 text-sm">AI replied:</p>
            <p class="text-xl font-semibold text-blue-400">{{ aiReply }}</p>
        </div>

        <audio v-if="aiAudio" :src="aiAudio" controls autoplay class="mt-4"></audio>
    </div>
</template>

<style scoped>
button {
    transition: background-color 0.2s ease;
}
</style>
