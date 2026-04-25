# OmniVoice TTS API Server

A lightweight Python-based server designed to provide a robust API for Omnivoice TTS. This project enables seamless speech synthesis and high-fidelity voice cloning, allowing you to deploy a powerful voice generation engine in seconds.

Zero-Shot Text-to-Speech API with voice cloning, supporting 600+ languages.
Based on OmniVoice model by k2-fsa.

## ✅ Features
- ✅ Voice cloning from 3-10 second reference audio
- ✅ 600+ languages support
- ✅ Automatic language detection
- ✅ Adjustable speech speed
- ✅ Works on both GPU (CUDA) and CPU
- ✅ Standard REST API interface
- ✅ Built-in Swagger UI documentation

---

## 📋 Requirements
- Python 3.10 - 3.13 (3.12 recommended)
- Minimum 8GB RAM
- For GPU acceleration: NVIDIA GPU with CUDA 12.8+
- NVidia RTX3060 12GB work perfectly

---

## 🚀 Installation

### Windows Portable
There is a portable standalone build for Windows that should work for running on Nvidia GPUs or for running on your CPU only on the releases page.

Simply download, extract with 7-Zip or with the windows explorer on recent windows versions and run:
`01_StartServer.bat.`
`02_StartTestDesign.bat.`

If you have downloaded model files put them in .\model\OmniVoice

The portable above currently comes with python 3.13 and pytorch cuda 12.8. Update your Nvidia drivers if it doesn't start.

### 1. Clone repository
```bash
git clone https://github.com/sinfisum/omnivoice-py.git
cd omnivoice-py
```

### 2. Create virtual environment

**Linux / Ubuntu:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```powershell
python.exe -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Upgrade pip
```bash
pip install --upgrade pip
```

### 4. Install PyTorch with CUDA support (recommended)
```bash
pip install torch torchvision torchaudio torchcodec --index-url https://download.pytorch.org/whl/cu128
```

> 💡 If you don't have GPU - skip this step, PyTorch will be installed automatically for CPU

### 5. Install all dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Start Server

```bash
python server.py
```

On successful startup you will see:
```
✅ Model loaded successfully! Sampling rate: 16000 Hz
Starting OmniVoice API server on http://127.0.0.1:8880
API documentation available at http://127.0.0.1:8880/docs
```

---

## 📚 API Documentation

After starting server interactive documentation is available:
- **Swagger UI:** http://127.0.0.1:8880/docs
- **OpenAPI specification:** http://127.0.0.1:8880/openapi.json

### Available endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/audio/speech/clone` | Speech synthesis with voice cloning |
| GET | `/health` | Server health check |

---

### 🔊 Voice Cloning Endpoint

**POST** `/v1/audio/speech/clone`

#### Form parameters:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | ✅ | Text to synthesize into speech |
| `ref_audio` | file | ✅ | Reference audio (WAV, 3-10 seconds, 16kHz recommended) |
| `ref_text` | string | ❌ | Transcript of reference audio (improves cloning quality) |
| `language` | string | ❌ | Language code (auto-detected if not provided) |
| `speed` | float | ❌ | Speech speed multiplier (0.5 to 2.0, default 1.0) |

#### Response:
WAV audio file 16kHz mono.

---

## 🧪 Testing

1. Run test:
```bash
python test_client_design.py

# or

python test_client_multi.py
```

On successful request result will be saved as `generated_speech.wav`

---

## 💡 Usage Recommendations

1. **Reference audio:**
   - Duration: 3-10 seconds
   - Clean audio without background noise
   - Single speaker
   - Normal speech rate
   - WAV format 16kHz 16bit mono

2. **Performance:**
   - On GPU RTX 3090 ~10 seconds speech generation takes ~1-2 seconds
   - On CPU ~10-15 times slower
   - Model automatically selects available device

---

## 🔧 Configuration

In `server.py` you can modify:
- Server `HOST` and `PORT`
- `CHECKPOINT` model path
- Default generation parameters in `DEFAULT_GEN_CONFIG`

---

## ⚠️ Notes

- On first run model will be automatically downloaded from Hugging Face Hub (~1.8GB)
- Hugging Face telemetry is disabled
- Temporary files are automatically deleted after processing
- Check OmniVoice model license for commercial usage
