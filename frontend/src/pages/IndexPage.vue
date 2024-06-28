<template>
  <q-page padding>
    <q-form @submit="submitText" @reset="onReset">
      <q-input filled v-model="text" label="Enter text for TTS" hint="Type here..." />
      <q-btn label="Submit" type="submit" color="primary" />
      <q-btn label="Reset" type="reset" color="primary" flat />
    </q-form>
    <q-banner v-if="message" type="positive" class="q-mt-md">{{ message }}</q-banner>
    <audio v-if="audioUrl" :src="audioUrl" controls @timeupdate="onTimeUpdate" @playing="onPlayingSound" ref="audio"
      class="q-mt-md"></audio>
    <div v-if="sentenceTimings.length" class="q-mt-md">
      <h3>Sentence Timings</h3>
      <ul>
        <li v-for="(sentenceTiming, index) in sentenceTimings" :key="index"
          :class="{ highlighted: currentSentenceIndex === index }">
          {{ sentenceTiming.sentence }}
        </li>
      </ul>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue';

const text = ref('');
const message = ref('');
const audioUrl = ref('');
const sentenceTimings = ref([]);
const currentSentenceIndex = ref(-1);

async function submitText() {
  try {
    const response = await fetch('http://localhost:5000/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text.value })
    });

    if (response.ok) {
      const data = await response.json();
      message.value = data.message;
      audioUrl.value = `http://localhost:5000${data.file_url}`;
      sentenceTimings.value = data.sentence_timings;
      console.log('Sentence timings:', sentenceTimings.value);
      currentSentenceIndex.value = -1; // Reset current sentence index
    } else {
      const error = await response.json();
      console.error('Error:', error.error);
      message.value = `Error: ${error.error}`;
    }
  } catch (error) {
    console.error('Error:', error);
    message.value = `Error: ${error.message}`;
  }
}

function onReset() {
  text.value = '';
  message.value = '';
  audioUrl.value = '';
  sentenceTimings.value = [];
  currentSentenceIndex.value = -1; // Reset current sentence index
}

// const onPlayingSound = (event) => {
//   console.log('Playing sound');
//   console.log(event);
// }

function onTimeUpdate(event) {
  const currentTime = event.target.currentTime;
  console.log('Current time:', currentTime);
  for (let i = 0; i < sentenceTimings.value.length; i++) {
    const { start_time, end_time } = sentenceTimings.value[i];
    if (currentTime >= start_time && currentTime <= end_time) {
      currentSentenceIndex.value = i;
    }
  }
}
</script>

<style scoped>
.highlighted {
  background-color: yellow;
}
</style>
