# NVIDIA NIM Setup Guide

## Getting Your API Key

1. Go to https://build.nvidia.com/explore
2. Sign in or create an NVIDIA account
3. Navigate to "API Catalog" or "Models"
4. Select a model (e.g., Llama 3.1, Nemotron, etc.)
5. Click "Get API Key" or "Generate API Key"
6. Copy your API key

## Configuration

### Option 1: Environment Variable (Recommended)

```bash
# Windows Command Prompt
set NVIDIA_API_KEY=your_api_key_here

# Windows PowerShell
$env:NVIDIA_API_KEY="your_api_key_here"

# Linux/Mac
export NVIDIA_API_KEY=your_api_key_here
```

### Option 2: Config File

Create `~/.capybara/config.yaml`:

```yaml
llm:
  provider: nvidia
  model: llama-3.1-405b
  api_key: your_api_key_here
```

### Option 3: Command Line

```bash
capybara --model nvidia/llama-3.1-405b
```

## Available Models

| Model Name | Description |
|------------|-------------|
| llama-3.1-405b | Meta Llama 3.1 405B Instruct |
| llama-3.1-70b | Meta Llama 3.1 70B Instruct |
| llama-3.1-8b | Meta Llama 3.1 8B Instruct |
| nemotron-4-340b | NVIDIA Nemotron 4 340B |
| mixtral-8x22b | Mistral Mixtral 8x22B |
| mixtral-8x7b | Mistral Mixtral 8x7B |
| gemma-2-27b | Google Gemma 2 27B |
| gemma-2-9b | Google Gemma 2 9B |
| phi-3 | Microsoft Phi-3 Medium |

## Testing Your Setup

```bash
# Set your API key
set NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxx

# Run Capybara with NVIDIA
python -m capybara_cli --model nvidia/llama-3.1-405b
```

## Troubleshooting

### Error 401 Unauthorized
- API key is missing or invalid
- Check that `NVIDIA_API_KEY` is set correctly
- Verify key at https://build.nvidia.com/explore

### Error 404 Not Found
- Model name might be incorrect
- Use one of the model names listed above

### Rate Limits
- Free tier has rate limits
- Check your usage at https://build.nvidia.com/user
- Consider upgrading for higher limits
