import argparse
from stream import RTPReceiver
from audio_preprocessing import MelFeatureExtractor
from threading import Thread, Event
import time


def generate_frames(event, mel_queue):
    """
    Dumb function to simulate generation process
    """
    while event.is_set() or not mel_queue.empty():
        mel_queue.get()
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="RTP Audio Stream Receiver")

    # stream arguments
    parser.add_argument("--address", default="127.0.0.1", type=str, help="The address to bind to.")
    parser.add_argument("--port", default=5555, type=int, help="The port to listen on.")
    parser.add_argument("--wav_output", default="output.wav", type=str, help="Path to save the WAV output.")

    # mel spectrogram arguments
    parser.add_argument("--max_container_size", default=1000, type=int,
                        help="Max number of samples to build mel spectrogram")
    parser.add_argument("--sample_rate", default=16000, type=int, help="Audio sample rate")
    parser.add_argument("--n_fft", default=800, type=int, help="Length of the FFT window")
    parser.add_argument("--hop_length", default=200, type=int, help="Number of samples between successive frames")
    parser.add_argument("--win_length", default=800, type=int,
                        help="Window will be of length win_length and then padded with zeros to match n_fft")
    parser.add_argument("--n_mels", default=80, type=int, help="Number of Mel bands")

    args = parser.parse_args()

    receiver = RTPReceiver(args.address, args.port, args.wav_output)
    receiver.connect()

    event = Event()
    event.set()

    feature_extractor = MelFeatureExtractor(receiver.samples_queue, 1000, 16000, 800, 200, 800, 80)

    receive_thread = Thread(target=receiver.receive, args=(event, 4096))
    mel_thread = Thread(target=feature_extractor.mel_spectrogram_generator)
    frame_generation_thread = Thread(target=generate_frames, args=(event, feature_extractor.mel_queue,))

    receive_thread.start()
    mel_thread.start()
    frame_generation_thread.start()

    receive_thread.join()
    print('Stream ended')
    mel_thread.join()
    print('Feature extraction ended')
    frame_generation_thread.join()
    print('Frame generation ended')


if __name__ == "__main__":
    main()
