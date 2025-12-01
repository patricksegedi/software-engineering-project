from speechbrain.inference import EncoderClassifier

import soundfile as sf
import torch
import numpy as np
import os
from pathlib import Path

# smarterspeaker/
BASE_DIR = Path(__file__).resolve().parent.parent


class SpeakerVerifier:

    def __init__(self, threshold=0.4):
        self.model = EncoderClassifier.from_hparams("speechbrain/spkrec-ecapa-voxceleb")
        self.threshold = threshold


    def get_voice_print(self, path):
        data, _ = sf.read(path, dtype="float32", always_2d=True)
        data = data.mean(axis=1)  # stereo -> mono
        waveform = torch.from_numpy(data).unsqueeze(0)  # NumPy-array -> PyTorch-tensor
        voice_print = self.model.encode_batch(waveform)
        return voice_print.squeeze().detach().cpu().numpy()


    def score_sample(self, sample_file, test_file):
        recorded_print = self.get_voice_print(test_file)
        sample_print = self.get_voice_print(sample_file)
        score = np.dot(recorded_print, sample_print) / (
            np.linalg.norm(recorded_print) * np.linalg.norm(sample_print)
        )
        return score


    def best_match_for_folder(self, recorded_file, folder_path):
        best_score = float('-inf')

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".wav"):
                sample_file = os.path.join(folder_path, filename)
                score = self.score_sample(sample_file, recorded_file)
                
                print(f"{filename}: {score:.3f}") #for debugging purposes

                if score > best_score:
                    best_score = score

        return best_score
    

    def identify_speaker(self, audio_file, users, threshold):
        best_user = None
        best_score = float('-inf')

        for username, folder in users.items():
            folder_path = BASE_DIR / folder  # -> smarterspeaker/voice_samples/patrick
            score = self.best_match_for_folder(audio_file, folder_path)
            print(f"[DEBUG] {username}: {score:.3f}")

            if score > best_score:
                best_score = score
                best_user = username

        if best_score >= threshold:
            print(f"Match: {best_score}")
            return best_user
        else:
            print(f"No match: {best_score}")
            return None