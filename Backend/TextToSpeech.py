import pygame # Import pygame library for handling audio playback.
import random # Import random for generating random choices.
import asyncio # Import asyncio for asynchronous operations.
import os # Import os for file path handling.
from speechify import Speechify
from speechify.tts import GetSpeechOptionsRequest
from dotenv import dotenv_values # import dotenv for reading environment variables from a .env file.

# load environment variables from a .env file.
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")  # Get the assistant's voice from the environment variables.
SpeechifyToken = env_vars.get("SpeechifyToken")  # Get the Speechify API token

# Speechify configuration
DEFAULT_VOICE_ID = "voice_id"  # Default voice ID - should be configured in .env
DEFAULT_MODEL = "simba-english"  # Default model
DEFAULT_LANGUAGE = "en-US"  # Default language

# Initialize Speechify client
def get_speechify_client():
    """Get Speechify client instance"""
    if not SpeechifyToken:
        raise Exception("SpeechifyToken not configured in .env file")
    return Speechify(token=SpeechifyToken)

def get_available_voices():
    """Get available voices from Speechify API"""
    if not SpeechifyToken:
        print("Warning: SpeechifyToken not configured. Using default voice.")
        return []
    
    try:
        client = get_speechify_client()
        voices_response = client.tts.voices.list()
        # The response is directly a list of voice objects
        return voices_response if isinstance(voices_response, list) else []
    except Exception as e:
        print(f"Error getting available voices: {e}")
        return []

def validate_voice_id(voice_id):
    """Validate if the voice ID exists in available voices"""
    if not voice_id:
        return False
    
    available_voices = get_available_voices()
    voice_ids = [voice.id for voice in available_voices if hasattr(voice, 'id')]
    return voice_id in voice_ids

# Asynchronous function to convert text to an audio file using Speechify API.
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"   # Define the path where the speech will be saved.

    if os.path.exists(file_path): # Check if the file already exists.
        os.remove(file_path)      # If it exists, remove it to avoid overwriting errors.

    # Validate voice ID
    voice_id = AssistantVoice if AssistantVoice else DEFAULT_VOICE_ID
    if not validate_voice_id(voice_id):
        print(f"Warning: Voice ID '{voice_id}' not found. Using default voice.")
        voice_id = DEFAULT_VOICE_ID

    try:
        # Get Speechify client
        client = get_speechify_client()
        
        # Create speech options
        options = GetSpeechOptionsRequest(
            loudness_normalization=True,
            text_normalization=True
        )
        
        # Generate speech using the official SDK
        audio_response = client.tts.audio.speech(
            audio_format="mp3",
            input=text,
            language=DEFAULT_LANGUAGE,
            model=DEFAULT_MODEL,
            options=options,
            voice_id=voice_id
        )
        
        # Save the audio data to file
        import base64
        audio_bytes = base64.b64decode(audio_response.audio_data)
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
            
        print(f"Successfully generated speech for text: {text[:50]}...")
            
    except Exception as e:
        print(f"Error in TextToAudioFile: {e}")
        raise e

# Function to manage Text-To-Speech (TTS) functionality.
def TTS (Text, func=lambda r=None: True):
    while True:
        try:
            # Convert text to an audio file asynchronously.
            asyncio.run(TextToAudioFile(Text)) 

            # Initialize pygame mixer for audio playback.
            pygame.mixer.init()

            # Load the generated speech file into pygame mixer.
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()  # Play the audio.

            # Loop until the audio is done playing or the function stops.
            while pygame.mixer.music.get_busy():
                if func() == False:  # Check if the external function returns false.
                    break
                pygame.time.Clock().tick(10)   # Limit the loop for 10 ticks per second.

            return True  # Return True if the audio plays successfully.
        
        except Exception as e:  # Handle any exceptions during the process.
            print (f"Error in TTS: {e}")
            # If it's an authentication error, don't retry
            if "Authentication failed" in str(e):
                return False

        finally:
            try:
                # Call the provided function with False to signal the end of TTS.
                func(False)
                pygame.mixer.music.stop()  # Stop the audio playback.
                pygame.mixer.quit()      # Quit the pygame mixer.

            except Exception as e:  # Handle any exceptions during cleanup.
                print(f"Error in finally block: {e}")

# Function to manage Text-To-Speech with additional responses for long text.
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")   # Split the text by periods into a list of sentences.

    # List of predefined responses for cases where the text is too long.
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out Ma'am.",
        "The rest of the text is now on the chat screen, Ma'am, please check it.",
        "You can see the rest of the text on the chat screen, Ma'am.",
        "The remaining part of the text is now on the chat screen, Ma'am.",
        "Ma'am, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, Ma'am.",
        "Ma'am, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, Ma'am.",
        "The next part of the text is on the chat screen, Ma'am.",
        "Ma'am, please check the chat screen for more information.",
        "There's more text on the chat screen for you, Ma'am.",
        "Ma'am, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, Ma'am.",
        "Ma'am, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, Ma'am.",
        "There's more to see on the chat screen, Ma'am, please look.",
        "Ma'am, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out Ma'am.",
        "Please review the chat screen for the rest of the text, Ma'am.",
        "Ma'am, look at the chat screen for the complete answer."
    ]

    # If the text is very long (more than 4 sentences and 250 characters), add a response message.
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)

    # Otherwise, just play the whole text.
    else:
        TTS(Text,func)

# Function to test Speechify API connection
def test_speechify_connection():
    """Test the Speechify API connection and return available voices"""
    print("Testing Speechify API connection...")
    
    if not SpeechifyToken:
        print("❌ SpeechifyToken not configured in .env file")
        return False
    
    try:
        voices = get_available_voices()
        if voices:
            print(f"✅ Speechify API connection successful. Found {len(voices)} voices.")
            print("Available voices:")
            for voice in voices[:5]:  # Show first 5 voices
                voice_id = getattr(voice, 'id', 'Unknown')
                name = getattr(voice, 'display_name', 'No name')
                print(f"  - {voice_id}: {name}")
            if len(voices) > 5:
                print(f"  ... and {len(voices) - 5} more voices")
            return True
        else:
            print("❌ Failed to connect to Speechify API or no voices available")
            return False
    except Exception as e:
        print(f"❌ Error testing Speechify connection: {e}")
        return False

# Main execution loop
if __name__ == "__main__":
    # Test connection first
    if test_speechify_connection():
        print("\nStarting TTS test mode...")
        while True:
            # Prompt user for input and pass it to Text-To-Speech function.
            TextToSpeech(input("Enter the text: "))
    else:
        print("Please configure SpeechifyToken in your .env file and try again.")

 
 

