# 🎬 SFCA – Short Form Content Analyzer

**SFCA** is an AI-powered content analysis tool designed for evaluating short-form video content like TikToks, Reels, and Shorts. Created during the AaltoAI Hackathon 2025 by Otso (otsuliini) and Oliver (Oltsu-code), SFCA processes visual, audio, and textual elements to analyze trends, patterns, and engagement signals. It also has a place to see all the latest news and trends.

---
**Note**:
Due to time constraints, the CLIP topic detection AI has only been trained on 25 topics. 


---

## 🔧 How to Get It Working
**Step by step guide**

1. **Install Dependencies**  
   Make sure you have Python 3.11 installed. Then run:

   ```bash
   pip install -r requirements.txt
   ```
   and in app/ContentAnalyzer
   ```bash
   npm install
   ```

   Also make sure you have the latest version of ffmpeg installed.

2. **Run the Pipeline** 
   Navigate to the api folder (/api/) and run:
   ```bash
   python api/api.py 
   ```

3. **Start Expo**
   Navigate to the Content Analyzer folder (/app/ContentAnalyzer) and run:
   ```bash
   npx expo start
   ```
   Then press 'w' for web, a for android emulator (if available) or just open it on your phone in the Expo Go App by scanning the QR-code

**Note**:
You will have to provide your own OpenAI key.

**Note**:
Change the API_BASE_URL to your IP or domain.

> **Authentication Setup:**  
> For authentication, you must create your own [Clerk](https://clerk.com/) project and set the required environment variables (`CLERK_PUBLISHABLE_KEY`, `CLERK_JWT_PUBLIC_KEY`, etc.) in your `.env` files.  
> **Never share your secret keys publicly.**  
>  
> You will also need to provide your own OpenAI API key in the backend `.env` file as `OPENAI_API_KEY=your-key-here`.

---

## How to use?
**Example Output** 
**Score** A score out of 100 based of the criteria below.
1. **Music:** A score out of 20. Using the "shazamio" api we analyze how the song fits the theme and topic of the video. 
2. **Transcription:** A score out of 20. Using OpenAI's whisper model, we get a transcription of the video to further predict how engaging the video is.
3. **Platfrom Accessibility:** A score out of 20. What platform is this content suitable for. 
4. **Visual Appeal & Social Sharing:** A score out of 20. How engaging the topic is.
5. **Video Length** A score out of 20. Predicts the viewers engagement based of the length of the video.


**Suggestions:** A list of suggestions to make the video more engaging.

---

**Features**
   - Video analysis 
      - Go to the "Analyze" tab press the "SCAN (PICK VIDEO)" button and wait for the video to analyze. Once done you will be redirected to a tab that will show the results.
      - These results will be saved and can be accessed right under the button. You can remove them whenever you want from the profile tab with the "Manage Analyses" where you can delete all or one with the id of the analisys.
      - You can also change the name of a analisys by viewing it and pressing the "Change name" button.
   - Personal "Clickbait" Creator
      - Go to the "Feed" tab where there will be a button with a speaker bubble icon on it. 
      - Write the bot the topic you want to get a "clickbait" title of. 
   - News Feed
      - Go to the "Feed" tab where you can find new and intresting topics from the latest news.
      - You can check more details of them by clicking on them. Including charts of when peak news writng happened of this topic.


**Tech Stack**
---

- **Frontend:**  
  - React Native (Expo)
  - TypeScript
  - Expo Router
  - Clerk (Authentication)
  - React Native Markdown Display
  - React Native Circular Progress
  - React Native Chart Kit
  - Expo Haptics

- **Backend:**  
  - FastAPI (Python)
  - SQLite (analysis storage)
  - OpenAI GPT-4o (AI analysis & news)
  - OpenAI Whisper (audio transcription)
  - Shazamio (music recognition)
  - Torch + CLIP (video frame classification)
  - ffmpeg-python (audio/video processing)

- **Other:**  
  - NewsAPI (news trends)
  - Docker/venv (local dev environments)
  - REST API (JWT Auth via Clerk)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing

We welcome contributions! Please open issues or submit pull requests on GitHub.




