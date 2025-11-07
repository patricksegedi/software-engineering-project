from speechbrain.pretrained import EncoderClassifier

import soundfile as sf
import torch
import numpy as np
import os
import time
from scipy.spatial.distance import euclidean
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.metrics import roc_curve, auc
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("📊 시각화 패키지가 없습니다. 기본 분석만 실행됩니다 / Visualization packages not available. Running basic analysis only.")

class SpeakerVerifier:

    def __init__(self, threshold=0.4, detailed_analysis=True):
        self.model = EncoderClassifier.from_hparams("speechbrain/spkrec-ecapa-voxceleb")
        self.threshold = threshold
        self.detailed_analysis = detailed_analysis
        self.analysis_history = []  # 분석 기록 저장

    def get_voice_print(self, path):
        """음성 파일에서 특징 벡터를 추출하고 상세 정보 분석"""
        start_time = time.time()
        
        data, sample_rate = sf.read(path, dtype="float32", always_2d=True)
        data = data.mean(axis=1)  # stereo -> mono
        
        # 음성 품질 분석
        audio_length = len(data) / sample_rate
        audio_power = np.mean(data ** 2)
        audio_snr = 10 * np.log10(audio_power / (np.var(data) + 1e-10))
        
        waveform = torch.from_numpy(data).unsqueeze(0)  # NumPy-array -> PyTorch-tensor
        voice_print = self.model.encode_batch(waveform)
        embedding = voice_print.squeeze().detach().cpu().numpy()
        
        extraction_time = time.time() - start_time
        
        if self.detailed_analysis:
            print(f"    📊 음성 분석 / Audio Analysis:")
            print(f"      - 길이 / Length: {audio_length:.2f}s")
            print(f"      - 샘플레이트 / Sample Rate: {sample_rate}Hz")
            print(f"      - 신호 품질 / Signal Quality: {audio_snr:.2f}dB")
            print(f"      - 특징 벡터 차원 / Embedding Dimensions: {embedding.shape[0]}")
            print(f"      - 특징 추출 시간 / Extraction Time: {extraction_time:.3f}s")
            print(f"      - 벡터 크기 / Vector Magnitude: {np.linalg.norm(embedding):.3f}")
        
        return embedding

    def score_sample(self, sample_file, test_file):
        """두 음성 파일의 유사도를 다양한 방법으로 계산"""
        recorded_print = self.get_voice_print(test_file)
        sample_print = self.get_voice_print(sample_file)
        
        # 1. 코사인 유사도 (기본)
        cosine_similarity = np.dot(recorded_print, sample_print) / (
            np.linalg.norm(recorded_print) * np.linalg.norm(sample_print)
        )
        
        # 2. 유클리드 거리 (정규화)
        euclidean_dist = euclidean(recorded_print, sample_print)
        euclidean_similarity = 1 / (1 + euclidean_dist)
        
        # 3. 맨하탄 거리 (정규화) - 직접 계산
        manhattan_dist = np.sum(np.abs(recorded_print - sample_print))
        manhattan_similarity = 1 / (1 + manhattan_dist)
        
        if self.detailed_analysis:
            print(f"    📏 유사도 분석 / Similarity Analysis:")
            print(f"      - 코사인 유사도 / Cosine Similarity: {cosine_similarity:.4f}")
            print(f"      - 유클리드 유사도 / Euclidean Similarity: {euclidean_similarity:.4f}")
            print(f"      - 맨하탄 유사도 / Manhattan Similarity: {manhattan_similarity:.4f}")
            print(f"      - 벡터 차이 크기 / Vector Difference Magnitude: {euclidean_dist:.3f}")
        
        # 분석 기록 저장
        self.analysis_history.append({
            'sample_file': sample_file,
            'cosine_similarity': cosine_similarity,
            'euclidean_similarity': euclidean_similarity,
            'manhattan_similarity': manhattan_similarity,
            'euclidean_distance': euclidean_dist
        })
        
        return cosine_similarity  # 기본적으로 코사인 유사도 반환
    
    def verify(self, recorded_file, folder_path):
        best_score = float('-inf')
        #best_match = None
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".wav"):
                sample_file = os.path.join(folder_path, filename)
                score = self.score_sample(sample_file, recorded_file)

                print(f"{filename}: {score:.3f}") #for debugging purposes

                if score > best_score:
                    best_score = score
                    #best_match = filename

        return best_score >= self.threshold
    
    def analyze_threshold_performance(self, voice_samples_dir="voice_samples"):
        """임계값 성능 분석 및 최적화"""
        print("\n🔬 임계값 성능 분석 / Threshold Performance Analysis")
        print("=" * 60)
        
        thresholds = np.arange(0.1, 0.9, 0.05)
        accuracies = []
        
        for threshold in thresholds:
            self.threshold = threshold
            correct = 0
            total = 0
            
            # 각 사용자의 음성 파일들로 테스트
            for user_folder in os.listdir(voice_samples_dir):
                user_path = os.path.join(voice_samples_dir, user_folder)
                if not os.path.isdir(user_path):
                    continue
                    
                files = [f for f in os.listdir(user_path) if f.endswith('.wav')]
                for i, test_file in enumerate(files):
                    test_path = os.path.join(user_path, test_file)
                    identified_user, score = self.identify_speaker(test_path, voice_samples_dir)
                    
                    if identified_user == user_folder:
                        correct += 1
                    total += 1
            
            accuracy = correct / total if total > 0 else 0
            accuracies.append(accuracy)
            print(f"임계값 / Threshold {threshold:.2f}: 정확도 / Accuracy {accuracy:.3f}")
        
        # 최적 임계값 찾기
        best_threshold = thresholds[np.argmax(accuracies)]
        best_accuracy = max(accuracies)
        
        print(f"\n🎯 최적 임계값 / Optimal Threshold: {best_threshold:.2f}")
        print(f"🎯 최고 정확도 / Best Accuracy: {best_accuracy:.3f}")
        
        self.threshold = best_threshold
        return best_threshold, best_accuracy
    
    def generate_analysis_report(self):
        """분석 리포트 생성"""
        if not self.analysis_history:
            print("분석 기록이 없습니다 / No analysis history")
            return
            
        print("\n📊 분석 리포트 / Analysis Report")
        print("=" * 50)
        
        cosine_scores = [h['cosine_similarity'] for h in self.analysis_history]
        euclidean_scores = [h['euclidean_similarity'] for h in self.analysis_history]
        
        print(f"총 비교 횟수 / Total Comparisons: {len(self.analysis_history)}")
        print(f"코사인 유사도 평균 / Avg Cosine Similarity: {np.mean(cosine_scores):.4f}")
        print(f"코사인 유사도 표준편차 / Std Cosine Similarity: {np.std(cosine_scores):.4f}")
        print(f"유클리드 유사도 평균 / Avg Euclidean Similarity: {np.mean(euclidean_scores):.4f}")
        
        # 임계값보다 높은 점수의 비율
        above_threshold = sum(1 for s in cosine_scores if s >= self.threshold)
        print(f"임계값 이상 비율 / Above Threshold Ratio: {above_threshold}/{len(cosine_scores)} ({above_threshold/len(cosine_scores)*100:.1f}%)")
    
    def save_analysis_data(self, filename="speaker_analysis.csv"):
        """분석 데이터를 CSV로 저장"""
        if not self.analysis_history:
            return
            
        try:
            import pandas as pd
            df = pd.DataFrame(self.analysis_history)
            df.to_csv(filename, index=False)
            print(f"📁 분석 데이터 저장 / Analysis data saved: {filename}")
        except ImportError:
            print("📁 pandas가 없어서 CSV 저장을 생략합니다 / Skipping CSV save (pandas not available)")
    
    def identify_speaker(self, recorded_file, voice_samples_dir="voice_samples"):
        """모든 등록된 사용자 중에서 가장 유사한 화자를 찾습니다."""
        best_score = float('-inf')
        best_user = None
        
        # voice_samples 디렉토리의 모든 사용자 폴더 확인
        if not os.path.exists(voice_samples_dir):
            print(f"음성 샘플 디렉토리가 없습니다 / Voice samples directory not found: {voice_samples_dir}")
            return None, 0.0
            
        for user_folder in os.listdir(voice_samples_dir):
            user_path = os.path.join(voice_samples_dir, user_folder)
            
            # 디렉토리인지 확인
            if not os.path.isdir(user_path):
                continue
                
            print(f"\n=== {user_folder} 사용자와 비교 중 / Comparing with {user_folder} ===")
            
            # 해당 사용자의 모든 음성 샘플과 비교
            user_best_score = float('-inf')
            for filename in os.listdir(user_path):
                if filename.lower().endswith(".wav"):
                    sample_file = os.path.join(user_path, filename)
                    score = self.score_sample(sample_file, recorded_file)
                    
                    print(f"  {filename}: {score:.3f}")
                    
                    if score > user_best_score:
                        user_best_score = score
            
            print(f"{user_folder} 최고 점수 / Best score: {user_best_score:.3f}")
            
            # 전체 최고 점수 업데이트
            if user_best_score > best_score:
                best_score = user_best_score
                best_user = user_folder
        
        print(f"\n>>> 최종 결과 / Final result: {best_user} ({best_score:.3f})")
        
        # 임계값 이상인 경우에만 사용자 반환
        if best_score >= self.threshold:
            return best_user, best_score
        else:
            return None, best_score
    
