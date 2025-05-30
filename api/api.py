from flask import Flask, jsonify, request, abort
import subprocess

app = Flask(__name__)

# Predefined API key
API_KEY = "prohackerschmacker6969"

# Decorator to require API key
def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key != API_KEY:
            abort(401, description="Unauthorized: Invalid API Key")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__  # Preserve function name for Flask
    return wrapper

def get_video(video):
    # get the users video 


@app.route('/date', methods=['GET'])
@require_api_key
def get_date():
    result = subprocess.check_output(['date']).decode('utf-8')
    return jsonify({'date': result.strip()})

@app.route('/cal', methods=['GET'])
@require_api_key
def get_cal():
    result = subprocess.check_output(['cal']).decode('utf-8')
    return jsonify({'calendar': result.strip()})

@app.route('/docker', methods=['GET'])
@require_api_key
def get_docker():
    result = subprocess.check_output(['docker', 'ps']).decode('utf-8')
    return jsonify({'docker': result.strip()})

@app.route('/cls', methods=['GET'])
@require_api_key
def get_cls():
    result = subprocess.check_output(['cls']).decode('utf-8')
    return jsonify({'cls': result.strip()})

@app.route('/upload', methods=['POST'])
@require_api_key
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the video to the uploads folder
    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    video.save(video_path)

    # Log the received video
    print(f"[INFO] Received video: {video.filename}")
    print(f"[INFO] Saved to: {video_path}")

    return jsonify({"message": "Video uploaded successfully", "path": video_path}), 200

@app.route('/analyze', methods=['POST'])
@require_api_key
def analyze_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded video
    video_path = os.path.join("uploads", video.filename)
    os.makedirs("uploads", exist_ok=True)
    video.save(video_path)

    # Log the received video
    print(f"[INFO] Received video for analysis: {video.filename}")
    print(f"[INFO] Saved to: {video_path}")

    # Call the CLIP classification script
    frame_dir = "frames"
    os.makedirs(frame_dir, exist_ok=True)
    extract_frames(video_path, frame_dir, frame_interval=2)

    # Load topics and analyze frames
    topics_file = "data/topics.txt"
    topics = load_topics(topics_file)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    text_tokens = clip.tokenize(topics).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    results = analyze_frames(frame_dir, model, preprocess, text_features, topics, device)

    # Summarize results
    topics_detected = [topic for _, topic in results]
    summary = Counter(topics_detected).most_common()

    # Log the analysis summary
    print(f"[INFO] Analysis complete for: {video.filename}")
    print(f"[INFO] Summary: {summary}")

    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run()