import requests
from io import BytesIO
from flask import Flask, request, render_template, send_file, redirect, url_for
import os
import time
import math
import ffmpeg
from werkzeug.utils import secure_filename
from faster_whisper import WhisperModel

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def download_video(video_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(video_url, headers=headers, stream=True)
    if response.status_code == 200:
        video = BytesIO(response.content)
        return video
    else:
        print(f"Failed to download video. Status code: {response.status_code}")
        print(response.content)
        raise Exception("Failed to download video")

def extract_audio(input_video, input_video_name):
    extracted_audio = os.path.join(app.config['UPLOAD_FOLDER'], f"audio-{input_video_name}.wav")
    stream = ffmpeg.input('pipe:0')
    stream = ffmpeg.output(stream, extracted_audio)
    ffmpeg.run(stream, input=input_video.read(), overwrite_output=True)
    return extracted_audio

def transcribe(audio):
    model = WhisperModel("small")
    segments, info = model.transcribe(audio)
    language = info[0]
    print("Transcription language", info[0])
    segments = list(segments)
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    return language, segments

def format_time(seconds):
    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"
    return formatted_time

def generate_subtitle_file(input_video_name, language, segments):
    subtitle_file = os.path.join(app.config['UPLOAD_FOLDER'], f"sub-{input_video_name}.{language}.srt")
    text = ""
    for index, segment in enumerate(segments):
        segment_start = format_time(segment.start)
        segment_end = format_time(segment.end)
        text += f"{str(index+1)} \n"
        text += f"{segment_start} --> {segment_end} \n"
        text += f"{segment.text} \n"
        text += "\n"
    with open(subtitle_file, "w") as f:
        f.write(text)
    return subtitle_file

def add_subtitle_to_video(input_video, input_video_name, soft_subtitle, subtitle_file, subtitle_language):
    video_input_stream = ffmpeg.input('pipe:0')
    subtitle_input_stream = ffmpeg.input(subtitle_file)
    output_video = os.path.join(app.config['OUTPUT_FOLDER'], f"output-{input_video_name}.mp4")
    subtitle_track_title = subtitle_file.replace(".srt", "")
    if soft_subtitle:
        stream = ffmpeg.output(
            video_input_stream, subtitle_input_stream, output_video, **{"c": "copy", "c:s": "mov_text"},
            **{"metadata:s:s:0": f"language={subtitle_language}", "metadata:s:s:0": f"title={subtitle_track_title}"}
        )
    else:
        stream = ffmpeg.output(video_input_stream, output_video, vf=f"subtitles={subtitle_file}")
    ffmpeg.run(stream, input=input_video.read(), overwrite_output=True)
    return output_video

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_video():
  video_url = request.form.get('video_url')
  if not video_url:
    return 'No video URL provided'

  input_video_name = os.path.basename(video_url).split('.')[0]
  try:
    input_video = download_video(video_url)
  except Exception as e:
    return str(e), 400

  extracted_audio = extract_audio(input_video, input_video_name)
  language, segments = transcribe(extracted_audio)
  subtitle_file = generate_subtitle_file(input_video_name, language, segments)
  input_video.seek(0)  # Reset video stream for ffmpeg
  output_video_path = add_subtitle_to_video(input_video, input_video_name, soft_subtitle=False, subtitle_file=subtitle_file, subtitle_language=language)

  output_filename = os.path.basename(output_video_path)
  return redirect(url_for('output_video', filename=output_filename))

@app.route('/output/<filename>')
def output_video(filename):
    return render_template('output.html', filename=filename)

@app.route('/outputs/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
