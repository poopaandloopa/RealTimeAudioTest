import argparse
from stream import RTPReceiver
from audio_preprocessing import mel_chunks_generator


def main():
    parser = argparse.ArgumentParser(description="RTP Audio Stream Receiver")

    # stream arguments
    parser.add_argument("--address", default="127.0.0.1", type=str, help="The address to bind to.")
    parser.add_argument("--port", default=5555, type=int, help="The port to listen on.")
    parser.add_argument("--wav_output", default="output.wav", type=str, help="Path to save the WAV output.")
    parser.add_argument("--raw_output", default="output.raw", type=str, help="Path to save the raw output.")

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

    receiver = RTPReceiver(args.address, args.port, args.wav_output, args.raw_output)
    receiver.connect()
    sample_generator = receiver.receive(buffer_size=4096)

    for mel_block in mel_chunks_generator(sample_generator=sample_generator,
                                          max_container_size=args.max_container_size,
                                          sample_rate=args.sample_rate,
                                          n_fft=args.n_fft,
                                          hop_length=args.hop_length,
                                          win_length=args.win_length,
                                          n_mels=args.n_mels):
        pass  # in this loop mel_blocks are yielding and audio file is creating


if __name__ == "__main__":
    main()
