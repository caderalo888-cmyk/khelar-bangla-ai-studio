# Khelar Bangla AI Studio

একটি starter web app: একই সাইটে বাংলা sports-script draft এবং ছবি দিয়ে 9:16 MP4 slideshow বানানো যায়।

## কী আছে
- Sports AI: topic থেকে বাংলা স্ক্রিপ্টের খসড়া
- Video Maker: একাধিক ছবি দিয়ে vertical MP4
- ঐচ্ছিক MP3/WAV/M4A/OGG audio যোগ
- Output download

## প্রয়োজন
- Python 3.10+
- FFmpeg ইনস্টল করা এবং PATH-এ থাকা
- Windows হলে FFmpeg ইনস্টল করে `ffmpeg -version` চালিয়ে পরীক্ষা করো

## চালানোর নিয়ম (Windows)
1. ZIP ফাইল Extract করো।
2. ওই ফোল্ডারে Command Prompt/Terminal খোলো।
3. Virtual environment তৈরি করো:
   `python -m venv .venv`
4. চালু করো:
   `.venv\\Scripts\\activate`
5. Dependency ইনস্টল:
   `pip install -r requirements.txt`
6. চালাও:
   `python app.py`
7. ব্রাউজারে খোলো:
   `http://127.0.0.1:5000`

## গুরুত্বপূর্ণ সীমাবদ্ধতা
এটি পূর্ণাঙ্গ prompt-to-video AI model নয়। বর্তমানে নিজের আপলোড করা ছবি থেকে slideshow তৈরি করে। সত্যিকারের text-to-video, realistic AI voice, auto captions এবং cloud hosting যোগ করতে উপযুক্ত model/API বা স্থানীয় GPU-চালিত model সংযুক্ত করতে হবে। এসবের খরচ, speed, duration এবং usage limit provider/hardware অনুযায়ী ভিন্ন হয়; “unlimited” নিশ্চিত নয়।

## নিরাপত্তা
- `FLASK_SECRET_KEY` বদলাও।
- Public internet-এ deploy করার আগে authentication, upload size/rate limits, file validation, CSRF protection, job queue এবং storage cleanup যোগ করো।
- এই development server production hosting-এর জন্য নয়।
- Generated sports scripts খসড়া মাত্র; প্রকাশের আগে খবরের সত্যতা যাচাই করো।
