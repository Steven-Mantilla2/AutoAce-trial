import os
import time
import json
from enum import Enum
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# 1. Pydantic Schemas
# -----------------------------------------------------------------------------
class EmotionalTone(str, Enum):
    neutral = "neutral"
    satisfied = "satisfied"
    frustrated = "frustrated"
    upset = "upset"
    distressed = "distressed"

class EmotionalIntensity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class NoiseSeverity(str, Enum):
    none = "none"
    low = "low"
    medium = "medium"
    high = "high"

class AudioQuality(str, Enum):
    clear = "clear"
    slightly_impaired = "slightly_impaired"
    severely_impaired = "severely_impaired"

class AudioAnalysisOutput(BaseModel):
    emotional_tone: EmotionalTone
    emotional_intensity: EmotionalIntensity
    background_noise_present: bool
    background_noise_type: str = Field(default="", description="Empty string if no noise present")
    background_noise_severity: NoiseSeverity
    audio_quality: AudioQuality
    speaker_overlap_present: bool
    long_silence_present: bool
    confidence: float = Field(ge=0.0, le=1.0)

# -----------------------------------------------------------------------------
# 2. Optimized Pipeline Function
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = """
Role: You are an expert Audio Quality Assurance AI analyzing customer support calls. Extract objective acoustic, emotional, and structural metadata from the audio clip.

EVALUATION BENCHMARKS:

1. emotional_tone:
   - 'upset': High vocal strain, sharp pitch inflections, sudden volume spikes, or open vocal distress.
   - 'frustrated': Audible impatience, sighing, abrupt cadence, exasperated tone, or hostile language/insults (regardless of volume or language).
   - 'neutral': Baseline classification. Standard conversational pace, steady monotone or polite pitch, and calm dialogue.
   - 'satisfied': Warm pitch inflections, relaxed cadence, polite laughter, or clear verbal resolution.
   - 'distressed': Crying, hyperventilating, or unmonitored emotional outbursts.

2. emotional_intensity:
   - 'high': Sharp decibel spikes, shouting, severe voice cracking, or direct profanity/hostility.
   - 'medium': Noticeable vocal tension, repeated sighing, or clear shifts in pacing and emphasis.
   - 'low': Strictly flat, calm, standard conversational volume and cadence.

3. background_noise_present & background_noise_type:
   - Detect background audio distinct from the primary speakers (e.g., 'TV', 'static', 'chatter', 'traffic').
   - CRITICAL SCHEMA RULE: If background_noise_present is false, background_noise_type MUST be "".

4. speaker_overlap_present: True ONLY if multiple distinct voices talk over each other.
5. long_silence_present: True ONLY if continuous dead air exceeds 2 consecutive seconds.

GENERALIZED RULES:
- Evaluate tone based on overall vocal energy, pitch stability, and semantic intent.
- Do not ignore low-volume profanity or subtle insults; hostile words reflect frustration regardless of amplitude.
- Rapid volume increases or persistent raised speech indicate high intensity.
"""

def analyze_audio(file_path: str, api_key: str):
    clean_key = api_key.strip()
    client = genai.Client(api_key=clean_key)
    
    mime_type = "audio/ogg" if file_path.lower().endswith(".ogg") else None
    
    # Upload file to Google Files API
    uploaded_file = client.files.upload(
        file=file_path,
        config=types.UploadFileConfig(mime_type=mime_type) if mime_type else None
    )
    
    max_retries = 3
    retry_delay = 21  # Reset delay for 429 quota limits
    
    try:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=[uploaded_file, SYSTEM_PROMPT],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AudioAnalysisOutput,
                        temperature=0.0,
                    ),
                )
                
                # Parse structured output safely
                if hasattr(response, "text") and response.text:
                    return json.loads(response.text)
                elif hasattr(response, "parsed") and response.parsed:
                    return response.parsed.model_dump()
                else:
                    raise ValueError("Empty response received from Gemini API.")

            except Exception as e:
                # Handle Rate Limiting (429) cleanly with retry logic
                if "429" in str(e) and attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise e
    finally:
        # Guarantee cleanup of remote temporary file
        try:
            client.files.delete(name=uploaded_file.name)
        except Exception:
            pass