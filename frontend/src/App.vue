<script setup lang="ts">
import { ref } from 'vue';
import { postTalk, type TalkResponse } from './api/talk'
import VoiceRecorder from './components/VoiceRecorder.vue';

async function sendUserMessage() {
  if (message.value.trim() === '') {
    error.value = 'Provide a value';
    return;
  }

  const response: TalkResponse = await postTalk(message.value);
  console.log(response);
  const audio = new Audio(`http://localhost:8000/output_audio/${response.audio_file}`);
  audio.play();

  error.value = '';
  message.value = '';
}

const message = ref('')
const error = ref('')
</script>

<template>
  <h1>AI Talk Partner</h1>
  <VoiceRecorder />
</template>

<style scoped></style>
