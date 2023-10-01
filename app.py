from flask import Flask, jsonify, request, send_file
import os
from models.video import VideoDatabse
import uuid
import base64
import time
from datetime import datetime
import threading

db = VideoDatabse()
recordingData = {}


app = Flask(__name__)

@app.route('/start-recording', strict_slashes=False, methods=['POST'])
def startRecording():
    try:
        sessionID = uuid.uuid4().hex[:16]
        createdAt = datetime.now().isoformat(timespec='minutes')
        print(f'New recording started: Session ID: {sessionID}, {createdAt}')
        db.add_file(sessionID, createdAt)
        recordingData[sessionID] = {'data': [], 'timeout': None}

        return jsonify({'sessionID': sessionID}), 200
    except Exception as err:
        return jsonify({'error': f"an error occured {err}"}), 400

def delete_file(fileURL):
    if os.path.exists(fileURL):
        os.remove(fileURL)

def delete_session(sessionId):
    del(recordingData[sessionId])
    db.delete_file(sessionId)

def del_file_timeout(fileURL):
    timeout_seconds = 10 * 60 * 1000
    time.sleep(timeout_seconds)
    delete_file(fileURL)

def set_timeout(session_id):
    timeout_seconds = 7 * 60
    time.sleep(timeout_seconds)
    delete_session(session_id)

def write_file(file_path, data):
    with open(file_path, 'wb') as file:
        file.write(data)

def cancel_timeout(session_id):
    if recordingData[session_id]['timeout'] is not None and recordingData[session_id]['timeout'].is_alive():
        recordingData[session_id]['timeout'].cancel()

@app.route('/stream-recording/<sessionId>', strict_slashes=False, methods=['POST'])
def streamRecordingData(sessionId):
    try:
        sessionExitsts = db.query_file(sessionId)

        print(sessionId)
        print(sessionExitsts)
        print(recordingData)
        
        if not sessionExitsts:
            return jsonify({'error': 'error invalid session'}), 400

        print(f'Received video data chunk for session {sessionId}')

        data = request.get_json()
        if 'videoChunk' in data:
            encoded_chunk = data['videoChunk']
            decoded_chunk = base64.b64decode(encoded_chunk)
        recordingData[sessionId]['data'].append(decoded_chunk)

        recordingData[sessionId].timeout = threading.Thread(target=set_timeout, args=(sessionId,))
        recordingData[sessionId].timeout.start()

        return jsonify({'message': "Video data chunk received succesfully"}), 200
    
    except Exception as err:
        return jsonify({'error': f"An error occured {err}"}), 400


@app.route('/stop-recording/<sessionId>', strict_slashes=False, methods=['POST'])
def stopRecording(sessionId):
    try:
        sessionExitsts = db.query_file(sessionId)

        if not sessionExitsts:
            return jsonify({'error': 'error invalid session'}), 400
        
        if sessionId not in recordingData or recordingData[sessionId]['data'] is None:
            return jsonify({'error': 'error invalid session'}), 400


        videoData = b''.join(recordingData[sessionId]['data'])
        filename = 'record'+sessionId+'.mp4'

        parent_dir = os.path.dirname(os.path.realpath(__file__))
        recording_path = os.path.join(parent_dir, 'recordings')

        if not os.path.exists(recording_path):
            os.mkdir(recording_path)
        
        videoUrl = os.path.join(recording_path, filename)
        
        write_file(videoUrl, videoData)

        cancel_timeout(sessionId)
        delete_session(sessionId)

        del_file_timeout(videoUrl)

        return jsonify({"video": videoUrl}), 200
    
    except Exception as err:
        return jsonify({"error": f"An error occured {err}"}), 400


@app.route('/save-video/<sessionId>', strict_slashes=False, methods=['GET'])
def downloadvideo(sessionId):
    try:
        filename = 'record'+sessionId+'.mp4'
        videopath = 'recordings/'+ filename
        if not os.path.exists(videopath):
            return jsonify({'error': "Invalid file"})
        content_type = 'video/mp4'
        return send_file(videopath, as_attachment=True, download_name=filename, mimetype=content_type)
    
    except Exception as err:
        return jsonify({"error": "An error occured {err}"}), 404


if __name__ == '__main__':
    app.run(debug=False)