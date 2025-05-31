# 🎬 SFCA – Short Form Content Analyzer

**SFCA** is an AI-powered content analysis tool designed for evaluating short-form video content like TikToks, Reels, and Shorts. Created during the AaltoAI Hackathon 2025 by Covert Studios, SFCA processes visual, audio, and textual elements to analyze trends, patterns, and engagement signals.

---

## 📁 Project Structure

```
SFCA/
├── api/                # API endpoints for video analysis
├── app/                # Frontend or CLI logic
├── models/             # ML models for video/audio analysis
├── utils/              # Helper functions and scripts
├── data/               # Sample videos and outputs
├── tests/              # Unit tests
├── analysis.sqlite3    # Local database for storing results
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 🚀 Quickstart

```bash
git clone https://github.com/Covert-Studios/AaltoAI-hackathon-2025.git
cd AaltoAI-hackathon-2025
pip install -r requirements.txt
python app/main.py --input path/to/video.mp4
```

---

## 🔧 How to Get It Working
**First of all, clone the repo**

1. **Install Dependencies**  
   Make sure you have Python 3.8 or higher installed. Then run:

   ```bash
   pip install -r requirements.txt
   ```

2. **Download Required Models**  
   SFCA uses Whisper for transcription and other ML models. Ensure you have downloaded the required models (e.g., from Hugging Face or OpenAI):

   ```python
   import whisper
   model = whisper.load_model("base")
   ```

3. **Provide Input Video**  
   Place your `.mp4` video file inside the `data/` directory or pass its path as an argument.

4. **Run the Pipeline**  
   Execute the pipeline using:

   ```bash
   python api/api.py 
   ```
5. **Start Expo**
   Navigate to the Content Analyzer Folder
   ```bash
   npx expo start
   ```

## 🔍 Features

- 🎥 Frame-by-frame video analysis
- 🔊 Audio feature extraction (tempo, pitch, dynamics)
- 🧠 Whisper-based transcription & NLP
- 🌈 Visual flow and cut detection
- 📊 Engagement heuristics for virality scoring

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing

We welcome contributions! Please open issues or submit pull requests on GitHub.

---

## 👥 Team

Built by Covert Studios during [AaltoAI Hackathon 2025](https://github.com/Covert-Studios/AaltoAI-hackathon-2025).
