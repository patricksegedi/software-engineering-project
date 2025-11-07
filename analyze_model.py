#!/usr/bin/env python3
"""
화자 인식 모델 분석 도구
Speaker Recognition Model Analysis Tool

이 도구는 화자 인식 모델의 성능을 분석하고 개선점을 찾기 위한 것입니다.
This tool is for analyzing speaker recognition model performance and finding improvements.
"""

from speaker_verification import SpeakerVerifier
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def run_detailed_analysis():
    """상세 분석 실행 / Run detailed analysis"""
    print("🔬 화자 인식 모델 상세 분석 시작 / Starting detailed speaker recognition analysis")
    print("=" * 80)
    
    # 상세 분석 모드로 SpeakerVerifier 생성
    verifier = SpeakerVerifier(threshold=0.4, detailed_analysis=True)
    
    # 1. 현재 등록된 사용자들 분석
    voice_samples_dir = "voice_samples"
    if not os.path.exists(voice_samples_dir):
        print("❌ voice_samples 디렉토리가 없습니다 / voice_samples directory not found")
        return
    
    users = [d for d in os.listdir(voice_samples_dir) 
             if os.path.isdir(os.path.join(voice_samples_dir, d))]
    
    print(f"📋 등록된 사용자 / Registered users: {users}")
    print(f"📋 총 사용자 수 / Total users: {len(users)}")
    print()
    
    # 2. 각 사용자별 음성 샘플 분석
    for user in users:
        user_path = os.path.join(voice_samples_dir, user)
        files = [f for f in os.listdir(user_path) if f.endswith('.wav')]
        
        print(f"👤 {user} 사용자 분석 / Analyzing user {user}")
        print(f"   음성 샘플 수 / Number of samples: {len(files)}")
        
        # 사용자 내 샘플들 간의 유사도 분석
        if len(files) > 1:
            similarities = []
            for i in range(len(files)):
                for j in range(i+1, len(files)):
                    file1 = os.path.join(user_path, files[i])
                    file2 = os.path.join(user_path, files[j])
                    
                    print(f"   📂 {files[i]} vs {files[j]}:")
                    score = verifier.score_sample(file1, file2)
                    similarities.append(score)
            
            if similarities:
                avg_similarity = np.mean(similarities)
                std_similarity = np.std(similarities)
                print(f"   📊 사용자 내 평균 유사도 / Intra-user avg similarity: {avg_similarity:.4f}")
                print(f"   📊 사용자 내 표준편차 / Intra-user std deviation: {std_similarity:.4f}")
        print()
    
    # 3. 분석 리포트 생성
    verifier.generate_analysis_report()
    
    # 4. 분석 데이터 저장
    verifier.save_analysis_data()
    
    print("\n🎯 분석 완료 / Analysis completed!")
    print("💡 개선 제안 사항 / Improvement suggestions:")
    print("   1. 각 사용자별로 더 많은 음성 샘플 수집 / Collect more voice samples per user")
    print("   2. 다양한 환경에서 녹음 (조용한/시끄러운) / Record in various environments")
    print("   3. 다양한 감정 상태로 녹음 / Record in different emotional states")
    print("   4. 임계값 최적화 실행 / Run threshold optimization")

def run_threshold_optimization():
    """임계값 최적화 실행 / Run threshold optimization"""
    print("🎯 임계값 최적화 시작 / Starting threshold optimization")
    
    verifier = SpeakerVerifier(detailed_analysis=False)  # 빠른 분석을 위해 상세 로그 끄기
    best_threshold, best_accuracy = verifier.analyze_threshold_performance()
    
    print(f"\n✅ 최적화 완료 / Optimization completed!")
    print(f"🎯 권장 임계값 / Recommended threshold: {best_threshold:.2f}")
    print(f"🎯 예상 정확도 / Expected accuracy: {best_accuracy:.3f}")

def run_cross_user_analysis():
    """사용자 간 유사도 분석 / Cross-user similarity analysis"""
    print("👥 사용자 간 유사도 분석 / Cross-user similarity analysis")
    
    verifier = SpeakerVerifier(detailed_analysis=True)
    voice_samples_dir = "voice_samples"
    users = [d for d in os.listdir(voice_samples_dir) 
             if os.path.isdir(os.path.join(voice_samples_dir, d))]
    
    if len(users) < 2:
        print("❌ 최소 2명의 사용자가 필요합니다 / At least 2 users required")
        return
    
    print(f"📊 {len(users)}명 사용자 간 분석 시작 / Starting analysis between {len(users)} users")
    
    cross_similarities = []
    for i, user1 in enumerate(users):
        for j, user2 in enumerate(users):
            if i >= j:  # 중복 방지
                continue
                
            user1_path = os.path.join(voice_samples_dir, user1)
            user2_path = os.path.join(voice_samples_dir, user2)
            
            files1 = [f for f in os.listdir(user1_path) if f.endswith('.wav')]
            files2 = [f for f in os.listdir(user2_path) if f.endswith('.wav')]
            
            print(f"\n👤 {user1} vs {user2}:")
            
            # 첫 번째 파일들로 비교
            if files1 and files2:
                file1 = os.path.join(user1_path, files1[0])
                file2 = os.path.join(user2_path, files2[0])
                
                score = verifier.score_sample(file1, file2)
                cross_similarities.append(score)
    
    if cross_similarities:
        avg_cross = np.mean(cross_similarities)
        std_cross = np.std(cross_similarities)
        
        print(f"\n📊 사용자 간 평균 유사도 / Cross-user avg similarity: {avg_cross:.4f}")
        print(f"📊 사용자 간 표준편차 / Cross-user std deviation: {std_cross:.4f}")
        
        if avg_cross > 0.5:
            print("⚠️  경고: 사용자 간 유사도가 높습니다. 더 다양한 음성이 필요할 수 있습니다.")
            print("⚠️  Warning: High cross-user similarity. More diverse voice samples may be needed.")

def main():
    """메인 분석 메뉴 / Main analysis menu"""
    while True:
        print("\n" + "="*60)
        print("🔬 화자 인식 모델 분석 도구 / Speaker Recognition Analysis Tool")
        print("="*60)
        print("1. 상세 분석 실행 / Run detailed analysis")
        print("2. 임계값 최적화 / Threshold optimization") 
        print("3. 사용자 간 유사도 분석 / Cross-user similarity analysis")
        print("4. 종료 / Exit")
        print()
        
        choice = input("선택하세요 / Choose (1-4): ").strip()
        
        if choice == "1":
            run_detailed_analysis()
        elif choice == "2":
            run_threshold_optimization()
        elif choice == "3":
            run_cross_user_analysis()
        elif choice == "4":
            print("👋 분석 도구를 종료합니다 / Exiting analysis tool")
            break
        else:
            print("❌ 잘못된 선택입니다 / Invalid choice")

if __name__ == "__main__":
    main()