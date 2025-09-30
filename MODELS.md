# OpenRouter Model Options

The `-m` / `--model` flag allows you to specify which LLM model to use via OpenRouter.

## Usage

```bash
python run_classification.py "your subject" -m "model-id"
python run_classification.py "your subject" --model "model-id" --stream
```

## Popular Models

### Free Models (Good for Testing)

| Model ID | Provider | Notes |
|----------|----------|-------|
| `x-ai/grok-2-1212` | xAI | **Default** - Fast, good reasoning |
| `google/gemini-2.0-flash-exp:free` | Google | Very fast, experimental |
| `meta-llama/llama-3.2-3b-instruct:free` | Meta | Smaller, faster |
| `mistralai/mistral-7b-instruct:free` | Mistral | Good balance |
| `nousresearch/hermes-3-llama-3.1-405b:free` | Nous | Large, capable |

### Paid Models (High Quality)

| Model ID | Provider | Cost | Notes |
|----------|----------|------|-------|
| `anthropic/claude-3.5-sonnet` | Anthropic | $$$ | Excellent reasoning, best quality |
| `anthropic/claude-3-haiku` | Anthropic | $ | Fast, cost-effective |
| `openai/gpt-4o` | OpenAI | $$$ | Strong performance |
| `openai/gpt-4o-mini` | OpenAI | $ | Good balance of cost/quality |
| `google/gemini-pro-1.5` | Google | $$ | Good reasoning, large context |
| `x-ai/grok-2-vision-1212` | xAI | $$ | Vision + reasoning |

### Specialized Models

| Model ID | Provider | Notes |
|----------|----------|-------|
| `perplexity/llama-3.1-sonar-huge-128k-online` | Perplexity | Online search capability |
| `anthropic/claude-3-opus` | Anthropic | Most capable, expensive |
| `cohere/command-r-plus` | Cohere | RAG-optimized |

## Examples

### Test with Free Model
```bash
python run_classification.py "constitutional law" -m "google/gemini-2.0-flash-exp:free"
```

### Best Quality (Paid)
```bash
python run_classification.py "quantum physics" -m "anthropic/claude-3.5-sonnet" --stream
```

### Cost-Effective (Paid)
```bash
python run_classification.py "library science" -m "openai/gpt-4o-mini"
```

### Fast Free Alternative
```bash
python run_classification.py "ancient history" -m "meta-llama/llama-3.2-3b-instruct:free" --verbose
```

## Model Selection Tips

### For Classification Tasks (DDC)

**Best overall**: `anthropic/claude-3.5-sonnet`
- Excellent at structured reasoning
- Strong JSON output
- Great at following complex instructions

**Best free**: `x-ai/grok-2-1212` (default)
- Good reasoning capabilities
- Fast responses
- Handles complex prompts well

**Most cost-effective paid**: `openai/gpt-4o-mini`
- Good quality at lower cost
- Fast
- Reliable JSON output

**Fastest**: `google/gemini-2.0-flash-exp:free`
- Very fast responses
- Free tier available
- Good for testing/iteration

### For Different Use Cases

**Complex multi-step reasoning**: `anthropic/claude-3.5-sonnet`, `openai/gpt-4o`

**Speed priority**: `google/gemini-2.0-flash-exp:free`, `anthropic/claude-3-haiku`

**Budget-friendly testing**: `x-ai/grok-2-1212`, `mistralai/mistral-7b-instruct:free`

**Large context needed**: `google/gemini-pro-1.5` (2M tokens), `anthropic/claude-3.5-sonnet` (200K tokens)

## Checking Available Models

Visit OpenRouter's model list:
https://openrouter.ai/models

Or check pricing:
https://openrouter.ai/docs#models

## API Key Setup

1. Sign up at https://openrouter.ai/
2. Get your API key from https://openrouter.ai/keys
3. Create `detective_systemv3/api.txt` with your key:
   ```
   sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

Or set environment variable:
```bash
export OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Cost Estimates (Approximate)

For a typical classification task (~5 rounds, ~10K tokens total):

- **Free models**: $0.00
- **gpt-4o-mini**: ~$0.002-0.005
- **claude-3-haiku**: ~$0.005-0.01
- **gpt-4o**: ~$0.02-0.05
- **claude-3.5-sonnet**: ~$0.03-0.08
- **claude-3-opus**: ~$0.10-0.20

## Troubleshooting

### Model not found
```
Error: Model 'xyz' not found
```
→ Check spelling, visit https://openrouter.ai/models for valid IDs

### Rate limits
```
Error: Rate limit exceeded
```
→ Wait a moment or upgrade your OpenRouter plan

### Insufficient credits
```
Error: Insufficient credits
```
→ Add credits to your OpenRouter account

### Model-specific issues

Some models may not support:
- Streaming (remove `--stream` flag)
- JSON mode (model will still work, just less structured)
- Large context (reduce `--max-rounds` or query size)

---
Last updated: 2025-09-30
