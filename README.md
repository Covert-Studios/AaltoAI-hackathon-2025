# 🎬 SFCA – Short Form Content Analyzer

**SFCA** is an AI-powered content analysis tool designed for evaluating short-form video content like TikToks, Reels, and Shorts. Created during the AaltoAI Hackathon 2025 by Otso (otsuliini) and Oliver (Oltsu-code), SFCA processes visual, audio, and textual elements to analyze trends, patterns, and engagement signals. It also has a place to see all the latest news and trends.

---

## 🔧 How to Get It Working
**Step by step guide**

1. **Install Dependencies**  
   Make sure you have Python 3.11 installed. Then run:

   ```bash
   pip install -r requirements.txt
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

---

## How to use?

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


## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing

We welcome contributions! Please open issues or submit pull requests on GitHub.

---
