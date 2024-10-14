# Communication Sections

## Shared Message Types

```
Section: Shared Message Types

Define a message type called "TaskRequest" with:
    - task ID
    - task description
    - task data (optional)
    - originating agent ID
    - callback URL (optional)
    - priority level (optional)

Define a message type called "TaskResponse" with:
    - task ID
    - result data
    - status (success, failed, in-progress)
    - agent ID (the agent completing the task)

Define a message type called "HandoffNotification" with:
    - task ID
    - current agent ID
    - new agent ID
    - reason for handoff

Define a message type called "ClarificationRequest" with:
    - task ID
    - question or clarifying data required
    - requested by (agent ID)
    
Define a message type called "ClarificationResponse" with:
    - task ID
    - answer or additional information
    - response provided by (agent ID)

Define a message type called "CallbackNotification" with:
    - task ID
    - result data
    - status (complete, failed, in-progress)
    - sent to (callback URL or agent ID)
    
Define a message type called "ErrorMessage" with:
    - task ID (optional)
    - error message
    - originating agent ID
```

## Transport Interface

```
Section: Shared Transport Interface

To define a transport interface:
    - Create a method to send messages to the server or client.
    - Create a method to receive messages and process them.
    
To implement a WebSocket transport:
    - Establish a WebSocket connection.
    - Send messages via WebSocket.
    - Receive messages and forward them to the appropriate handler.

To implement an HTTP transport:
    - Send HTTP POST requests with message data.
    - Receive responses and handle errors.

To implement any future transport:
    - Ensure the transport can send and receive the standard message types.
    - Follow the same structure for handling communication.
```

## Server-side Transport

```
Section: Server-Side Transport Abstraction

To define the server:
    - Create a transport interface that can listen for incoming messages.
    - Support multiple transports (WebSocket, HTTP, etc.).

To handle incoming message:
    - Parse the message based on its type (TaskRequest, ClarificationRequest, etc.).
    - Route the message to the appropriate handler.
    
To respond to a client:
    - Format the response as TaskResponse or ErrorMessage.
    - Send the response using the same transport (WebSocket, HTTP response, etc.).

Section: Task Handlers

To handle a TaskRequest:
    - Check if the task is valid and within the server’s capabilities.
    - If the task can be processed, assign it to the appropriate agent.
    - If the task requires a handoff, send a HandoffNotification to the client.
    - If clarification is required, send a ClarificationRequest back to the client.

To handle a CallbackNotification:
    - Once the task is complete, forward the result back to the originating agent or callback URL.
    - If the task is incomplete, send a status update (e.g., in-progress).

To handle a ClarificationResponse:
    - Once the clarification is received, update the task context.
    - Resume the task execution or continue processing.

Section: Server Transport Management

To initialize WebSocket server:
    - Listen for WebSocket connections.
    - Process incoming WebSocket messages as described.

To initialize HTTP server:
    - Define REST endpoints for task submission, clarification, handoffs, and callbacks.
    - Process incoming HTTP POST requests as described.
    
To support additional transports:
    - Implement the same interface for any new transport.
```

## Client-side Transport

```
Section: Client-Side Transport Abstraction

To define the client:
    - Create a transport interface to send messages to the server.
    - Support sending task requests, clarifications, handoff notifications, and callbacks.
    
To send a TaskRequest:
    - Format the message using the "TaskRequest" message type.
    - Include task ID, description, data, originating agent, and optional callback URL.
    - Send the request to the server using the defined transport (WebSocket, HTTP, etc.).

To receive a TaskResponse:
    - Listen for server responses (either via WebSocket messages or HTTP responses).
    - Parse the response and act on it.
    
To handle a HandoffNotification:
    - If the task is handed off, update the task state.
    - Optionally re-send the task to the new agent if necessary.

To handle a ClarificationRequest:
    - If a clarification is required, ask the user or another agent for the missing information.
    - Send a ClarificationResponse back to the server once the clarification is provided.

Section: Client Transport Management

To initialize WebSocket client:
    - Connect to the server via WebSocket.
    - Send messages over WebSocket as needed.
    - Listen for server responses in real-time.

To initialize HTTP client:
    - Send POST requests to the server for task submission and clarifications.
    - Handle HTTP responses and error messages.

To support additional transports:
    - Implement the same interface for any new transport.
```

## Agent Management

```
Section: Agent Management

Create a list called "registered agents" that is empty.

To register an agent:
    Parse the incoming message as "TaskRequest".
    If the task description includes the phrase "register me as an agent", then
        Extract the agent ID, capabilities, address, and status from the task description.
        If the agent is not already registered, then
            Add the agent's ID, capabilities, address, and status to the "registered agents" list.
            Display "Agent [agent ID] registered successfully with capabilities: [capabilities]."
            Send a "TaskResponse" back to the agent with status "success" and the result data containing the registration details.
        Otherwise
            Display "Error: Agent with ID [agent ID] is already registered."
            Send a "TaskResponse" back to the agent with status "failed" and an error message.
    Otherwise
        Display "Error: Invalid registration request."
        Send a "TaskResponse" with status "failed" and the message "Invalid registration request."

To lookup an agent:
    Parse the incoming message as "TaskRequest".
    If the task description includes the phrase "find an agent", then
        Extract the capabilities the client is looking for from the task description.
        For each agent in "registered agents",
            If the agent's capabilities include the requested capability and the agent's status is "available", then
                Display "Found agent [agent ID] with capabilities: [capabilities], address: [address]."
                Add the agent's details to a list of available agents.
        If one or more agents are found, then
            Send a "TaskResponse" to the client with status "success" and the result data containing the list of available agents.
        Otherwise
            Display "No available agents found for the requested capabilities."
            Send a "TaskResponse" to the client with status "failed" and an error message "No available agents found."
    Otherwise
        Display "Error: Invalid lookup request."
        Send a "TaskResponse" with status "failed" and the message "Invalid lookup request."
```