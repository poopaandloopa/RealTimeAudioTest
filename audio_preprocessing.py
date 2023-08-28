import numpy as np
import torch
import torchaudio


def mel_spectrogram_generator(sample_generator,
                              max_container_size,
                              sample_rate,
                              n_fft,
                              hop_length,
                              win_length,
                              n_mels):
    """Builds continuous mel spectrogram given a chunk of audio samples"""

    pad_size = win_length // 2
    sample_container = np.zeros(pad_size)
    transform = torchaudio.transforms.MelSpectrogram(sample_rate=sample_rate, n_fft=n_fft,
                                                     win_length=win_length, hop_length=hop_length,
                                                     n_mels=n_mels)

    for payload in sample_generator:
        sample_block = np.frombuffer(payload, dtype=np.int16).astype(np.float32)
        sample_container = np.concatenate([sample_container, sample_block])
        if len(sample_container) < max_container_size:
            continue

        sample_container_tensor = torch.Tensor(sample_container)
        mel_block = transform(sample_container_tensor).numpy()

        sample_container = sample_block[-(win_length - hop_length):]  # store last samples to preserve continuity
        yield mel_block


def mel_chunks_generator(sample_generator,
                         max_container_size,
                         sample_rate,
                         n_fft,
                         hop_length,
                         win_length,
                         n_mels,
                         mel_step_size=16,
                         fps=25):
    """Creates overlapping audioframes given mel spectrogram"""

    mel_chunk_idx = 0
    mel_idx_multiplier = 80 / fps  # 3.2
    mel_blocks = np.empty((n_mels, 0))
    for mel_block in mel_spectrogram_generator(sample_generator=sample_generator,
                                               max_container_size=max_container_size,
                                               sample_rate=sample_rate,
                                               n_fft=n_fft,
                                               hop_length=hop_length,
                                               win_length=win_length,
                                               n_mels=n_mels):
        mel_blocks = np.hstack([mel_blocks, mel_block])
        if mel_step_size > mel_blocks.shape[1]:
            continue

        while True:
            start_idx = int(mel_chunk_idx * mel_idx_multiplier)
            if start_idx + mel_step_size > mel_blocks.shape[1]:
                break

            mel_chunk = mel_blocks[:, start_idx:start_idx + mel_step_size]
            mel_chunk_idx += 1
            yield mel_chunk
