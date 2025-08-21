"""
Utility functions for Speechify API integration.
This module provides helper functions for voice selection and testing.
"""

from speechify import Speechify
from speechify.tts import GetSpeechOptionsRequest
import base64
import os
from dotenv import dotenv_values

def filter_voice_models(voices, *, gender=None, locale=None, tags=None):
    """
    Filter Speechify voices by gender, locale, and/or tags,
    and return the list of model IDs for matching voices.

    Args:
        voices (list): List of GetVoice objects.
        gender (str, optional): e.g. 'male', 'female'.
        locale (str, optional): e.g. 'en-US'.
        tags (list, optional): list of tags, e.g. ['timbre:deep', 'use-case:advertisement'].

    Returns:
        list[str]: IDs of matching voice models.
    """
    results = []

    for voice in voices:
        # gender filter
        if gender and voice.gender.lower() != gender.lower():
            continue

        # locale filter (check across models and languages)
        if locale:
            if not any(
                any(lang.locale == locale for lang in model.languages)
                for model in voice.models
            ):
                continue

        # tags filter
        if tags:
            if not all(tag in voice.tags for tag in tags):
                continue

        # If we got here, the voice matches -> collect model ids
        for model in voice.models:
            results.append(model.name)

    return results

def get_available_voices(client=None):
    """
    Get all available voices from Speechify API.
    
    Args:
        client: Speechify client instance. If None, creates one using env token.
    
    Returns:
        list: List of available voice objects
    """
    if client is None:
        env_vars = dotenv_values(".env")
        token = env_vars.get("SpeechifyToken")
        if not token:
            raise ValueError("SpeechifyToken not found in environment variables")
        client = Speechify(token=token)
    
    return client.tts.voices.list()

def list_voices_by_language(language_code="en-US"):
    """
    List all available voices for a specific language.
    
    Args:
        language_code (str): Language code (e.g., "en-US", "fr-FR")
    
    Returns:
        list: List of voice IDs for the specified language
    """
    client = None
    try:
        env_vars = dotenv_values(".env")
        token = env_vars.get("SpeechifyToken")
        if not token:
            print("SpeechifyToken not found in environment variables")
            return []
        
        client = Speechify(token=token)
        voices = get_available_voices(client)
        
        matching_voices = []
        for voice in voices:
            for model in voice.models:
                for lang in model.languages:
                    if lang.locale == language_code:
                        matching_voices.append({
                            'voice_id': voice.voice_id,
                            'name': voice.name,
                            'gender': voice.gender,
                            'tags': voice.tags
                        })
                        break
                if any(lang.locale == language_code for lang in model.languages):
                    break
        
        return matching_voices
    
    except Exception as e:
        print(f"Error listing voices: {e}")
        return []

def test_voice(voice_id, text="Hello, this is a test of the Speechify API.", output_file="test_audio.mp3"):
    """
    Test a specific voice with sample text.
    
    Args:
        voice_id (str): The voice ID to test
        text (str): Text to convert to speech
        output_file (str): Output file path for the audio
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        env_vars = dotenv_values(".env")
        token = env_vars.get("SpeechifyToken")
        if not token:
            print("SpeechifyToken not found in environment variables")
            return False
        
        client = Speechify(token=token)
        
        # Determine language from voice_id
        language = "en-US"
        if "-" in voice_id:
            voice_parts = voice_id.split("-")
            if len(voice_parts) >= 2:
                language = f"{voice_parts[0]}-{voice_parts[1]}"
        
        # Choose model based on language
        model = "simba-english" if language.startswith("en") else "simba-multilingual"
        
        print(f"Testing voice: {voice_id}")
        print(f"Language: {language}")
        print(f"Model: {model}")
        
        # Generate speech
        audio_response = client.tts.audio.speech(
            audio_format="mp3",
            input=text,
            language=language,
            model=model,
            options=GetSpeechOptionsRequest(
                loudness_normalization=True,
                text_normalization=True
            ),
            voice_id=voice_id
        )
        
        # Save audio file
        audio_bytes = base64.b64decode(audio_response.audio_data)
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"Audio saved to: {output_file}")
        print(f"Billable characters: {audio_response.billable_characters_count}")
        return True
        
    except Exception as e:
        print(f"Error testing voice: {e}")
        return False

def get_supported_languages():
    """
    Get list of supported languages with their codes.
    
    Returns:
        dict: Dictionary with language names as keys and codes as values
    """
    return {
        # Fully Supported Languages
        "English": "en",
        "French": "fr-FR", 
        "German": "de-DE",
        "Spanish": "es-ES",
        "Portuguese (Brazil)": "pt-BR",
        "Portuguese (Portugal)": "pt-PT",
        
        # Beta Languages
        "Arabic": "ar-AE",
        "Danish": "da-DK",
        "Dutch": "nl-NL", 
        "Estonian": "et-EE",
        "Finnish": "fi-FI",
        "Greek": "el-GR",
        "Hebrew": "he-IL",
        "Hindi": "hi-IN",
        "Italian": "it-IT",
        "Japanese": "ja-JP",
        "Norwegian": "nb-NO",
        "Polish": "pl-PL",
        "Russian": "ru-RU",
        "Swedish": "sv-SE",
        "Turkish": "tr-TR",
        "Ukrainian": "uk-UA",
        "Vietnamese": "vi-VN"
    }

if __name__ == "__main__":
    print("Speechify Voice Utility")
    print("=" * 30)
    
    # Show supported languages
    languages = get_supported_languages()
    print("\nSupported Languages:")
    for name, code in languages.items():
        print(f"  {name}: {code}")
    
    # Test with a sample voice
    print("\nTesting with English voices...")
    english_voices = list_voices_by_language("en-US")
    
    if english_voices:
        print(f"\nFound {len(english_voices)} English voices:")
        for i, voice in enumerate(english_voices[:5]):  # Show first 5
            print(f"  {i+1}. {voice['name']} ({voice['gender']}) - ID: {voice['voice_id']}")
        
        # Test the first voice
        if english_voices:
            test_voice(english_voices[0]['voice_id'])
    else:
        print("No English voices found or API token not configured.") 