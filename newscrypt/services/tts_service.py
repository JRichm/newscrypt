import os
import re
import random
from typing import Optional

from newscrypt.config import (
    OUTPUT_DIR,
    OPENAI_API_KEY,
    ELEVENLABS_API_KEY,
    AZURE_SPEECH_KEY,
    AZURE_REGION
)

# optional imports
try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
    elevenlabs_available = True
except ImportError:
    elevenlabs_available = False

try:
    from gtts import gTTS
    gtts_available = True
except ImportError:
    gtts_available = False

try:
    import azure.cognitiveservices.speech as speechsdk
    azure_available = True
except ImportError:
    azure_available = False


class TTSService:
    """Service for generating text-to-speech audio"""

    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY) if (OPENAI_API_KEY and openai_available) else None
        self.elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY) if (ELEVENLABS_API_KEY and elevenlabs_available) else None

    
    def generate_tts(self, script_text: str) -> Optional[str]:
        """Generate text-to-speech audio using the best available method"""
        
        if not script_text:
            return None
        
        methods = [
            ("ElevenLabs", self._generate_tts_elevenlabs),
            ("OpenAI TTS", self._generate_tts_openai),
            ("Azure Neural Voices", self._generate_tts_azure),
            ("Google TTS", self._generate_tts_gtts)
        ]


        for method_name, method_func in methods:
            print(f"Trying {method_name}...")
            result = method_func(script_text)
        
            if result:
                print(f"Successfully generated audio using {method_name}")
                return result
            else:
                print(f"{method_name} not available or failed")

        print("All TTS generators not available or failed!")
        return None
    

    def _clean_script(self, script_text: str) -> str:
        """Clean text for TTS processing"""

        return re.sub(r'[^\w\s.,!?-]', '', script_text)
    

    def _generate_audio_path(self, extension: str = "mp3") -> str:
        """Generate a unique audio file path"""

        return os.path.join(OUTPUT_DIR, f"audio_{random.randint(1000, 9999)}.{extension}")
    

    def _generate_tts_openai(self, script_text: str) -> Optional[str]:
        """Generate TTS using OpenAI's API"""

        if not self.openai_client or not openai_available:
            return None
        
        try:
            clean_script = self._clean_script(script_text)
            audio_path = self._generate_audio_path("mp3")

            with self.openai_client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="alloy",
                input=clean_script,
                speed=1,
            ) as response:
                response.stream_to_file(audio_path)

            return audio_path
        
        except Exception as e:
            print(f"Error generating OpenAI TTS: {e}")
            return None
    

    def _generate_tts_elevenlabs(self, script_text: str) -> Optional[str]:
        """Generate TTS using ElevenLabs API"""

        if not self.elevenlabs_client or not elevenlabs_available:
            return None
        
        try:
            clean_script = self._clean_script(script_text)

            audio = self.elevenlabs_client.text_to_speech.convert(
                text=clean_script,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )

            audio_path = self._generate_audio_path('mp3')
            save(audio, audio_path)
            return audio_path
        
        except Exception as e:
            print(f"Error generating ElevenLabs TTS: {e}")
            return None
        
    
    def _generate_tts_azure(self, script_text: str) -> Optional[str]:
        """Generate TTS using Azure Cognitive Services"""
        
        if not azure_available or not AZURE_SPEECH_KEY:
            return None
        
        try:
            clean_script = self._clean_script(script_text)
            
            speech_config = speechsdk.SpeechConfig(
                subscription=AZURE_SPEECH_KEY, 
                region=AZURE_REGION
            )
            speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
            
            audio_path = self._generate_audio_path("wav")
            audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, 
                audio_config=audio_config
            )
            result = synthesizer.speak_text_async(clean_script).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return audio_path
            else:
                print(f"Azure TTS failed: {result.reason}")
                return None
                
        except Exception as e:
            print(f"Error generating Azure TTS: {e}")
            return None
    

    def _generate_tts_gtts(self, script_text: str) -> Optional[str]:
        """Generate TTS using Google Text-to-Speech"""
        
        if not gtts_available:
            return None
        
        try:
            clean_script = self._clean_script(script_text)
            tts = gTTS(text=clean_script, lang='en', slow=False)
            
            audio_path = self._generate_audio_path("mp3")
            tts.save(audio_path)
            return audio_path
            
        except Exception as e:
            print(f"Error generating gTTS: {e}")
            return None
