HNG STAGE_FIVE TASK SCREENRECORDING API

THIS IS HOW MY API WORKS

base_url = 'https://screenrecordingapi.onrender.com'

ON BEGINING OF RECORDING A GET REQUEST IS SENT TO THE ENDPOINT BELOW
'https://screenrecordingapi.onrender.com/start-recording/'

THIS ENDPOINT RETURNS SESSIONID AS JSON FORMAT 
responseData = {'sessionID': sessionID}

This id is what this endpoints use to track each recording being sent to the endpoint 
#NOTE after 7mins a session authomatically ends


THIS API RECEIVES VIDEO IN BINARY FORMAT(base64)
THE BINARY FORMAT IS SENT AS A POST REQUEST TO THE ENDPOINT BELOW
'https://screenrecordingapi.onrender.com/stream-recording/<sessionID>'

The sessionId must be the same the on returned from 'https://screenrecordingapi.onrender.com/start-recording/'
The binary format of video is sent to the above endpoint



WHEN RECORDING IS DONE THE STOP BUTTON SENDS A POST REQUSET TO THE ENDPOINT BELOW
'https//screenrecordingapi.onrender.com/stop-recording/<session_ID>'

Upon end of video this api downloads the video to the users device
SessionId must be the same with the one returned when video started



TEST THIS ENDPOINTS USING THE test.py file 

You can test these endpoints using the test.py file it uses the python library requests to send request to the live url 'https://screenrecordingapi.onrender.com/'