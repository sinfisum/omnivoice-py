import os
import logging
import tempfile
import soundfile as sf
import torch
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
from io import BytesIO
from omnivoice import OmniVoice, OmniVoiceGenerationConfig

# --- Configuration ---
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
LOCAL_MODEL_PATH = "./model/OmniVoice"
HF_CHECKPOINT = "k2-fsa/OmniVoice"
HOST = "127.0.0.1"
PORT = 8880

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# --- Determine model source ---
if os.path.isdir(LOCAL_MODEL_PATH) and os.path.isfile(os.path.join(LOCAL_MODEL_PATH, "config.json")):
    CHECKPOINT = LOCAL_MODEL_PATH
    logger.info(f"Local model found at {LOCAL_MODEL_PATH}")
else:
    CHECKPOINT = HF_CHECKPOINT
    logger.info(f"Local model not found, loading from HuggingFace Hub: {HF_CHECKPOINT}")

# --- Model Loading ---
logger.info(f"Loading OmniVoice model from {CHECKPOINT}...")

model = OmniVoice.from_pretrained(
    CHECKPOINT,
    device_map='cuda' if torch.cuda.is_available() else 'cpu',
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    load_asr=True,
    token=False,
)

sampling_rate = model.sampling_rate
logger.info(f"✅ Model loaded successfully! Sampling rate: {sampling_rate} Hz")
logger.info(f"Using device: {'CUDA GPU' if torch.cuda.is_available() else 'CPU'}")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="OmniVoice TTS API",
    description="Zero-Shot TTS with Voice Cloning - 600+ Languages",
    version="0.1.1"
)

# --- Generation Config Defaults ---
DEFAULT_GEN_CONFIG = OmniVoiceGenerationConfig(
    num_step=32,
    guidance_scale=3.0,
    denoise=0.8,
    preprocess_prompt=True,
    postprocess_output=True,
)

@app.post("/v1/audio/speech/clone", summary="Clone voice from reference audio")
async def clone_voice(
    text: str = Form(..., description="Text to synthesize into speech"),
    ref_text: str = Form("", description="Optional transcript of reference audio"),
    ref_audio: UploadFile = File(..., description="Reference audio file (3-10 seconds recommended)"),
    language: str = Form(None, description="Language code (optional, auto-detected if not provided)"),
    speed: float = Form(1.0, description="Speech speed multiplier (0.5 to 2.0)"),
):
    """
    Generate speech with cloned voice from reference audio.
    
    - Accepts text, reference audio file and optional reference text
    - Returns generated audio as WAV file
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if not ref_audio:
        raise HTTPException(status_code=400, detail="Reference audio is required")

    try:
        # Save reference audio temporarily
        ref_audio_bytes = await ref_audio.read()
        
        fd, ref_audio_path = tempfile.mkstemp(suffix=".wav")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(ref_audio_bytes)
            
            # Create voice clone prompt
            voice_prompt = model.create_voice_clone_prompt(
                ref_audio=ref_audio_path,
                ref_text=ref_text.strip() if ref_text else None,
            )
        finally:
            # Clean up temp file
            try:
                os.unlink(ref_audio_path)
            except OSError:
                pass
        
        # Prepare generation parameters
        generation_kwargs = dict(
            text=text.strip(),
            language=language,
            voice_clone_prompt=voice_prompt,
            generation_config=DEFAULT_GEN_CONFIG,
        )
        
        if speed != 1.0:
            generation_kwargs["speed"] = speed
        
        # Generate audio
        logger.info(f"Generating speech for text: {text[:50]}...")
        audio = model.generate(**generation_kwargs)
        
        # Convert to WAV bytes
        buffer = BytesIO()
        sf.write(buffer, audio[0], sampling_rate, format='WAV')
        buffer.seek(0)
        
        logger.info(f"✅ Audio generated successfully, duration: {audio[0].shape[-1]/sampling_rate:.1f}s")
        
        return Response(
            content=buffer.read(),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=\"speech.wav\""
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating speech: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation failed: {type(e).__name__}: {str(e)}")

@app.post("/v1/audio/speech/design", summary="Generate voice by design parameters")
async def design_voice(
    text: str = Form(..., description="Text to synthesize into speech"),
    gender: str = Form(None, description="Voice gender: male / female"),
    age: str = Form(None, description="Voice age: child / teenager / young adult / middle-aged / elderly"),
    pitch: str = Form(None, description="Voice pitch: very low pitch / low pitch / moderate pitch / high pitch / very high pitch"),
    style: str = Form(None, description="Voice style: whisper"),
    language: str = Form(None, description="Language code (optional, auto-detected if not provided)"),
    speed: float = Form(1.0, description="Speech speed multiplier (0.5 to 2.0)"),
):
    """
    Generate speech with designed voice without reference audio.
    
    - Only text is required, all other parameters are optional
    - Automatically generates voice based on selected attributes
    - Returns generated audio as WAV file
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # Build instruct string from parameters
        instruct_parts = []
        
        if gender and gender.strip():
            instruct_parts.append(gender.strip())
        if age and age.strip():
            instruct_parts.append(age.strip())
        if pitch and pitch.strip():
            instruct_parts.append(pitch.strip())
        if style and style.strip():
            instruct_parts.append(style.strip())
        
        instruct = ", ".join(instruct_parts) if instruct_parts else None
        
        # Prepare generation parameters
        generation_kwargs = dict(
            text=text.strip(),
            language=language,
            generation_config=DEFAULT_GEN_CONFIG,
        )
        
        if instruct:
            generation_kwargs["instruct"] = instruct
        
        if speed != 1.0:
            generation_kwargs["speed"] = speed
        
        # Generate audio
        logger.info(f"Generating designed voice for text: {text[:50]}...")
        if instruct:
            logger.info(f"Voice parameters: {instruct}")
            
        audio = model.generate(**generation_kwargs)
        
        # Convert to WAV bytes
        buffer = BytesIO()
        sf.write(buffer, audio[0], sampling_rate, format='WAV')
        buffer.seek(0)
        
        logger.info(f"✅ Audio generated successfully, duration: {audio[0].shape[-1]/sampling_rate:.1f}s")
        
        return Response(
            content=buffer.read(),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=\"designed_speech.wav\""
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating designed voice: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation failed: {type(e).__name__}: {str(e)}")


@app.get("/health", summary="Health check endpoint")
async def health_check():
    return {
        "status": "ok",
        "model_loaded": True,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "sampling_rate": sampling_rate
    }

if __name__ == "__main__":
    logger.info(f"Starting OmniVoice API server on http://{HOST}:{PORT}")
    logger.info(f"API documentation available at http://{HOST}:{PORT}/docs")
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )
