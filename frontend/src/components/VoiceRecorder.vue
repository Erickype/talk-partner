<script setup>
import { ref } from 'vue'

const isRecording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const userText = ref('')
const aiReply = ref('')
const aiAudio = ref(null)

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
    const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.wav')

    const response = await fetch('http://localhost:8000/talk/voice', {
        method: 'POST',
        body: formData
    })

    const data = await response.json()
    userText.value = data.user_text
    aiReply.value = data.reply_text
    aiAudio.value = `http://localhost:8000/output_audio/${data.audio_file}`
}
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
