using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using NAudio.Wave;
using System.IO;
using System.Collections.Concurrent;

namespace OpenAIWebSocketClient
{
    // Define the structure of messages
    public class SessionCreateMessage
    {
        public string type = "session_create";
        public string model { get; set; }
        public string[] modalities { get; set; }
        public string voice { get; set; }
        public InputAudioConfig input_audio_config { get; set; }
        public OutputAudioConfig output_audio_config { get; set; }
        public TurnDetectionConfig turn_detection { get; set; }
    }

    public class InputAudioConfig
    {
        public string transcription_model { get; set; }
        public string format { get; set; }
    }

    public class OutputAudioConfig
    {
        public string format { get; set; }
    }

    public class TurnDetectionConfig
    {
        public string type { get; set; }
        public double threshold { get; set; }
        public int silence_duration_ms { get; set; }
    }

    public class ConversationItem
    {
        public string type { get; set; } = "user";
        public string content { get; set; }
    }

    public class TruncateDeleteEvent
    {
        public string type { get; set; }
        public string event_type { get; set; }
        public string item_id { get; set; }
    }

    class Program
    {
        private static ClientWebSocket _webSocket = new ClientWebSocket();
        private static CancellationTokenSource _cancellation = new CancellationTokenSource();
        private static string _sessionId;
        private static ConcurrentDictionary<string, string> _conversationItems = new ConcurrentDictionary<string, string>();
        private static MemoryStream _audioBuffer = new MemoryStream();

        static async Task Main(string[] args)
        {
            Console.WriteLine("Starting OpenAI WebSocket Client...");

            try
            {
                await ConnectWebSocket();

                // Start receiving messages
                var receiveTask = ReceiveMessages();

                // Start handling user input
                await HandleUserInput();

                // Wait for receive task to complete
                await receiveTask;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error occurred: {ex.Message}");
            }
            finally
            {
                await CloseWebSocket();
            }
        }

        private static async Task ConnectWebSocket()
        {
            var uri = new Uri("wss://api.openai.com/v1/assistants-streaming");
            await _webSocket.ConnectAsync(uri, CancellationToken.None);
            Console.WriteLine("WebSocket connected.");

            // Create session
            var sessionMessage = new SessionCreateMessage
            {
                model = "gpt-4o-realtime-preview-2024-10-01",
                modalities = new string[] { "text", "audio" },
                voice = "alloy",
                input_audio_config = new InputAudioConfig
                {
                    transcription_model = "whisper-1",
                    format = "pcm16"
                },
                output_audio_config = new OutputAudioConfig
                {
                    format = "pcm16"
                },
                turn_detection = new TurnDetectionConfig
                {
                    type = "server_vad",
                    threshold = 0.5,
                    silence_duration_ms = 200
                }
            };

            string sessionJson = JsonConvert.SerializeObject(sessionMessage);
            await SendMessage(sessionJson);
            Console.WriteLine("Session created successfully.");
        }

        private static async Task SendMessage(string message)
        {
            var bytes = Encoding.UTF8.GetBytes(message);
            var buffer = new ArraySegment<byte>(bytes);
            await _webSocket.SendAsync(buffer, WebSocketMessageType.Text, true, CancellationToken.None);
        }

        private static async Task ReceiveMessages()
        {
            var buffer = new byte[8192];

            try
            {
                while (_webSocket.State == WebSocketState.Open)
                {
                    var result = await _webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), _cancellation.Token);

                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        Console.WriteLine("Server initiated close. Closing connection.");
                        await _webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
                        break;
                    }

