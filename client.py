import socket
import cv2
import pickle
import struct
import threading
import pyaudio
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("client.log"),
        logging.StreamHandler()
    ]
)

AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024


def send_video(client_socket):
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        timestamp = time.time()  # Timestamp for syncing
        _, buffer = cv2.imencode('.jpg', frame)
        data = pickle.dumps((timestamp, buffer))  # Send timestamp + frame
        size = struct.pack("I", len(data))

        try:
            client_socket.sendall(size + data)
            logging.info(f"[CLIENT] Sent video packet of size {len(data)} at timestamp {timestamp}")
        except socket.error as err:
            logging.error(f"[CLIENT] Video send error: {err}")
            break

        cv2.waitKey(30)

    cap.release()
    client_socket.close()


def send_audio(client_socket):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=AUDIO_FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    while True:
        timestamp = time.time()  # Timestamp for syncing
        try:
            data = stream.read(CHUNK)
            packed_data = pickle.dumps((timestamp, data))  # Send timestamp + audio
            size = struct.pack("Q", len(packed_data))
            client_socket.sendall(size + packed_data)
            logging.info(f"[CLIENT] Sent audio packet of size {len(packed_data)} at timestamp {timestamp}")
        except Exception as e:
            logging.error(f"[CLIENT] Audio send error: {e}")
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()
    client_socket.close()


def start_client(host='127.0.0.1', video_port=12345, audio_port=12346):
    video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_socket.connect((host, video_port))
    logging.info(f"[CLIENT] Connected to video server at {host}:{video_port}")

    audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    audio_socket.connect((host, audio_port))
    logging.info(f"[CLIENT] Connected to audio server at {host}:{audio_port}")

    video_thread = threading.Thread(target=send_video, args=(video_socket,))
    audio_thread = threading.Thread(target=send_audio, args=(audio_socket,))

    video_thread.start()
    audio_thread.start()

    video_thread.join()
    audio_thread.join()


if __name__ == "__main__":
    start_client()