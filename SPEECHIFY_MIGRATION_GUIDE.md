# Speechify Migration Guide

This guide explains the migration from edge-tts to Speechify API in the EVA AI project.

## Changes Made

### 1. Updated Dependencies
- **Removed**: `edge-tts`
- **Added**: `speechify-api`

### 2. Code Changes in `Backend/TextToSpeech.py`

#### Imports Updated:
```python
# Old imports
import edge_tts

# New imports
from speechify import Speechify
from speechify.tts import GetSpeechOptionsRequest
import base64
```

#### Key Function Changes:
- `TextToAudioFile()`: Changed from async function to synchronous function
- Removed edge-tts specific parameters (pitch, rate)
- Added Speechify API integration with proper error handling
- Added language detection and model selection logic

#### New Features:
- Automatic language detection from voice configuration
- Support for both English (`simba-english`) and multilingual (`simba-multilingual`) models
- Proper audio format handling (MP3)
- Base64 decoding of audio response

### 3. Environment Variables

Add the following to your `.env` file:
```
SpeechifyToken = YOUR_SPEECHIFY_API_TOKEN
```

## Installation

1. Install the new dependency:
```bash
pip install speechify-api
```

2. Update your `.env` file with your Speechify API token.

## Voice Configuration

The system now automatically detects the language from your `AssistantVoice` configuration:

- If voice contains language codes (e.g., "en-US-JennyNeural"), it extracts the language
- Uses "simba-english" model for English languages
- Uses "simba-multilingual" model for other languages
- Falls back to "en-US" if no language is detected

## Supported Languages

### Fully Supported:
- English (en)
- French (fr-FR)
- German (de-DE)
- Spanish (es-ES)
- Portuguese Brazil (pt-BR)
- Portuguese Portugal (pt-PT)

### Beta Support:
- Arabic, Danish, Dutch, Estonian, Finnish, Greek, Hebrew, Hindi, Italian, Japanese, Norwegian, Polish, Russian, Swedish, Turkish, Ukrainian, Vietnamese

## Functionality Preserved

All existing functionality has been preserved:
- Text-to-speech conversion
- Audio playback using pygame
- Long text handling with truncation
- Error handling and cleanup
- Callback function support

## Breaking Changes

1. **API Token Required**: You must now provide a Speechify API token
2. **Voice Format**: Voice IDs may need to be updated to match Speechify's voice format
3. **Synchronous Operation**: The `TextToAudioFile` function is now synchronous instead of async

## Troubleshooting

### Common Issues:

1. **Missing API Token**: Ensure `SpeechifyToken` is set in your `.env` file
2. **Voice Not Found**: Update `AssistantVoice` to use a valid Speechify voice ID
3. **Language Issues**: Check that your language code is supported by Speechify

### Error Messages:
- "SpeechifyToken not found in environment variables" - Add your API token to `.env`
- "Error in TextToAudioFile" - Check your API token and voice configuration

## Testing

To test the migration:

1. Set up your Speechify API token
2. Run the TextToSpeech module directly:
```bash
python Backend/TextToSpeech.py
```

3. Enter test text to verify audio generation and playback works correctly.

## Migration Checklist

- [ ] Install speechify-api: `pip install speechify-api`
- [ ] Add SpeechifyToken to `.env` file
- [ ] Update AssistantVoice to use valid Speechify voice ID
- [ ] Test text-to-speech functionality
- [ ] Verify audio playback works correctly
- [ ] Test with different languages if needed 