                    int count = result.Count;
                    using (var ms = new MemoryStream())
                    {
                        ms.Write(buffer, 0, count);
                        while (!result.EndOfMessage)
                        {
                            result = await _webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), _cancellation.Token);
                            ms.Write(buffer, 0, result.Count);
                        }
                        var message = Encoding.UTF8.GetString(ms.ToArray());
                        HandleServerMessage(message);
                    }
                }
            }
            catch (OperationCanceledException)
            {
                // Ignore cancellation
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error occurred: {ex.Message}");
            }
        }

        private static void HandleServerMessage(string message)
        {
            try
            {
                var json = JObject.Parse(message);
                var type = json["type"]?.ToString();

                switch (type)
                {
                    case "text":
                        string responseText = json["content"]?.ToString();
                        Console.WriteLine($"Assistant: {responseText}");
                        break;
                    case "audio":
                        string audioBase64 = json["content"]?.ToString();
                        PlayAudio(audioBase64);
                        break;
                    case "function_call":
                        string functionName = json["function_name"]?.ToString();
                        string parameters = json["parameters"]?.ToString();
                        Console.WriteLine($"Calling function {functionName} with parameters: {parameters}");
                        break;
                    case "error":
                        string errorMessage = json["message"]?.ToString();
                        Console.WriteLine($"Error: {errorMessage}");
                        break;
                    default:
                        Console.WriteLine($"Unknown message type: {type}");
                        break;
                }
            }
            catch (JsonException ex)
            {
                Console.WriteLine($"Error parsing server message: {ex.Message}");
            }
        }

        private static void PlayAudio(string audioBase64)
        {
            try
            {
                byte[] audioBytes = Convert.FromBase64String(audioBase64);
                using (var ms = new MemoryStream(audioBytes))
                using (var waveOut = new WaveOutEvent())
                using (var waveProvider = new RawSourceWaveStream(ms, new WaveFormat(16000, 16, 1)))
                {
                    waveOut.Init(waveProvider);
                    waveOut.Play();
                    while (waveOut.PlaybackState == PlaybackState.Playing)
                    {
                        Thread.Sleep(100);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error playing audio: {ex.Message}");
            }
        }

        private static async Task HandleUserInput()
        {
            Console.WriteLine("You can start typing your messages. Type 'exit' to quit.");
            Console.WriteLine("To send audio, type 'audio'.");

            while (true)
            {
                Console.Write("> ");
                string input = Console.ReadLine();

                if (string.IsNullOrWhiteSpace(input))
                    continue;

                if (input.Equals("exit", StringComparison.OrdinalIgnoreCase))
                {
                    break;
                }
                else if (input.StartsWith("truncate ", StringComparison.OrdinalIgnoreCase))
                {
                    string itemId = input.Substring(9).Trim();
                    await TruncateConversationItem(itemId);
                }
                else if (input.StartsWith("delete ", StringComparison.OrdinalIgnoreCase))
                {
                    string itemId = input.Substring(7).Trim();
                    await DeleteConversationItem(itemId);
                }
                else if (input.Equals("audio", StringComparison.OrdinalIgnoreCase))
                {
                    await HandleAudioInput();
                }
                else
                {
                    await SendTextMessage(input);
                }
            }
        }

        private static async Task SendTextMessage(string text)
        {
            var conversationItem = new ConversationItem
            {
                content = text
            };

            string json = JsonConvert.SerializeObject(conversationItem);
            await SendMessage(json);
            Console.WriteLine($"User said: {text}");
        }

        private static async Task HandleAudioInput()
        {
            Console.WriteLine("Recording audio... Press Enter to stop.");
            var audioBytes = RecordAudio();
            if (audioBytes != null && audioBytes.Length > 0)
            {
                string audioBase64 = Convert.ToBase64String(audioBytes);
                // Assuming the server expects audio messages with type 'audio'
                var audioMessage = new
                {
                    type = "audio",
                    content = audioBase64
                };
                string json = JsonConvert.SerializeObject(audioMessage);
                await SendMessage(json);
                Console.WriteLine("Audio message sent to the server.");
            }
            else
            {
                Console.WriteLine("No audio recorded.");
            }
        }

        private static byte[] RecordAudio()
        {
            try
            {
                using (var waveIn = new WaveInEvent())
                {
                    waveIn.WaveFormat = new WaveFormat(16000, 16, 1); // PCM16
                    using (var ms = new MemoryStream())
                    {
                        waveIn.DataAvailable += (s, a) =>
                        {
                            ms.Write(a.Buffer, 0, a.BytesRecorded);
                        };

                        waveIn.StartRecording();
                        Console.ReadLine(); // Wait for Enter to stop
                        waveIn.StopRecording();

                        return ms.ToArray();
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error recording audio: {ex.Message}");
                return null;
            }
        }

        private static async Task TruncateConversationItem(string itemId)
        {
            var truncateEvent = new TruncateDeleteEvent
            {
                type = "conversation_event",
                event_type = "truncate",
                item_id = itemId
            };

            string json = JsonConvert.SerializeObject(truncateEvent);
            await SendMessage(json);
            Console.WriteLine($"Truncated item {itemId}");
        }

        private static async Task DeleteConversationItem(string itemId)
        {
            var deleteEvent = new TruncateDeleteEvent
            {
                type = "conversation_event",
                event_type = "delete",
                item_id = itemId
            };

            string json = JsonConvert.SerializeObject(deleteEvent);
            await SendMessage(json);
            Console.WriteLine($"Deleted item {itemId}");
        }

        private static async Task CloseWebSocket()
        {
            if (_webSocket.State == WebSocketState.Open || _webSocket.State == WebSocketState.CloseReceived)
            {
                await _webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
                Console.WriteLine("Connection closed.");
            }
            _cancellation.Cancel();
            _webSocket.Dispose();
        }
    }
}
