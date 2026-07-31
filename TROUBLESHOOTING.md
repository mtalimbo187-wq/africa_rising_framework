# Troubleshooting Guide

## Common Issues & Solutions

### 1. Import Errors

**Error:** `ModuleNotFoundError: No module named 'core.schemas'`

**Solution:**
```bash
# Ensure you're in the project root
cd /path/to/africa_rising_framework

# Install dependencies
pip install pydantic psutil
```

### 2. API Key Issues

**Error:** `KeyError: Environment variable not set: ANTHROPIC_API_KEY`

**Solution:**
```bash
# Set environment variables
export ANTHROPIC_API_KEY="your_key_here"
export ELEVENLABS_API_KEY="your_key_here"

# Or use .env file
source .env
```

### 3. FFmpeg Not Found

**Error:** `FileNotFoundError: ffmpeg command not found`

**Solution:**
```bash
# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Linux (Fedora)
sudo dnf install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
# Add to PATH
```

### 4. Whisper Installation Issues

**Error:** `ModuleNotFoundError: No module named 'whisper'`

**Solution:**
```bash
pip install openai-whisper

# If that fails, use conda:
conda install -c conda-forge openai-whisper
```

### 5. GPU Not Detected

**Error:** GPU-related errors or extremely slow video generation

**Solution:**
```bash
# Check if GPU is available
python3 << 'EOF'
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name()}")
EOF

# Install CUDA drivers (if using NVIDIA)
# Visit: https://developer.nvidia.com/cuda-downloads
```

### 6. Budget Exceeded

**Error:** `CRITICAL: API budget exceeded`

**Solution:**
1. Check current costs:
   ```bash
   tail output/logs/costs.jsonl
   ```

2. Reduce video generation budget in config.yaml:
   ```yaml
   ai_generator:
     max_videos_per_project: 3  # Reduce from default
   ```

3. Use cheaper providers (Grok before Veo):
   ```yaml
   visual_generation:
     provider_preference: ["grok", "runway", "veo"]
   ```

### 7. Script Analysis Fails

**Error:** `Script analysis failed - empty output`

**Solution:**
1. Check script format - should have clear sections
2. Minimum script length: 100 words
3. Use clear markers:
   ```
   # Scene 1: Introduction
   Narration text here...
   
   # Scene 2: Story
   More narration...
   ```

### 8. No Assets Found

**Error:** `Warning: Asset search returned 0 results`

**Solution:**
1. Check API keys for Pexels, Archive.org, etc.
2. Try broader search terms (single words instead of phrases)
3. Enable all asset sources in config.yaml
4. Check internet connection

### 9. Audio Sync Issues

**Error:** Subtitles drift from narration

**Solution:**
1. Check narration duration matches script duration
2. Re-run Captioning Agent with smaller Whisper model:
   ```yaml
   captions:
     whisper:
       model: "tiny"  # Faster, less accurate
   ```

3. Manually adjust subtitle timings in output/captions/

### 10. Video Export Fails

**Error:** `FFmpeg error: Cannot create output file`

**Solution:**
1. Check output directory exists:
   ```bash
   mkdir -p output/projects
   ```

2. Check disk space:
   ```bash
   df -h
   ```

3. Check file permissions:
   ```bash
   chmod 755 output
   ```

## Performance Optimization

### Slow Processing

1. **Reduce quality for faster turnaround:**
   ```yaml
   video_settings:
     resolution: "1024x576"  # Instead of 1280x720
     fps: 24  # Instead of 25
   ```

2. **Use faster AI models:**
   ```yaml
   visual_generation:
     runway:
       enabled: true  # Faster than Veo
     veo:
       enabled: false  # Slower, more cinematic
   ```

3. **Reduce Whisper accuracy for speed:**
   ```yaml
   captions:
     whisper:
       model: "tiny"  # Fastest
   ```

### High Memory Usage

1. **Process in smaller batches:**
   ```yaml
   pipeline:
     batch_size: 3  # Instead of 5
   ```

2. **Use smaller image resolutions:**
   ```yaml
   asset_finder:
     image_size: "small"
   ```

3. **Reduce cache retention:**
   ```yaml
   cache:
     max_size_mb: 500
   ```

## Monitoring & Debugging

### View Logs

```bash
# Real-time logs
tail -f output/logs/application.log

# API calls
cat output/logs/api_calls.jsonl | jq

# Costs breakdown
cat output/logs/costs.jsonl | jq

# Errors
cat output/logs/errors.jsonl | jq
```

### Check Telemetry

```bash
cat output/logs/project_telemetry.json | jq '.total_cost_usd'
```

### Debug Agent Actions

```bash
# See all agent actions
jq '.[] | select(.agent_name=="research_agent")' output/logs/production.jsonl
```

## Getting Help

1. Check error logs: `output/logs/errors.jsonl`
2. Review API responses: `output/logs/api_calls.jsonl`
3. Check telemetry: `output/logs/project_telemetry.json`
4. Read OPERATING_PROCEDURES.md for workflow guidance
