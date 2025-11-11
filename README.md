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
- Windows 11
- Python 3.13.7
- 16GB RAM ddr4 minimum
- Modern Intel i7-1165G7 processor or equivalent

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd talk-partner
```