import requests
import base64

# Encode your video chunk as base64
chunk_path = 'screenrecord.webm'
with open(chunk_path, 'rb') as chunk_file:
    encoded_chunk = base64.b64encode(chunk_file.read()).decode('utf-8')

# URL of the Flask API endpoints
base_url = 'https://screenrecordingapi.onrender.com'  # Update with your server's URL
start_recording_url = f'{base_url}/start-recording/'

# Start a new recording session and get the session ID
response = requests.get(start_recording_url)
print(response.content)

# Attempt to extract sessionID from the response
try:
    session_id = response.json()['sessionID']
    print(f'Successfully obtained session ID: {session_id}')

    # Send video chunks to the stream-recording endpoint
    chunk_data = {'videoChunk': encoded_chunk}
    response = requests.post(
        f'{base_url}/stream-recording/{session_id}', json=chunk_data)
    print(response.content)
    response = requests.post(f'{base_url}/stop-recording/{session_id}')
    if response.status_code == 200:
        video_content = response.content

        with open(f'downloads/{session_id}video.webm', 'wb') as f:
            f.write(video_content)
except Exception as e:
    print(f'Error extracting session ID: {e}')
