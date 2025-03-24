from typing import Optional
import logging
import os
import tempfile
from transformers import pipeline
import torch
from google.translationapi import translate_client
from gtts import gTTS

logger = logging.getLogger(__name__)

class TTSConverter:
    """
    Class for converting text to speech in Hindi.
    """
    
    def __init__(self, use_huggingface: bool = True):
        """
        Initialize the TTSConverter instance.
        
        Args:
            use_huggingface: Whether to use Hugging Face models for TTS.
                             Falls back to gTTS if False or if HF fails.
        """
        self.use_huggingface = use_huggingface
        self.tts_model = None
        self.translator = None
        
        # Initialize translation service
        try:
            # Attempt to use Google Translate API if credentials are available
            self.translator = translate_client.Client()
            logger.info("Google Translation Client initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Google Translation Client: {str(e)}")
            logger.info("Will use fallback translation methods")
            self.translator = None
        
        # Initialize TTS model if using Hugging Face
        if use_huggingface:
            try:
                logger.info("Loading Hugging Face TTS model for Hindi")
                model_name = "facebook/mms-tts-hin"  # Hindi TTS model
                self.tts_model = pipeline("text-to-speech", model=model_name)
                logger.info("Hugging Face TTS model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Hugging Face TTS model: {str(e)}")
                logger.info("Falling back to gTTS")
                self.use_huggingface = False
    
    def translate_to_hindi(self, text: str) -> str:
        """
        Translate text to Hindi.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text in Hindi
        """
        try:
            if self.translator:
                # Use Google Translate API
                result = self.translator.translate(text, target_language='hi')
                return result['translatedText']
            else:
                # Fallback to simplified approach
                # This is just a demonstration - in a real app, you'd use a proper translation service
                logger.warning("Using fallback translation method - limited vocabulary")
                
                # Very basic word mapping for demonstration purposes only
                basic_translation = {
                    "positive": "सकारात्मक",
                    "negative": "नकारात्मक",
                    "neutral": "तटस्थ",
                    "news": "समाचार",
                    "analysis": "विश्लेषण",
                    "company": "कंपनी",
                    "market": "बाज़ार",
                    "stocks": "शेयर",
                    "growth": "विकास",
                    "decline": "गिरावट"
                }
                
                # Replace known words
                result = text
                for eng, hindi in basic_translation.items():
                    result = result.replace(eng, hindi)
                
                return result
        
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            # Return original text with a note
            return text + " (Translation failed)"
    
    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Convert text to Hindi speech and save to a file.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file. If None, a temporary file is created.
            
        Returns:
            Path to the generated audio file
        """
        # Translate text to Hindi
        hindi_text = self.translate_to_hindi(text)
        
        if not output_path:
            # Create temporary file
            fd, output_path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)
        
        try:
            if self.use_huggingface and self.tts_model:
                # Use Hugging Face TTS model
                logger.info("Generating speech using Hugging Face TTS model")
                speech = self.tts_model(hindi_text)
                
                # Save audio to file
                with open(output_path, 'wb') as f:
                    f.write(speech['bytes'])
                
            else:
                # Use gTTS
                logger.info("Generating speech using gTTS")
                tts = gTTS(text=hindi_text, lang='hi', slow=False)
                tts.save(output_path)
            
            logger.info(f"Speech generated and saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            
            # Fallback to gTTS if Hugging Face fails
            if self.use_huggingface:
                logger.info("Falling back to gTTS")
                try:
                    tts = gTTS(text=hindi_text, lang='hi', slow=False)
                    tts.save(output_path)
                    logger.info(f"Speech generated using fallback method and saved to {output_path}")
                    return output_path
                except Exception as fallback_e:
                    logger.error(f"Fallback TTS error: {str(fallback_e)}")
            
            # If all methods fail, return empty string
            return ""