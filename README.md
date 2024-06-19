# AI Subtitle Video Enbedding Application

## Pre-requisites
1. **Install Python**: Make sure you have Python 3.6 or later installed: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. **Install FFMPEG**: [https://ffmpeg.org](https://ffmpeg.org)
   
## Local Setup Process
1. **Create a virtual environment**: You can create a virtual environment using the following command in your terminal:

```bash
python3 -m venv env
```
2. **Activate the virtual environment**
   
```bash
source env/bin/activate
```
3. **Intall Dependancies**:

```bash
pip3 install -r requirements
```
4. **Freeze dependencies**
   
```bash
pip3 freeze > requirements.txt
```
5. **Finally run the flask application**
   
```bash
flask --app app.py run
```

The web application will be active on `http:127.0.0.1:5000`

## Testing the application
1. Insert a link into the input field given, here's a sample link - [https://i.imgur.com/hHS2geD.mp4](https://i.imgur.com/hHS2geD.mp4) (copy&paste)
2. Click on `Add Subtitle` button, and wait for a few second for the process to complete
3. After successfull completion the app will redirect you to your subtitle embedded video.
  
<img width="1080" alt="Screenshot 2024-06-20 at 00 02 30" src="https://github.com/anur4ag/ffmpeg-subtitle-ai/assets/71564387/dc849ea6-dbdd-42b4-abbe-d3cc761d3997">

