from wsgi import app
from db import VideoDatabase, db
from flask import jsonify, request, send_file
import os
from models.video import VideoDatabase
import uuid
import base64
import time
from datetime import datetime
import threading

recordingData = {}


@app.route('/start-recording', strict_slashes=False, methods=['GET'])
def startRecording():
    try:
        sessionID = uuid.uuid4().hex[:16]
        createdAt = datetime.now().isoformat(timespec='minutes')
        recordingData[sessionID] = {'data': [], 'timeout': None}

        video = VideoDatabase(sessionID=sessionID, createdAt=createdAt)
        db.session.add(video)
        db.session.commit()

        print(f'New recording started: Session ID: {sessionID}, {createdAt}')
        responseData = {'sessionID': sessionID}
        return jsonify(responseData), 200
    except Exception as err:
        print(f"Error: {err}")
        return jsonify({'error': f"an error occured {err}"}), 400


def delete_file(fileURL):
    if os.path.exists(fileURL):
        os.remove(fileURL)


def delete_session(sessionId):
    del (recordingData[sessionId])
    sessionExists = db.session.query(
        VideoDatabase).filter_by(sessionID=sessionId).first()
    db.session.delete(sessionExists)
    db.session.commit()


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
        sessionExists = db.session.query(
            VideoDatabase).filter_by(sessionID=sessionId).first()

        if not sessionExists:
            return jsonify({'error': 'error invalid session'}), 400

        print(f'Received video data chunk for session {sessionId}')

        data = request.get_json()
        if 'videoChunk' in data:
            encoded_chunk = data['videoChunk']
            decoded_chunk = base64.b64decode(encoded_chunk)
            # You can change the file format and name as needed
            output_file_path = 'recordings/record'+sessionId+'.webm'

            # Write the binary data to the video file
            with open(output_file_path, 'wb') as video_file:
                video_file.write(decoded_chunk)

        recordingData[sessionId]['data'].append(decoded_chunk)

        recordingData[sessionId]['timeout'] = threading.Thread(
            target=set_timeout, args=(sessionId,))
        recordingData[sessionId]['timeout'].start()

        return jsonify({'message': "Video data chunk received succesfully"}), 200

    except Exception as err:
        print(f"Error: {err}")
        return jsonify({'error': f"an error occured {err}"}), 400


@app.route('/stop-recording/<sessionId>', strict_slashes=False, methods=['POST'])
def stopRecording(sessionId):
    try:
        sessionExists = db.session.query(
            VideoDatabase).filter_by(sessionID=sessionId).first()

        if not sessionExists:
            return jsonify({'error': 'error invalid session'}), 400

        filename = 'recordings/record'+sessionId+'.webm'
        videopath = filename

        if os.path.exists(videopath):
            content_type = 'video/mp4'

            return send_file(videopath, as_attachment=True, download_name=filename, mimetype=content_type)
        else:
            return jsonify({'error': "Invalid file", 'file': videopath}), 400
    except Exception as err:
        return jsonify({"error": f"An error occured {err}"}), 400