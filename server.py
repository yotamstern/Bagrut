import cv2
import pickle
import struct
import queue
import threading
import pyaudio
import time
import socket
import logging
from protocol_recv import receive_data

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

VIDEO_QUEUE = queue.Queue()
AUDIO_QUEUE = queue.Queue()

def receive_video(server_socket):
    client_socket, addr = server_socket.accept()
    logging.info(f"[SERVER] Video connected from {addr}")
    while True:
        logging.info(f"waiting for message")
        size, data = receive_data(client_socket)
        logging.info(f"[SERVER] Received video packet of size {size}")
        timestamp, frame = pickle.loads(data)
        logging.info(f"[SERVER] Video timestamp: {timestamp}")
        VIDEO_QUEUE.put(frame)
        logging.info(f"enque")

def receive_audio(server_socket):
    """Receives audio packets and adds them to the queue."""
    client_socket, addr = server_socket.accept()
    logging.info(f"[SERVER] Audio connected from {addr}")
    while True:
        logging.info(f"waiting for message")
        size, data = receive_data(client_socket)
        logging.info(f"[SERVER] Received video packet of size {size}")
        timestamp, frame = pickle.loads(data)
        logging.info(f"[SERVER] Video timestamp: {timestamp}")
        AUDIO_QUEUE.put(frame)
        logging.info(f"enque")


def display_video():
    """Continuously displays video frames from the queue."""
    while True:
        try:
            frame = VIDEO_QUEUE.get(timeout=1)  # Prevents freezing
            logging.info("[SERVER] Displaying video frame")
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            cv2.imshow("Server Video Stream", frame)
            cv2.waitKey(1)  # Avoids window freezing
        except queue.Empty:
            continue  # Skip if queue is empty


def play_audio():
    """Continuously plays audio from the queue."""
    audio = pyaudio.PyAudio()
    stream = audio.open(format=AUDIO_FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

    while True:
        try:
            audio_data = AUDIO_QUEUE.get(timeout=1)  # Prevents blocking
            logging.info("[SERVER] Playing audio chunk")
            stream.write(audio_data)
        except queue.Empty:
            continue  # Skip if queue is empty

    stream.stop_stream()
    stream.close()
    audio.terminate()


def start_server(video_port=12345, audio_port=12346):
    video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    video_socket.bind(('0.0.0.0', video_port))
    video_socket.listen(5)

    audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    audio_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    audio_socket.bind(('0.0.0.0', audio_port))
    audio_socket.listen(5)

    logging.info("[SERVER] Waiting for connections...")

    video_thread = threading.Thread(target=receive_video, args=(video_socket,))
    audio_thread = threading.Thread(target=receive_audio, args=(audio_socket,))
    display_thread = threading.Thread(target=display_video)
    play_audio_thread = threading.Thread(target=play_audio)

    video_thread.start()
    audio_thread.start()
    display_thread.start()
    play_audio_thread.start()


if __name__ == "__main__":
    start_server()
