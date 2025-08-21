import pygame # Import pygame library for handling audio playback.
import random # Import random for generating random choices.
import asyncio # Import asyncio for asynchronous operations.
import os # Import os for file path handling.
from dotenv import dotenv_values # import dotenv for reading environment variables from a .env file.
from speechify import Speechify
from speechify.tts import GetSpeechOptionsRequest
import base64

# load environment variables from a .env file.
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")  # Get the assistant's voice from the environment variables.
SpeechifyToken = env_vars.get("SpeechifyToken")  # Get the Speechify API token from environment variables.

# Initialize Speechify client
def get_speechify_client():
    """Initialize and return Speechify client with API token."""
    if not SpeechifyToken:
        raise ValueError("SpeechifyToken not found in environment variables")
    return Speechify(token=SpeechifyToken)

# Function to convert text to an audio file using Speechify API.
def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"   # Define the path where the speech will be saved.

    if os.path.exists(file_path): # Check if the file already exists.
        os.remove(file_path)      # If it exists, remove it to avoid overwriting errors.

    try:
        # Get Speechify client
        client = get_speechify_client()
        
        # Determine language and model based on AssistantVoice
        # Default to English if no specific language is detected
        language = "en-US"
        model = "simba-english"
        
        # If AssistantVoice contains language codes, extract them
        if AssistantVoice and "-" in AssistantVoice:
            # Extract language code from voice (e.g., "en-US-JennyNeural" -> "en-US")
            voice_parts = AssistantVoice.split("-")
            if len(voice_parts) >= 2:
                language = f"{voice_parts[0]}-{voice_parts[1]}"
        
        # Use multilingual model for non-English languages
        if not language.startswith("en"):
            model = "simba-multilingual"
        
        # Generate speech using Speechify API
        audio_response = client.tts.audio.speech(
            audio_format="mp3",
            input=text,
            language=language,
            model=model,
            options=GetSpeechOptionsRequest(
                loudness_normalization=True,
                text_normalization=True
            ),
            voice_id=AssistantVoice if AssistantVoice else "default"
        )
        
        # Decode the audio data and save to file
        audio_bytes = base64.b64decode(audio_response.audio_data)
        
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
            
    except Exception as e:
        print(f"Error in TextToAudioFile: {e}")
        raise

# Function to manage Text-To-Speech (TTS) functionality.
def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            # Convert text to an audio file.
            TextToAudioFile(Text) 

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
            print(f"Error in TTS: {e}")

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
        TTS(Text, func)

# Main execution loop
if __name__ == "__main__":
    while True:
        # Prompt user for input and pass it to Text-To-Speech function.
        TextToSpeech(input("Enter the text: "))

 
 

