const fs = require('fs');
const path = require('path');
const { AgentServer } = require('../AgentServer/AgentServer.js');

class DirectoryAgent extends AgentServer {
    constructor() {
        super();
        this.registered_agents = [];
        this.loadAgents();
        console.log("Directory Agent initialized.");
    }

    handleTaskRequest(taskRequest, transport) {
        console.log(`Received task: ${taskRequest.task}`);
        if (taskRequest.task.includes("register me as an agent")) {
            this.registerAgent(taskRequest, transport);
        } else if (taskRequest.task.includes("find an agent")) {
            this.lookupAgent(taskRequest, transport);
        } else {
            const response = {
                task_ID: taskRequest.task_ID,
                result: "Task not supported.",
                status: "failed",
                replying_agent_ID: "DirectoryAgent"
            };
            this.sendResponse(response, transport);
        }
    }

    registerAgent(taskRequest, transport) {
        const agentDetails = this.extractAgentDetails(taskRequest.task);
        if (this.registered_agents.some(agent => agent.agent_ID === agentDetails.agent_ID)) {
            const errorMessage = {
                task_ID: taskRequest.task_ID,
                error_message: "Agent ID already registered.",
                requesting_agent_ID: taskRequest.requesting_agent_ID
            };
            this.sendResponse(errorMessage, transport);
        } else {
            this.registered_agents.push(agentDetails);
            this.saveAgents();
            console.log(`Agent ${agentDetails.agent_ID} registered successfully.`);
            const response = {
                task_ID: taskRequest.task_ID,
                result: JSON.stringify(agentDetails),
                status: "success",
                replying_agent_ID: "DirectoryAgent"
            };
            this.sendResponse(response, transport);
        }
    }

    lookupAgent(taskRequest, transport) {
        const requestedCapabilities = this.extractCapabilities(taskRequest.task);
        const availableAgents = this.registered_agents.filter(agent => 
            agent.status === "available" && 
            requestedCapabilities.every(cap => agent.capabilities.includes(cap))
        );

        if (availableAgents.length > 0) {
            const response = {
                task_ID: taskRequest.task_ID,
                result: JSON.stringify(availableAgents),
                status: "success",
                replying_agent_ID: "DirectoryAgent"
            };
            this.sendResponse(response, transport);
        } else {
            const response = {
                task_ID: taskRequest.task_ID,
                result: "No available agents found.",
                status: "failed",
                replying_agent_ID: "DirectoryAgent"
            };
            this.sendResponse(response, transport);
        }
    }

    extractAgentDetails(task) {
        const details = {};
        details.agent_ID = task.match(/ID (\w+)/)[1];
        details.capabilities = task.match(/capabilities '([^']+)'/)[1].split(', ');
        details.address = task.match(/address '([^']+)'/)[1];
        details.status = task.match(/status '([^']+)'/)[1];
        return details;
    }

    extractCapabilities(task) {
        return task.match(/perform (.+)/)[1].split(', ');
    }

    loadAgents() {
        const agentsDir = path.join(__dirname, 'agents');
        if (!fs.existsSync(agentsDir)) {
            fs.mkdirSync(agentsDir);
        }
        const files = fs.readdirSync(agentsDir);
        files.forEach(file => {
            const agentData = JSON.parse(fs.readFileSync(path.join(agentsDir, file), 'utf8'));
            this.registered_agents.push(agentData);
        });
    }

    saveAgents() {
        const agentsDir = path.join(__dirname, 'agents');
        this.registered_agents.forEach(agent => {
            fs.writeFileSync(path.join(agentsDir, `${agent.agent_ID}.json`), JSON.stringify(agent));
        });
    }
}

// Start the DirectoryAgent instance
const directoryAgent = new DirectoryAgent();
directoryAgent.start();

module.exports = { DirectoryAgent };