use tokio::net::TcpStream;
use tokio::sync::mpsc;
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message};
use serde::{Serialize, Deserialize};
use serde_json::json;
use futures::{SinkExt, StreamExt};
use base64::{encode as base64_encode, decode as base64_decode};
use std::error::Error;
use std::io::{self, Write};
use bytes::Bytes;

// Define the structures for various message types
#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "type", content = "data")]
enum ServerMessage {
    Text { text: String },
    Audio { audio: String }, // Base64-encoded audio
    FunctionCall { function_name: String, parameters: serde_json::Value },
    Error { message: String },
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "type", content = "data")]
enum ClientMessage {
    CreateSession {
        model: String,
        modalities: Vec<String>,
        voice: String,
        input_audio_transcription: String,
        input_audio_format: String,
        output_audio_format: String,
        turn_detection: TurnDetection,
        silence_duration_ms: u64,
    },
    ConversationItem {
        role: String,
        content: String,
    },
    TruncateEvent {
        item_id: String,
    },
    DeleteEvent {
        item_id: String,
    },
}

#[derive(Serialize, Deserialize, Debug)]
struct TurnDetection {
    type_field: String, // "type" is a reserved keyword
    threshold: f64,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // WebSocket URL
    let ws_url = "wss://api.openai.com/v1/assistants-streaming";

    // Insert your OpenAI API key here
    let api_key = "YOUR_OPENAI_API_KEY";

    // Set up headers with authorization
    let (ws_stream, _) = connect_async(
        tungstenite::handshake::client::Request::builder()
            .uri(ws_url)
            .header("Authorization", format!("Bearer {}", api_key))
            .header("Content-Type", "application/json")
            .body(())
            .unwrap(),
    ).await?;

    println!("Connected to WebSocket.");

    let (mut write, read) = ws_stream.split();

    // Create a channel for sending messages from user input to the WebSocket writer
    let (tx, mut rx) = mpsc::unbounded_channel();

    // Spawn a task to handle incoming WebSocket messages
    tokio::spawn(async move {
        read.for_each(|message| async {
            match message {
                Ok(msg) => {
                    if msg.is_text() {
                        handle_server_response(msg.to_text().unwrap()).await;
                    } else if msg.is_binary() {
                        // Handle binary messages if necessary
                        println!("Received binary message.");
                    }
                },
                Err(e) => {
                    println!("WebSocket error: {}", e);
                },
            }
        }).await;
    });

    // Spawn a task to handle outgoing messages
    let write_task = tokio::spawn(async move {
        while let Some(msg) = rx.recv().await {
            if let Err(e) = write.send(msg).await {
                println!("Error sending message: {}", e);
                break;
            }
        }
    });

    // Create session
    let create_session_msg = ClientMessage::CreateSession {
        model: "gpt-4o-realtime-preview-2024-10-01".to_string(),
        modalities: vec!["text".to_string(), "audio".to_string()],
        voice: "alloy".to_string(),
        input_audio_transcription: "whisper-1".to_string(),
        input_audio_format: "pcm16".to_string(),
        output_audio_format: "pcm16".to_string(),
        turn_detection: TurnDetection {
            type_field: "server_vad".to_string(),
            threshold: 0.5,
        },
        silence_duration_ms: 200,
    };

    let msg_text = serde_json::to_string(&create_session_msg)?;
    tx.send(Message::Text(msg_text))?;
    println!("Session created successfully.");

    // Handle user input
    loop {
        print!("Enter command (text/audio/quit): ");
        io::stdout().flush()?;
        let mut command = String::new();
        io::stdin().read_line(&mut command)?;
        let command = command.trim();

        if command.eq_ignore_ascii_case("quit") {
            break;
        } else if command.eq_ignore_ascii_case("text") {
            print!("Enter your message: ");
            io::stdout().flush()?;
            let mut user_input = String::new();
            io::stdin().read_line(&mut user_input)?;
            let user_input = user_input.trim().to_string();

            let conversation_item = ClientMessage::ConversationItem {
                role: "user".to_string(),
                content: user_input.clone(),
            };

            let msg_text = serde_json::to_string(&conversation_item)?;
            tx.send(Message::Text(msg_text))?;
            println!("User said: {}", user_input);
        } else if command.eq_ignore_ascii_case("audio") {
            print!("Enter path to PCM16 audio file: ");
            io::stdout().flush()?;
            let mut path = String::new();
            io::stdin().read_line(&mut path)?;
            let path = path.trim();

            // Read the audio file
            match tokio::fs::read(path).await {
                Ok(audio_bytes) => {
                    // Encode to Base64
                    let encoded_audio = base64_encode(&audio_bytes);

                    let audio_message = ClientMessage::ConversationItem {
                        role: "user".to_string(),
                        content: encoded_audio,
                    };

                    let msg_text = serde_json::to_string(&audio_message)?;
                    tx.send(Message::Text(msg_text))?;
                    println!("Audio message sent to the server.");
                },
                Err(e) => {
                    println!("Failed to read audio file: {}", e);
                },
            }
        } else {
            println!("Unknown command. Please enter 'text', 'audio', or 'quit'.");
        }
    }

    // Close the WebSocket connection
    tx.send(Message::Close(None))?;
    println!("Connection closed.");

    // Await the write task to finish
    write_task.await?;

    Ok(())
}

async fn handle_server_response(message: &str) {
    let parsed: serde_json::Result<ServerMessage> = serde_json::from_str(message);
    match parsed {
        Ok(server_msg) => {
            match server_msg {
                ServerMessage::Text { text } => {
                    println!("Assistant: {}", text);
                },
                ServerMessage::Audio { audio } => {
                    match base64_decode(&audio) {
                        Ok(audio_bytes) => {
                            // Here you can implement audio playback using a suitable crate
                            // For simplicity, we'll just acknowledge the reception
                            println!("Received audio response. [Audio playback not implemented]");
                        },
                        Err(e) => {
                            println!("Failed to decode audio: {}", e);
                        },
                    }
                },
                ServerMessage::FunctionCall { function_name, parameters } => {
                    println!("Calling function {} with parameters: {}", function_name, parameters);
                    // Implement function calling logic as needed
                },
                ServerMessage::Error { message } => {
                    println!("Error: {}", message);
                },
            }
        },
        Err(e) => {
            println!("Failed to parse server message: {}", e);
        },
    }
}
