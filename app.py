import os, re, uuid, subprocess, shutil
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename

APP_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = APP_DIR / "uploads"
OUTPUT_DIR = APP_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024
ALLOWED_IMAGES = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_AUDIO = {".mp3", ".wav", ".m4a", ".ogg"}
ALLOWED_VIDEO = {".mp4", ".mov", ".webm"}

def safe_name(name):
    return secure_filename(name or "upload")

def make_sports_script(topic, style="dramatic"):
    topic = (topic or "").strip()
    if not topic:
        topic = "আজকের খেলার খবর"
    if style == "breaking":
        opening = f"ব্রেকিং স্পোর্টস আপডেট! {topic} নিয়ে এসেছে নতুন আলোচনা।"
    elif style == "emotional":
        opening = f"খেলার মাঠে আবেগ, উত্তেজনা আর নাটকীয়তা—{topic} এখন সমর্থকদের আলোচনায়।"
    else:
        opening = f"খেলার দুনিয়ায় বড় আপডেট! {topic} নিয়ে বিস্তারিত জানুন খেলার বাংলায়।"
    return (opening + "\n\n"
            + f"{topic} নিয়ে সমর্থকদের আগ্রহ এখন তুঙ্গে। "
            "সর্বশেষ তথ্য, নির্ভরযোগ্য সূত্র এবং আনুষ্ঠানিক আপডেট যাচাই করে খবরটি প্রকাশ করুন।\n\n"
            "আপনার মতামত কমেন্টে জানান। এমন আরও স্পোর্টস আপডেট পেতে খেলার বাংলা ফলো করুন।")

def has_ffmpeg():
    return shutil.which("ffmpeg") is not None

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", ffmpeg=has_ffmpeg())

@app.route("/script", methods=["POST"])
def script():
    topic = request.form.get("topic", "")
    style = request.form.get("style", "dramatic")
    generated = make_sports_script(topic, style)
    return render_template("result.html", title="Sports Script", content=generated)

@app.route("/create-video", methods=["POST"])
def create_video():
    if not has_ffmpeg():
        flash("ভিডিও তৈরির জন্য FFmpeg ইনস্টল করতে হবে। README.md দেখুন।")
        return redirect(url_for("index"))

    title = (request.form.get("video_title") or "Khelar Bangla Video").strip()
    duration = max(3, min(int(request.form.get("duration", "5") or 5), 30))
    caption = (request.form.get("caption") or title).strip()
    images = request.files.getlist("images")
    audio = request.files.get("audio")
    valid_images = []
    for f in images:
        if f and f.filename and Path(f.filename).suffix.lower() in ALLOWED_IMAGES:
            name = f"{uuid.uuid4().hex}_{safe_name(f.filename)}"
            dest = UPLOAD_DIR / name
            f.save(dest)
            valid_images.append(dest)
    if not valid_images:
        flash("ভিডিও বানাতে অন্তত একটি ছবি (JPG/PNG/WebP) আপলোড করুন।")
        return redirect(url_for("index"))

    job_id = uuid.uuid4().hex[:10]
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    try:
        segments = []
        for i, image_path in enumerate(valid_images):
            segment = job_dir / f"segment_{i:03d}.mp4"
            # A still-image slideshow clip; use a safe, widely compatible H.264 encode.
            vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p"
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", str(image_path),
                "-t", str(duration), "-vf", vf,
                "-r", "25", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-an", str(segment)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            segments.append(segment)

        concat_file = job_dir / "concat.txt"
        concat_file.write_text("".join(f"file '{p.as_posix()}'\n" for p in segments), encoding="utf-8")
        silent_video = job_dir / "silent.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-c", "copy", str(silent_video)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

        output = f"{job_id}.mp4"
        final_path = OUTPUT_DIR / output
        audio_path = None
        if audio and audio.filename and Path(audio.filename).suffix.lower() in ALLOWED_AUDIO:
            audio_path = UPLOAD_DIR / f"{uuid.uuid4().hex}_{safe_name(audio.filename)}"
            audio.save(audio_path)
        if audio_path:
            subprocess.run([
                "ffmpeg", "-y", "-i", str(silent_video), "-i", str(audio_path),
                "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(final_path)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        else:
            shutil.copy2(silent_video, final_path)
        return render_template("result.html", title=title, content="আপনার ভিডিও তৈরি হয়েছে। নিচের বোতামে ক্লিক করে ডাউনলোড করুন।", video=output)
    except subprocess.CalledProcessError as e:
        detail = (e.stderr or b"").decode("utf-8", errors="ignore")[-1200:]
        flash("ভিডিও তৈরি করা যায়নি। FFmpeg/ফাইল ফরম্যাট পরীক্ষা করুন। " + detail)
        return redirect(url_for("index"))

@app.route("/outputs/<path:filename>")
def download_output(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
