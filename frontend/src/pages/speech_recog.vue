<template>
    <q-page padding>
        <q-form @submit.prevent="transcribeAndConvert" @reset="onReset">
            <input type="file" @change="handleFileChange" accept=".wav,.mp3" />
            <q-btn label="Submit" type="submit" color="primary" />
            <q-btn label="Reset" type="reset" color="primary" flat />
        </q-form>
        <q-banner v-if="message" type="positive" class="q-mt-md">{{ message }}</q-banner>
        <audio v-if="audioUrl" :src="audioUrl" controls @timeupdate="onTimeUpdate" ref="audio" class="q-mt-md"></audio>
        <div v-if="sentenceTimings.length" class="q-mt-md">
            <h3>Sentence Timings</h3>
            <ul>
                <li v-for="(sentenceTiming, index) in sentenceTimings" :key="index">
                    <div :class="{ highlighted: currentSentenceIndex === index }">
                        {{ sentenceTiming.sentence }}
                    </div>
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
const text = ref(` Elephants are the biggest land mammals. They have enormous ears, long noses or trunks and tusks. They can weigh more than 10 tons or six cars.
      `);


function handleFileChange(event) {
    const files = event.target.files;
    if (files.length > 0) {
        file.value = files[0];
    }
}

async function transcribeAndConvert() {
    try {
        // Send the transcribed text to the backend for audio conversion
        const response = await sendTextToBackend(text.value);
        message.value = response.message;
        audioUrl.value = `http://localhost:5000${response.file_url}`;
        sentenceTimings.value = response.sentence_timings;
        currentSentenceIndex.value = -1; // Reset current sentence index
    } catch (error) {
        console.error('Error:', error);
        message.value = `Error: ${error.message}`;
    }

}

async function sendTextToBackend(text) {
    console.log("Sending text to backend:", text); // Debug statement
    try {
        const response = await axios.post('http://localhost:5000/convert', { text }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error sending text to backend:', error);
        console.error('Error details:', error.response ? error.response.data : error.message);
        throw error;
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
    transition: 1s ease;
    display: inline-block;

}
</style>
