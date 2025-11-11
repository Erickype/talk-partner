# Talk Partner 🎙️

**Status: Prototype** ⚠️

An AI-powered conversation partner designed to help English learners practice speaking skills through natural conversations.

## 🎯 Motivation

Learning a new language requires practice, but not everyone has access to conversation partners. Talk Partner aims to solve this problem by providing:

- **Local execution** - Run entirely on your machine, no cloud services required
- **No GPU needed** - Optimized to run on consumer-grade CPUs
- **Privacy-focused** - Your conversations stay on your device
- **Always available** - Practice anytime without scheduling or additional costs

This tool is specifically designed for English learners who spend time alone and need a reliable partner to practice conversational skills.

## 🛠️ Technologies Used

### Backend
- **Python 3.13.7** - Core runtime
- **faster-whisper** - Speech-to-text (STT) using distil-large-v3 model
- **NeuTTS Air** - Text-to-speech (TTS) with voice cloning capabilities
- **NeuCodec** - Neural audio codec (ONNX decoder for CPU optimization)
- **Perth** - Audio watermarking
- **Phi-3** - Language model for conversation (CPU-optimized)
- **torch** - Deep learning framework
- **librosa** - Audio processing
- **phonemizer** - Phonetic transcription

### Frontend
- (To be implemented with modern design)

## 🚀 Run Instructions

### Prerequisites
The application was tested using the following:
- Python 3.13.7
- 16GB RAM minimum
- Modern Intel i7 processor or equivalent

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Erickype/talk-partner
cd talk-partner
git submodule update --init
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Run application:
```bash
python run.py
```

## Docker Support
Docker containerization is planned for easier deployment. 
Stay tuned for updates.

## 🖥️ Tested Hardware
The application has been successfully tested on:

- CPU: Intel Core i7-1165G7 (11th Gen, 4 cores, 8 threads)
- RAM: 16GB DDR4 3200MHz
- Storage: SSD recommended for model loading

## ⚡ Performance Constraints
With the current hardware configuration, the application is expected to achieve the following performance constraints:
- Real-Time Factor (RTF): ~2.5
  - This means audio generation takes approximately 2.5x longer than the duration of the output
  - Example: 1 second of audio takes ~2.5 seconds to generate

The performance of the application can improve in modern hardware like Apple Silicon, for more information, 
see the https://github.com/neuphonic/neutts-air repository.

## 🔮 Future Implementations (MVP Roadmap)
### Short-term Goals
- **Modern UI/UX Design** - Implement an intuitive, visually appealing interface
- **GPU Support for Phi-3** - Enable GPU acceleration for faster inference
- **Better Voice Quality** - Optimize TTS parameters for more natural speech

## Waiting on External Dependencies
- NeuTTS GPU Support - Currently limited by library capabilities
- Codec Optimizations - Awaiting upstream improvements in NeuCodec

## Possible Additional Features
- Multi-language support
- Conversation history and analytics
- Custom voice profiles
- Pronunciation feedback
- Vocabulary tracking

## 🤝 Contributing
Contributions are welcome! This is an early prototype,
and there's plenty of room for improvement.

## ⚠️ Known Limitations
- CPU-only execution results in slower inference times
- Real-time conversations are challenging with current RTF (due to my test hardware, still acceptable though)
- UI is currently basic/non-existent
- Limited to English language at this stage

Note: This is an active prototype under development. 
Features and performance characteristics are subject to change.