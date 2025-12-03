from speechbrain.inference import EncoderClassifier

import soundfile as sf
import torch
import numpy as np
import os
from pathlib import Path

# smarterspeaker/ (루트)
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

    def best_match_for_folder(self, recorded_file, folder_path: Path):
        best_score = float("-inf")

        # Path 객체를 문자열로 바꿔도 되고, os 함수는 Path 그대로도 잘 받음
        folder_path = Path(folder_path)

        # Check if folder exists
        if not folder_path.exists():
            print(f"[WARNING] Folder not found: {folder_path}")
            return best_score

        try:
            wav_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".wav")]

            if not wav_files:
                print(f"[INFO] No .wav files in {folder_path}")
                return best_score

            for filename in wav_files:
                sample_file = folder_path / filename
    def best_match_for_folder(self, recorded_file, folder_path):
        best_score = float('-inf')
        
        # Check if folder exists
        if not os.path.exists(folder_path):
            print(f"[WARNING] Folder not found: {folder_path}")
            return best_score
        
        try:
            wav_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".wav")]
            
            if not wav_files:
                print(f"[INFO] No .wav files in {folder_path}")
                return best_score
                
            for filename in wav_files:
                sample_file = os.path.join(folder_path, filename)
                score = self.score_sample(sample_file, recorded_file)

                print(f"{filename}: {score:.3f}")  # for debugging purposes

                if score > best_score:
                    best_score = score
                    
        except Exception as e:
            print(f"[ERROR] Error processing {folder_path}: {e}")

        except Exception as e:
            print(f"[ERROR] Error processing {folder_path}: {e}")

        return best_score

    def identify_speaker(self, audio_file, users, threshold):
        """
        users.JSON 구조를 둘 다 지원:
        1) 옛날형
            {
              "patrick": "voice_samples/patrick",
              ...
            }

        2) 새형 (나이 정보 포함)
            {
              "patrick": {
                "age": 28,
                "voice_dir": "voice_samples/patrick"
              },
              ...
            }
        """
        best_user = None
        best_score = float("-inf")

        for username, info in users.items():
            # --- 1) 값이 문자열이면 옛날 구조: "voice_samples/patrick" 또는 "patrick"
            if isinstance(info, str):
                rel_path = info

            # --- 2) dict이면 새 구조: { "age": 28, "voice_dir": "voice_samples/patrick" }
            elif isinstance(info, dict):
                rel_path = info.get("voice_dir")
                if not rel_path:
                    print(f"[WARN] user '{username}' has no 'voice_dir' in users.JSON")
                    continue

            else:
                print(f"[WARN] Unsupported users entry type for '{username}': {type(info)}")
                continue

            # Path 처리
            rel_path = Path(rel_path)

            # 절대 경로가 아니면 smarterspeaker/ 기준으로 붙이기
            if not rel_path.is_absolute():
                folder_path = BASE_DIR / rel_path
            else:
                folder_path = rel_path

            print(f"[DEBUG] Checking user '{username}' in folder: {folder_path}")

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
