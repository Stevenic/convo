# OpenAI Sections

This is a collection of reusable sections for calling OpenAI models and services.

## LLM Calls

Here's a section that's adds basic support for calling OpenAI models.

```
Section: LLM Support

Use OpenAI for LLM support:
    - Add a configuration setting for specifying the API key (hidden). Link for creating keys is https://platform.openai.com/api-keys
    - Add a configuration setting for specifying the chat completion model: 
        - chatgpt-4o-latest (default)
        - gpt-4o-mini
        - o1-preview
        - o1-mini
    - Note that o1-preview and o1-mini don't support "system" messages or settings like "temperature".
```

If using JavaScript or TypeScript, append the follwing instruction to ensure proper usage of fetch() for model calls.

```
    - Use fetch() to POST to the https://api.openai.com/v1/chat/completions endpoint.
```
