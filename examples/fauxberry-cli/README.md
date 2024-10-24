# fauxberry CLI

A Node.js CLI application that implements a "fauxberry" style thinking loop using Anthropic's Claude AI model. This tool helps break down complex tasks into smaller reasoning steps before providing a final response. It simulates a stripped down version of the reasoning loop found in OpenAI's o1 family of models.

## Features

- Implements the fauxberry thinking methodology
- Supports Claude 3.5 and other Anthropic models
- Accepts tasks via command line or file input
- Configurable API key via environment variable or command line
- Detailed step-by-step reasoning process
- Customizable model selection

## Installation

### Global Installation

```bash
npm install -g fauxberry-cli
```

### Local Installation

```bash
git clone https://github.com/Stevenic/convo.git
cd convo/examples/fauxberry-cli
npm install
```

## Configuration

Before using fauxberry, you need an Anthropic API key. You can provide it in two ways:

1. Environment variable:
   Create a `.env` file in the project root:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

2. Command line argument:
   ```bash
   fauxberry-cli --apiKey "your_anthropic_api_key"
   ```

## Usage

### Basic Usage

```bash
fauxberry-cli --task "count backwards from 100 to 1 skipping every 3rd and 14th number"
```

### Using a File Input

```bash
fauxberry-cli --file "path/to/task.txt"
```

### Specifying a Different Model

```bash
fauxberry-cli --task "Your task" --model "claude-3-5-sonnet-20240620"
```

### Command Line Options

```
Options:
  --apiKey, -k     Anthropic API key                             [string]
  --model, -m      Model to use                                  [string] [default: "claude-3-5-sonnet-20241022"]
  --task, -t       Task to perform                               [string]
  --file, -f       File containing the task                      [string]
  --help           Show help                                     [boolean]
```

## Example

```bash
$ fauxberry-cli --task "count backwards from 100 to 1 skipping every 3rd and 14th number"
```