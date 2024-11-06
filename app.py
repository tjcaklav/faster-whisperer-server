import ffmpeg
import requests
import time
import wave
import json
import jieba

# Define the RTMP stream URL
rtmp_url = "rtmp://192.168.1.6/live/abc123"

# Define the HTTP POST URL
http_post_url = "http://localhost:8000/v1/audio/transcriptions"

# Buffer every 2 seconds of the audio stream
buffer = b""
buffer_secs = 2
start_time = time.time()
audio_rate = 16000
audio_channel = 1

prompt_list = ["親愛的朋友，大家好，大家平安。"]
#prompt_list = ["Welcome, this is a sermon by a preacher from True Jesus Church."]
prompt = ' '.join(prompt_list)

data = {
    "language": "zh",
    "model": "large-v2",
    "prompt": prompt,
    "response_format": "verbose_json"
}

# Create a process to run ffmpeg
process = (
    ffmpeg
    .input(rtmp_url, threads=0)
    .output('-', format='wav', acodec='pcm_s16le', ac=audio_channel, ar=audio_rate)
    .run_async(pipe_stdout=True, pipe_stderr=True)
)

while True:
    buffer += process.stdout.read(4096)
    if len(buffer) >= audio_rate*2*audio_channel*buffer_secs:
        # Write the buffered data to a file
        with wave.open('buffered_data.wav', 'wb') as f:
            f.setnchannels(audio_channel)
            f.setsampwidth(2)
            f.setframerate(audio_rate)
            f.writeframes(buffer)

        # Reset the buffer and the start time
        buffer = b""
        start_time = time.time()
        
        with open('buffered_data.wav', "rb") as f:
            files = {"file": f}
            # Perform a HTTP POST with the buffered data
            response = requests.post(http_post_url, files=files, data=data)
            # Parse the JSON string
            parsed_json = json.loads(response.text)
            # Access the value of the "text" key
            text = parsed_json["text"]
            #print(f"HTTP POST response: {text}")
            #print(text)
            # Tokenize the text and print the tokens
            tokens = jieba.lcut(text)
            print(tokens)
        
        # Append the text to the 'prompt' in the data dictionary with a space
        if text != "":
            prompt_list.append(text)
        # Restrict prompt to the most recent 3 transcribed audio
        if len(prompt_list) > 3:
            prompt_list.pop(0)
        data['prompt'] = ' '.join(prompt_list)
        #print('prompts: ' + ' '.join(prompt_list))