const express = require('express');
const http = require('http');
const WebSocket = require('ws');

class AgentServer {
  constructor(port = 4242) {
    this.port = port;
    this.app = express();
    this.server = http.createServer(this.app);
    this.wss = new WebSocket.Server({ server: this.server });
  }

  start() {
    this.initializeHTTP();
    this.initializeWebSocket();
    this.server.listen(this.port, () => {
      console.log(`AgentServer listening on port ${this.port}`);
    });
  }

  initializeHTTP() {
    this.app.use(express.json());
    this.app.post('/message', (req, res) => {
      const message = req.body;
      const transport = new HTTPTransport(res);
      this.handleIncomingMessage(message, transport);
    });
  }

  initializeWebSocket() {
    this.wss.on('connection', (ws) => {
      const transport = new WebSocketTransport(ws);
      ws.on('message', (message) => {
        this.handleIncomingMessage(JSON.parse(message), transport);
      });
    });
  }

  handleIncomingMessage(message, transport) {
    if ('task' in message) {
      this.handleTaskRequest(message, transport);
    } else if ('current_agent_ID' in message) {
      this.handleHandoffNotification(message, transport);
    } else if ('answer' in message) {
      this.handleClarificationResponse(message, transport);
    } else if ('status' in message) {
      this.handleCallbackNotification(message, transport);
    } else {
      const errorMessage = {
        error_message: 'Unknown message type',
        requesting_agent_ID: message.requesting_agent_ID || 'unknown',
      };
      this.sendResponse(errorMessage, transport);
    }
  }

  sendResponse(response, transport) {
    transport.sendResponse(response);
  }

  handleTaskRequest(taskRequest, transport) {
    // To be overridden by child classes
    console.log('Received task request:', taskRequest);
  }

  handleHandoffNotification(handoffNotification, transport) {
    // To be overridden by child classes
    console.log('Received handoff notification:', handoffNotification);
  }

  handleCallbackNotification(callbackNotification, transport) {
    // To be overridden by child classes
    console.log('Received callback notification:', callbackNotification);
  }

  handleClarificationResponse(clarificationResponse, transport) {
    // To be overridden by child classes
    console.log('Received clarification response:', clarificationResponse);
  }
}

class HTTPTransport {
  constructor(res) {
    this.res = res;
  }

  sendResponse(response) {
    this.res.json(response);
  }
}

class WebSocketTransport {
  constructor(ws) {
    this.ws = ws;
  }

  sendResponse(response) {
    this.ws.send(JSON.stringify(response));
  }
}

// Type definitions
/**
 * @typedef {Object} TaskRequest
 * @property {string} task_ID
 * @property {string} task
 * @property {string} requesting_agent_ID
 * @property {string} [callback_URL]
 */

/**
 * @typedef {Object} TaskResponse
 * @property {string} task_ID
 * @property {string} result
 * @property {('success'|'failed'|'in-progress')} status
 * @property {string} replying_agent_ID
 */

/**
 * @typedef {Object} HandoffNotification
 * @property {string} task_ID
 * @property {string} current_agent_ID
 * @property {string} new_agent_ID
 * @property {string} reason_for_handoff
 */

/**
 * @typedef {Object} ClarificationRequest
 * @property {string} task_ID
 * @property {string} question
 * @property {string} requesting_agent_id
 */

/**
 * @typedef {Object} ClarificationResponse
 * @property {string} task_ID
 * @property {string} answer
 * @property {string} replying_agent_id
 */

/**
 * @typedef {Object} CallbackNotification
 * @property {string} task_ID
 * @property {string} result
 * @property {('complete'|'failed'|'in-progress')} status
 * @property {string} requesting_agent_ID
 * @property {string} replying_agent_ID
 */

/**
 * @typedef {Object} ErrorMessage
 * @property {string} [task_ID]
 * @property {string} error_message
 * @property {string} requesting_agent_ID
 */

/**
 * @typedef {Object} TransportInterface
 * @property {function(any): void} sendResponse
 */

module.exports = {
  AgentServer,
  // Export type definitions (these are just for documentation purposes in JavaScript)
  TaskRequest: null,
  TaskResponse: null,
  HandoffNotification: null,
  ClarificationRequest: null,
  ClarificationResponse: null,
  CallbackNotification: null,
  ErrorMessage: null,
  TransportInterface: null,
};