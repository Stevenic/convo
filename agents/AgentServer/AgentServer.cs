using System;
using System.Net;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace AgentServer
{
    public class AgentServer
    {
        private const int DefaultPort = 4242;
        private HttpListener _httpListener;
        private CancellationTokenSource _cancellationTokenSource;

        public virtual void Start()
        {
            _httpListener = new HttpListener();
            _httpListener.Prefixes.Add($"http://localhost:{DefaultPort}/");
            _cancellationTokenSource = new CancellationTokenSource();

            _httpListener.Start();
            Console.WriteLine($"AgentServer started on port {DefaultPort}");

            Task.Run(() => AcceptConnections(_cancellationTokenSource.Token));
        }

        private async Task AcceptConnections(CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    HttpListenerContext context = await _httpListener.GetContextAsync();
                    if (context.Request.IsWebSocketRequest)
                    {
                        ProcessWebSocketRequest(context);
                    }
                    else
                    {
                        ProcessHttpRequest(context);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error accepting connection: {ex.Message}");
                }
            }
        }

        private async void ProcessWebSocketRequest(HttpListenerContext context)
        {
            HttpListenerWebSocketContext webSocketContext = await context.AcceptWebSocketAsync(null);
            WebSocket webSocket = webSocketContext.WebSocket;

            var transport = new WebSocketTransport(webSocket);
            await HandleWebSocketConnection(transport);
        }

        private async Task HandleWebSocketConnection(TransportInterface transport)
        {
            var buffer = new byte[1024 * 4];
            while (transport is WebSocketTransport wsTransport && wsTransport.WebSocket.State == WebSocketState.Open)
            {
                var result = await wsTransport.WebSocket.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
                if (result.MessageType == WebSocketMessageType.Text)
                {
                    string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    HandleIncomingMessage(message, transport);
                }
            }
        }

        private void ProcessHttpRequest(HttpListenerContext context)
        {
            var transport = new HttpTransport(context.Response);
            string requestBody;
            using (var reader = new System.IO.StreamReader(context.Request.InputStream, context.Request.ContentEncoding))
            {
                requestBody = reader.ReadToEnd();
            }
            HandleIncomingMessage(requestBody, transport);
        }

        public virtual void HandleIncomingMessage(string message, TransportInterface transport)
        {
            try
            {
                JObject jsonMessage = JObject.Parse(message);
                string messageType = jsonMessage["type"]?.ToString();

                switch (messageType)
                {
                    case "TaskRequest":
                        HandleTaskRequest(JsonConvert.DeserializeObject<TaskRequest>(message), transport);
                        break;
                    case "HandoffNotification":
                        HandleHandoffNotification(JsonConvert.DeserializeObject<HandoffNotification>(message), transport);
                        break;
                    case "CallbackNotification":
                        HandleCallbackNotification(JsonConvert.DeserializeObject<CallbackNotification>(message), transport);
                        break;
                    case "ClarificationResponse":
                        HandleClarificationResponse(JsonConvert.DeserializeObject<ClarificationResponse>(message), transport);
                        break;
                    default:
                        Console.WriteLine($"Unknown message type: {messageType}");
                        break;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error handling incoming message: {ex.Message}");
            }
        }

        public virtual void SendResponse(object response, TransportInterface transport)
        {
            transport.SendResponse(response);
        }

        public virtual void HandleTaskRequest(TaskRequest taskRequest, TransportInterface transport)
        {
            // Override this method to implement task processing logic
            Console.WriteLine($"Received TaskRequest: {taskRequest.task_ID}");
        }

        public virtual void HandleHandoffNotification(HandoffNotification handoffNotification, TransportInterface transport)
        {
            // Override this method to implement handoff notification logic
            Console.WriteLine($"Received HandoffNotification: {handoffNotification.task_ID}");
        }

        public virtual void HandleCallbackNotification(CallbackNotification callbackNotification, TransportInterface transport)
        {
            // Override this method to implement callback notification logic
            Console.WriteLine($"Received CallbackNotification: {callbackNotification.task_ID}");
        }

        public virtual void HandleClarificationResponse(ClarificationResponse clarificationResponse, TransportInterface transport)
        {
            // Override this method to implement clarification response logic
            Console.WriteLine($"Received ClarificationResponse: {clarificationResponse.task_ID}");
        }
    }

    public class TaskRequest
    {
        public string task_ID { get; set; }
        public string task { get; set; }
        public string requesting_agent_ID { get; set; }
        public string callback_URL { get; set; }
    }

    public class TaskResponse
    {
        public string task_ID { get; set; }
        public string result { get; set; }
        public string status { get; set; }
        public string replying_agent_ID { get; set; }
    }

    public class HandoffNotification
    {
        public string task_ID { get; set; }
        public string current_agent_ID { get; set; }
        public string new_agent_ID { get; set; }
        public string reason_for_handoff { get; set; }
    }

    public class ClarificationRequest
    {
        public string task_ID { get; set; }
        public string question { get; set; }
        public string requesting_agent_id { get; set; }
    }

    public class ClarificationResponse
    {
        public string task_ID { get; set; }
        public string answer { get; set; }
        public string replying_agent_id { get; set; }
    }

    public class CallbackNotification
    {
        public string task_ID { get; set; }
        public string result { get; set; }
        public string status { get; set; }
        public string requesting_agent_ID { get; set; }
        public string replying_agent_ID { get; set; }
    }

    public class ErrorMessage
    {
        public string task_ID { get; set; }
        public string error_message { get; set; }
        public string requesting_agent_ID { get; set; }
    }

    public interface TransportInterface
    {
        void SendResponse(object response);
    }

    public class WebSocketTransport : TransportInterface
    {
        public WebSocket WebSocket { get; }

        public WebSocketTransport(WebSocket webSocket)
        {
            WebSocket = webSocket;
        }

        public async void SendResponse(object response)
        {
            string jsonResponse = JsonConvert.SerializeObject(response);
            byte[] buffer = Encoding.UTF8.GetBytes(jsonResponse);
            await WebSocket.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
        }
    }

    public class HttpTransport : TransportInterface
    {
        private readonly HttpListenerResponse _response;

        public HttpTransport(HttpListenerResponse response)
        {
            _response = response;
        }

        public void SendResponse(object response)
        {
            string jsonResponse = JsonConvert.SerializeObject(response);
            byte[] buffer = Encoding.UTF8.GetBytes(jsonResponse);
            _response.ContentLength64 = buffer.Length;
            _response.ContentType = "application/json";
            _response.OutputStream.Write(buffer, 0, buffer.Length);
            _response.Close();
        }
    }
}