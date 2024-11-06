import asyncio
import ffmpeg
import websockets

async def main():
    # Equivalent of: ffmpeg -loglevel quiet -i rtmp://192.168.1.6/live/abc123 -ac 1 -ar 16000 -f s16le -
    # Load audio file and set parameters
    process = (
        ffmpeg
        .input('rtmp://192.168.1.6/live/abc123')
        .output('pipe:', format='s16le', acodec='pcm_s16le', ac=1, ar=16000)
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    

    #stream = ffmpeg.input('rtmp://192.168.1.6/live/abc123')
    #stream = ffmpeg.output(stream, 'pipe:', format='s16le', acodec='pcm_s16le', ac=1, ar='16000')
    #out, _ = ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)

    # Equivalent of: websocat --binary ws://localhost:8000/v1/audio/transcriptions
    # Create a WebSocket connection
    while True:
        async with websockets.connect("ws://127.0.0.1:8000/v1/audio/transcriptions") as ws:
            # Send audio data over WebSocket
            await ws.send(process.stdout.read(65536))
            print(f"Sent: {len(process.stdout.read(65536))}")
            message = await ws.recv()
            print(f"Received: {message}")

# Run the main function
asyncio.run(main())
