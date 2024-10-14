// client.js

const WebSocket = require('ws');
const readline = require('readline');
const record = require('node-record-lpcm16');
const Speaker = require('speaker');
const { Buffer } = require('buffer');

// Configuration Constants
const WS_URL = 'wss://api.openai.com/v1/assistants-streaming';
const MODEL = 'gpt-4o-realtime-preview-2024-10-01';
const SESSION_MODALITIES = ['text', 'audio'];
const SESSION_VOICE = 'alloy';
const TRANSCRIPTION_MODEL = 'whisper-1';
const AUDIO_FORMAT = 'pcm16';
const VAD_TYPE = 'server_vad';
const VAD_THRESHOLD = 0.5;
const SILENCE_DURATION = 200; // in milliseconds

// Placeholder for authentication if needed
const AUTH_TOKEN = 'YOUR_AUTH_TOKEN_HERE'; // Replace with actual token

// Initialize WebSocket
const ws = new WebSocket(WS_URL, {
    headers: {
        'Authorization': `Bearer ${AUTH_TOKEN}`,
        'Content-Type': 'application/json'
    }
});

// Session Variables
let sessionId = null;
let audioBuffer = Buffer.alloc(0);
let audioStream = null;

// Initialize Readline Interface for User Input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Function to display messages
function display(message) {
    console.log(message);
}

// Function to create a session
function createSession() {
    const sessionCreateMessage = {
        action: 'create_session',
        data: {
            model: MODEL,
            modalities: SESSION_MODALITIES,
            voice: SESSION_VOICE,
            input_transcription: {
                model: TRANSCRIPTION_MODEL,
                format: AUDIO_FORMAT
            },
            output_format: AUDIO_FORMAT,
            turn_detection: {
                type: VAD_TYPE,
                threshold: VAD_THRESHOLD
            },
            silence_duration: SILENCE_DURATION
        }
    };
    ws.send(JSON.stringify(sessionCreateMessage));
}

// Function to handle user text input
function handleUserTextInput(input) {
    const conversationItem = {
        action: 'create_conversation_item',
        data: {
            type: 'text',
            content: input
        }
    };
    ws.send(JSON.stringify(conversationItem));
    display(`User said: ${input}`);
}

// Function to handle user audio input
function handleUserAudioInput(audioBase64) {
    const audioBytes = Buffer.from(audioBase64, 'base64');
    audioBuffer = Buffer.concat([audioBuffer, audioBytes]);

    // Commit the audio buffer as a user message
    const audioMessage = {
        action: 'create_conversation_item',
        data: {
            type: 'audio',
            content: audioBuffer.toString('base64'),
            format: AUDIO_FORMAT
        }
    };
    ws.send(JSON.stringify(audioMessage));
    display('Audio message sent to the server.');

    // Reset the audio buffer
    audioBuffer = Buffer.alloc(0);
}

// Function to play audio from Base64
function playAudio(audioBase64) {
    const audioBytes = Buffer.from(audioBase64, 'base64');

    const speaker = new Speaker({
        channels: 1,          // 1 channel
        bitDepth: 16,         // 16-bit samples
        sampleRate: 16000     // 16 kHz sample rate
    });

    speaker.write(audioBytes);
    speaker.end();
}

// Function to handle server responses
function handleServerResponse(message) {
    const response = JSON.parse(message);

    switch (response.type) {
        case 'text':
            display(`Assistant: ${response.content}`);
            break;
        case 'audio':
            playAudio(response.content);
            break;
        case 'function_call':
            display(`Calling function ${response.function_name} with parameters: ${JSON.stringify(response.parameters)}`);
            break;
        case 'error':
            display(`Error: ${response.message}`);
            break;
        default:
            display(`Unknown response type: ${response.type}`);
    }
}

// Function to truncate a conversation item
function truncateConversationItem(itemId) {
    const truncateMessage = {
        action: 'truncate_conversation_item',
        data: {
            id: itemId
        }
    };
    ws.send(JSON.stringify(truncateMessage));
    display(`Truncated item ${itemId}`);
}

// Function to delete a conversation item
function deleteConversationItem(itemId) {
    const deleteMessage = {
        action: 'delete_conversation_item',
        data: {
            id: itemId
        }
    };
    ws.send(JSON.stringify(deleteMessage));
    display(`Deleted item ${itemId}`);
}

// Function to start recording audio
function startAudioRecording() {
    audioStream = record.record({
        sampleRate: 16000,
        channels: 1,
        audioType: 'raw',
        endOnSilence: false
    });

    audioStream.stream().on('data', (chunk) => {
        // Convert chunk to Base64 and send
        const audioBase64 = chunk.toString('base64');
        handleUserAudioInput(audioBase64);
    });

    display('Started audio recording...');
}

// Function to stop recording audio
function stopAudioRecording() {
    if (audioStream) {
        audioStream.stop();
        display('Stopped audio recording.');
    }
}

// WebSocket Event Handlers
ws.on('open', () => {
    display('Connected to WebSocket.');
    createSession();
});

ws.on('message', (data) => {
    const message = data.toString();
    const parsedMessage = JSON.parse(message);

    if (parsedMessage.action === 'session_created') {
        sessionId = parsedMessage.data.session_id;
        display('Session created successfully.');

        // Start listening for user input after session is created
        promptUserInput();
    } else {
        handleServerResponse(message);
    }
});

ws.on('error', (error) => {
    display(`Error occurred: ${error.message}`);
});

ws.on('close', () => {
    display('Connection closed.');
    process.exit(0);
});

// Function to prompt user for input
function promptUserInput() {
    rl.question('Enter text or type "audio" to send audio input, "truncate [id]", "delete [id]", or "exit": ', (answer) => {
        if (answer.toLowerCase() === 'exit') {
            closeConnection();
            return;
        }

        if (answer.toLowerCase() === 'audio') {
            // Start audio recording
            startAudioRecording();
            display('Press ENTER to stop recording.');
            rl.once('line', () => {
                stopAudioRecording();
                promptUserInput();
            });
            return;
        }

        const truncateMatch = answer.match(/^truncate\s+(\S+)/i);
        if (truncateMatch) {
            const itemId = truncateMatch[1];
            truncateConversationItem(itemId);
            promptUserInput();
            return;
        }

        const deleteMatch = answer.match(/^delete\s+(\S+)/i);
        if (deleteMatch) {
            const itemId = deleteMatch[1];
            deleteConversationItem(itemId);
            promptUserInput();
            return;
        }

        // Handle as text input
        handleUserTextInput(answer);
        promptUserInput();
    });
}

// Function to gracefully close the connection
function closeConnection() {
    ws.close();
    rl.close();
}

// Handle process termination
process.on('SIGINT', () => {
    display('\nGracefully shutting down...');
    closeConnection();
});
