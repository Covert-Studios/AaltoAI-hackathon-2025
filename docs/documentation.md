# 📚 Documentation: SocialScope Content Analysis Pipeline

## Overview

SocialScope is a multi-stage pipeline for analyzing video content, combining transcription, visual analysis, music detection, subtitle detection, topic extraction, and AI-powered scoring. The system leverages state-of-the-art models and libraries such as OpenAI Whisper, CLIP, Shazamio, and GPT-4o.

---

## Pipeline Steps

### 1. Ingest Video
- **Script:** [`CLIPvideoclassification.py`](../api/CLIPvideoclassification.py)
- **Description:** Loads a video file and extracts frames at intervals for further analysis.
- **Key Function:** `extract_frames(video_path, output_dir, frame_interval=2)`

### 2. Transcription
- **Script:** [`whisperstuff.py`](../api/whisperstuff.py)
- **Tool:** [OpenAI Whisper](https://github.com/openai/whisper)
- **Description:** Transcribes the audio track of a video or audio file to text.
- **Output:** `transcription.txt`

### 3. Visual Pattern Analysis
- **Script:** [`CLIPvideoclassification.py`](../api/CLIPvideoclassification.py)
- **Tools:** `opencv`, `numpy`, `scikit-image`, [OpenAI CLIP](https://github.com/openai/CLIP)
- **Description:** Analyzes extracted frames for scene mood, transitions, object motion, and predicts semantic topics using CLIP.
- **Output:** `visual_summary.json`

### 4. Music Detection
- **Script:** [`shazamioapi.py`](../api/shazamioapi.py)
- **Tool:** [Shazamio](https://github.com/olunav/shazamio)
- **Description:** Identifies background music, extracting track name, artist, genre, and tempo.
- **Output:** `music.json`

### 5. Subtitle Detection
- **Tool:** `pytesseract`, `cv2`
- **Description:** Scans video frames for the presence of subtitles using OCR.
- **Output:** `has_subtitles: true/false`

### 6. Topic Detection (User-Aided)
- **Script:** [`CLIPvideoclassification.py`](../api/CLIPvideoclassification.py)
- **Description:** Optionally uses CLIP to extract semantic topics from video frames, or accepts user-provided hints.

### 7. GPT-4 Analysis
- **Script:** [`chatgptapi.py`](../api/chatgptapi.py)
- **Tool:** OpenAI GPT-4o/Turbo
- **Description:** Aggregates all extracted data and scores content, visuals, audio, and engagement using GPT.
- **Output:** Various scores (content_score, visual_score, audio_match_score, engagement_score)

### 8. BONUS: Subject Speed ↔ Music Tempo
- **Tool:** Object tracking (YOLOv5, DeepSort, or cv2 trackers)
- **Description:** Compares subject motion speed with detected music BPM for coherence analysis.
- **Output:** `coherence_score`

### 9. Aggregate
- **Description:** Combines all scores into a final score (0.00–10.00) and generates improvement suggestions via ChatGPT.

---

## API

- **Script:** [`api.py`](../api/api.py)
- **Framework:** Flask
- **Endpoints:**
  - `/date` – Returns server date (API key required)
  - `/cal` – Returns calendar (API key required)
  - `/docker` – Returns Docker status (API key required)
  - `/cls` – Attempts to clear screen (may not work on all OS)
- **API Key:** Set in the script as `prohackerschmacker6969`

---

## Frontend App

- **Folder:** [`app/ContentAnalyzer`](../app/ContentAnalyzer/)
- **Framework:** Expo (React Native)
- **Features:**
  - User authentication via Clerk
  - Tab navigation: Feed, Analyze, Profile
  - Themed UI components
  - Example code for routing, theming, and navigation

---

## Scripts Summary

- [`CLIPvideoclassification.py`](../api/CLIPvideoclassification.py): Video frame extraction and topic classification using CLIP.
- [`whisperstuff.py`](../api/whisperstuff.py): Audio transcription with Whisper.
- [`shazamioapi.py`](../api/shazamioapi.py): Music recognition with Shazamio.
- [`chatgptapi.py`](../api/chatgptapi.py): Example of querying OpenAI GPT models.
- [`api.py`](../api/api.py): Flask API for basic server commands (date, calendar, docker status).
- [`app/ContentAnalyzer/app`](../app/ContentAnalyzer/app): Main Expo app source code.

---

## Setup & Usage

1. **Install Python dependencies:**
   ```
   pip install -r docs/requirements.txt
   ```
2. **Install Node/Expo dependencies:**
   ```
   cd app/ContentAnalyzer
   npm install
   ```
3. **Run the backend API:**
   ```
   python api/api.py
   ```
4. **Run the Expo app:**
   ```
   npx expo start
   ```

---

## References

- [OpenAI Whisper](https://github.com/openai/whisper)
- [OpenAI CLIP](https://github.com/openai/CLIP)
- [Shazamio](https://github.com/olunav/shazamio)
- [Expo](https://expo.dev/)
- [Clerk](https://clerk.com/)
