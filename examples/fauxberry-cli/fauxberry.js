#!/usr/bin/env node

const axios = require('axios');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');
const fs = require('fs').promises;
require('dotenv').config();

const argv = yargs(hideBin(process.argv))
  .option('apiKey', {
    alias: 'k',
    type: 'string',
    description: 'Anthropic API key'
  })
  .option('model', {
    alias: 'm',
    type: 'string',
    default: 'claude-3-5-sonnet-20241022',
    description: 'Model to use'
  })
  .option('task', {
    alias: 't',
    type: 'string',
    description: 'Task to perform'
  })
  .option('file', {
    alias: 'f',
    type: 'string',
    description: 'File containing the task'
  })
  .help()
  .argv;

async function sendMessageToClaude(task, messages, apiKey, model) {
  try {
    // Create the system message
    const system = `<TASK>\n${task}\n\n<INSTRUCTIONS>\nSlow down your thinking by breaking complex questions into multiple reasoning steps.\nEach individual reasoning step should be brief.\nReturn <DONE> after the last step.`;

    const response = await axios.post('https://api.anthropic.com/v1/messages', {
      model,
      system,
      max_tokens: 8182,
      messages
    }, {
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
      }
    });

    return response.data.content[0].text;
  } catch (error) {
    console.error('Error sending message to Claude:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
    }
    process.exit(1);
  }
}

async function thinkingLoop(task, apiKey, model) {
  const conversationHistory = [];
  let continueLoop = true;

  while (continueLoop) {
    // Add user message to conversation history
    conversationHistory.push({
      role: 'user',
      content: 'Think about your next reasoning step to perform the TASK. Return just the next step.'
    });
    
    // Get response from Claude
    const response = await sendMessageToClaude(task, conversationHistory, apiKey, model);
    
    // Add assistant's response to conversation history
    conversationHistory.push({
      role: 'assistant',
      content: response
    });

    console.log('Assistant:', response); // Log each step

    if (response.includes('<DONE>')) {
      continueLoop = false;
    }
  }

  return conversationHistory;
}

async function completeTask(task, apiKey, model) {
  // Run the thinking loop
  const conversationHistory = await thinkingLoop(task, apiKey, model);
  
  // Add final completion request
  conversationHistory.push({
    role: 'user',
    content: 'Complete the <TASK>. Do not return <DONE>.'
  });

  // Get final response
  const finalResponse = await sendMessageToClaude(task, conversationHistory, apiKey, model);
  
  // Print final response
  console.log('\nFinal Response:');
  console.log(finalResponse);
}

async function main() {
  const apiKey = argv.apiKey || process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.error('API key is required. Provide it via --apiKey or ANTHROPIC_API_KEY environment variable.');
    process.exit(1);
  }

  let task;
  if (argv.file) {
    task = await fs.readFile(argv.file, 'utf-8');
  } else if (argv.task) {
    task = argv.task;
  } else {
    console.error('Task is required. Provide it via --task or --file.');
    process.exit(1);
  }

  await completeTask(task, apiKey, argv.model);
}

main().catch(console.error);