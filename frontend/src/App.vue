<script setup lang="ts">
import { ref } from 'vue'
import VoiceRecorder from './components/VoiceRecorder.vue'
import Chat from './components/Chat.vue'

// Hold the latest captured audio URL (object URL)
const audioUrl = ref<string | null>(null)

function onAudio(url: string) {
  // Revoke previous object URL to avoid leaking memory
  if (audioUrl.value) {
    try { URL.revokeObjectURL(audioUrl.value) } catch (e) { /* ignore */ }
  }
  // Save and pass to sibling via prop
  audioUrl.value = url
}
</script>

<template>
  <h1>AI Talk Partner</h1>
  <VoiceRecorder @audio="onAudio" />
  <Chat :audioUrl="audioUrl ?? undefined" />
</template>

<style scoped></style>
