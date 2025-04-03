import os
import time
import json
import requests
import speech_recognition as sr
from aip import AipSpeech

# 百度语音合成配置
APP_ID = '118339955'
API_KEY = 'CCtkiTJAQhgFCAHBoR0TW0LB'
SECRET_KEY = 'J2RRqtIkugQD5ZlMPJwu14I1aS6jsYUA'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

# 阿里云 API 配置
ALI_API_KEY = 'sk-e4d8a3361419475e9f8d409e0fd1c649'
ALI_API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'

# 语音合成
def speak_baidu(text):
    os.makedirs("audio", exist_ok=True)
    filename = f"audio/xiaoli_{int(time.time())}.mp3"
    result = client.synthesis(text, 'zh', 1, {
        'vol': 5, 'spd': 4, 'pit': 6, 'per': 4
    })
    if not isinstance(result, dict):
        with open(filename, 'wb') as f:
            f.write(result)
        return filename
    else:
        return None

# 调用阿里云百炼
def get_reply_ali(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ALI_API_KEY}"
    }
    body = {
        "model": "qwen-turbo",
        "input": {
            "prompt": prompt
        }
    }
    try:
        response = requests.post(ALI_API_URL, headers=headers, data=json.dumps(body))
        data = response.json()
        return data['output']['text'].strip()
    except:
        return "小丽脑袋有点短路了～"

# 语音识别
def listen_once():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source, phrase_time_limit=5)
    try:
        text = r.recognize_google(audio, language='zh-CN')
        return text
    except:
        return ""