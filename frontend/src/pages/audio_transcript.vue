<template>
    <q-page padding>
        <q-form @submit.prevent="submitAudio" @reset="onReset">
            <input type="file" @change="handleFileChange" accept=".wav,.mp3" />
            <q-btn label="Submit" type="submit" color="primary" />
            <q-btn label="Reset" type="reset" color="primary" flat />
        </q-form>
        <q-banner v-if="message" type="positive" class="q-mt-md">{{ message }}</q-banner>
        <audio v-if="audioUrl" :src="audioUrl" controls @timeupdate="onTimeUpdate" ref="audio" class="q-mt-md"></audio>
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
import axios from 'axios';


const file = ref(null);
const message = ref('');
const audioUrl = ref('');
const sentenceTimings = ref([]);
const currentSentenceIndex = ref(-1);

function handleFileChange(event) {
    const files = event.target.files;
    if (files.length > 0) {
        file.value = files[0];
    }
}

async function submitAudio() {
    if (file.value) {
        const formData = new FormData();
        formData.append('file', file.value);
        try {
            const response = await fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            if (response.ok) {
                message.value = data.message;
                audioUrl.value = `http://localhost:5000${data.file_url}`;
                sentenceTimings.value = data.sentence_timings;
                currentSentenceIndex.value = -1; // Reset current sentence index
            } else {
                console.error('Error:', data.error);
                message.value = `Error: ${data.error}`;
            }
        } catch (error) {
            console.error('Error:', error);
            message.value = `Error: ${error.message}`;
        }
    } else {
        message.value = 'Please upload an audio file.';
    }
}

function onReset() {
    file.value = null;
    message.value = '';
    audioUrl.value = '';
    sentenceTimings.value = [];
    currentSentenceIndex.value = -1; // Reset current sentence index
}

function onTimeUpdate(event) {
    const currentTime = event.target.currentTime;
    for (let i = 0; i < sentenceTimings.value.length; i++) {
        const { start_time, end_time } = sentenceTimings.value[i];
        if (currentTime >= start_time && currentTime <= end_time) {
            currentSentenceIndex.value = i;
            break;
        }
    }
}
</script>

<style scoped>
.highlighted {
    background-color: yellow;
}
</style>
