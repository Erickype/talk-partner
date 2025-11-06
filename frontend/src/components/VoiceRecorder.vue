<script lang="ts" setup>
import { ref } from 'vue'

const isRecording = ref(false)
const mediaRecorder = ref(new MediaRecorder(new MediaStream()))
const audioChunks = ref<Blob[]>([])
const userText = ref('')
const aiReply = ref('')

// Emit typed event when audio is ready
const emit = defineEmits<{ (e: 'audio', audioUrl: string): void }>()

async function toggleRecording(event: Event) {
    if (!isRecording.value) {
        // ... (existing recording start logic) ...
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        mediaRecorder.value = new MediaRecorder(stream)
        audioChunks.value = []

        mediaRecorder.value.ondataavailable = (e) => {
            if (e.data.size > 0) audioChunks.value.push(e.data as never)
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

async function handleStop(event: Event) {
    const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
    // Create an object URL for the captured audio and emit it to parent
    const audioUrl = URL.createObjectURL(audioBlob)
    emit('audio', audioUrl)
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

    </div>
</template>

<style scoped>
button {
    transition: background-color 0.2s ease;
}
</style>
