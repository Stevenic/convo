const express = require('express');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

app.use(express.json());

// Message Types
const MessageType = {
    TaskRequest: 'TaskRequest',
    TaskResponse: 'TaskResponse',
    HandoffNotification: 'HandoffNotification',
    ClarificationRequest: 'ClarificationRequest',
    ClarificationResponse: 'ClarificationResponse',
    CallbackNotification: 'CallbackNotification',
    ErrorMessage: 'ErrorMessage'
};

// Server-Side Transport Abstraction
class Transport {
    constructor() {
        this.handlers = {};
    }

    on(messageType, handler) {
        this.handlers[messageType] = handler;
    }

    handleMessage(message) {
        const handler = this.handlers[message.type];
        if (handler) {
            handler(message);
        } else {
            console.error(`No handler for message type: ${message.type}`);
        }
    }

    sendResponse(client, response) {
        if (client instanceof WebSocket) {
            client.send(JSON.stringify(response));
        } else {
            client.json(response);
        }
    }
}

const transport = new Transport();

// Task Handlers
transport.on(MessageType.TaskRequest, (message) => {
    // Implement task request handling logic here
    console.log('Received TaskRequest:', message);
    // Example response:
    transport.sendResponse(message.client, {
        type: MessageType.TaskResponse,
        taskId: message.taskId,
        result: 'Task processed successfully',
        status: 'success',
        agentId: 'agent-001'
    });
});

transport.on(MessageType.ClarificationResponse, (message) => {
    // Implement clarification response handling logic here
    console.log('Received ClarificationResponse:', message);
    // Example: resume task execution
});

transport.on(MessageType.CallbackNotification, (message) => {
    // Implement callback notification handling logic here
    console.log('Received CallbackNotification:', message);
    // Example: forward result to originating agent or callback URL
});

// Server Transport Management
wss.on('connection', (ws) => {
    ws.on('message', (message) => {
        const parsedMessage = JSON.parse(message);
        parsedMessage.client = ws;
        transport.handleMessage(parsedMessage);
    });
});

// HTTP endpoints
app.post('/task', (req, res) => {
    const message = req.body;
    message.client = res;
    transport.handleMessage(message);
});

app.post('/clarification', (req, res) => {
    const message = req.body;
    message.client = res;
    transport.handleMessage(message);
});

app.post('/handoff', (req, res) => {
    const message = req.body;
    message.client = res;
    transport.handleMessage(message);
});

app.post('/callback', (req, res) => {
    const message = req.body;
    message.client = res;
    transport.handleMessage(message);
});

// Start the server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});