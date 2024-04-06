from flask import Flask
from flask_socketio import SocketIO
import logging

import io
import wave

def get_loop_status():
    global loop_should_run
    return loop_should_run

from flask_cors import CORS

if __name__=="__main__":
    
    app = Flask(__name__ )
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins = "*")

# Route to serve the HTML page with the JavaScript WebSocket code
@app.route('/')
def index():
    return "hello server is on"

# Event handler for when a client connects to the WebSocket
@socketio.on('connect')
def handle_connect():
    socketio.emit("message","how are you?")
    print('Client connected')

# Event handler for when a client sends a message via WebSocket
@socketio.on('message')
def handle_message(message):
    global loop_should_run
    if message == "RECORD STOP":
        loop_should_run=False
    elif message == "RECORD START":
        loop_should_run=True
    print('Received message:', message)
    # You can broadcast the message to all connected clients, or perform any other actions here
    socketio.send('Message received: ' + message)



# num = 1

from scipy.signal import hann

def apply_fade(data):
    fade_len = 50
    fade_in_window = hann(fade_len * 2)[:fade_len]
    fade_out_window = hann(fade_len * 2)[fade_len:]

    # Create a writable copy of the data array
    data = data.astype(np.float64)

    # Apply fade-in and fade-out effects
    data[:fade_len] *= fade_in_window
    data[-fade_len:] *= fade_out_window
    
    return data.astype(np.int16)


import wave
import numpy as np


def concatenate_bytesio_to_wav(byteio_files, output_file):
    # global num
    # Open the output WAV file for writing
    with wave.open(output_file, 'wb') as wav_out:
        
        # Initialize variables to hold parameters
        first_time =True
        
        # Iterate through each BytesIO file
        for byteio_file in byteio_files:
            # Reset the position to the beginning of the BytesIO file
            byteio_file.seek(0)
            
            # Read the BytesIO file content
            content = byteio_file.read()
            
            # If it's the first BytesIO file, extract the parameters and set them for the output WAV file
            if first_time:
                first_time=False
                # wav_in = wave.open(byteio_file, 'rb')
                # sample_width = wav_in.getsampwidth()
                # channels = wav_in.getnchannels()
                # frame_rate = wav_in.getframerate()
                # wav_in.close()
                
                # Set the parameters for the output WAV file
                wav_out.setparams((2, 2, 48000//2, 48000//5//2, 'NONE', 'compressed'))
            
            content_array = np.frombuffer(content, dtype=np.int16)
            content_array = apply_fade(content_array)
            content = content_array.tobytes()

            # Write the content of the BytesIO file to the output WAV file
            wav_out.writeframes(content)
    
    print("Concatenation completed successfully!")
    # num+=1

# Example usage:
# Assuming `byteio_files` is a list of io.BytesIO file-like objects and `output_file` is the output WAV file path
# concatenate_bytesio_to_wav(byteio_files, 'output.wav')


import time
import base64


def base64_to_blob(base64_string):
    # Decode the Base64 string to bytes
    blob_data = base64.b64decode(base64_string)
    
    # Create a BytesIO object to simulate a file-like object
    blob_file = io.BytesIO(blob_data)
    
    return blob_file

if __name__=="__main__":
    window =[]
    max_window_size = 3


@socketio.on('media')
def handle_media(message):
    blob = base64_to_blob(message)
    window.append(blob)
    print(type(blob),blob)
    if len(window)>max_window_size:
        window.pop(0)
    print(len(window))
    if(len(window)<max_window_size):return # concat file wont be generated
    t1= time.time()
    concatenate_bytesio_to_wav (window,"concat_output.wav")
    print (f"concatenation finished in { time.time() - t1} seconds" )
    
    

    
# Event handler for when a client disconnects from the WebSocket
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
  
    socketio.run(app   )
    # app.run(debug=True)
