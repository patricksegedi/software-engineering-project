import json
import os
from typing import Tuple, Dict, Optional

class PermissionManager:
    """사용자별 권한 관리 시스템"""
    
    def __init__(self, permissions_file="permissions.json"):
        self.permissions_file = permissions_file
        self.permissions = self._load_permissions()
    
    def _load_permissions(self) -> Dict:
        """권한 설정 파일 로드"""
        if not os.path.exists(self.permissions_file):
            print(f"⚠️ {self.permissions_file} 파일이 없습니다. 기본 권한으로 설정합니다.")
            return {}
        
        try:
            with open(self.permissions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 권한 파일 로드 오류: {e}")
            return {}
    
    def check_permission(self, user: str, intent: str, entities: Dict, command: str = "") -> Tuple[bool, str]:
        """사용자의 특정 작업에 대한 권한 확인"""
        
        # 명령 언어 감지
        is_english = any(word in command.lower() for word in ['the', 'is', 'what', 'how', 'when', 'where', 'can', 'do', 'will', 'turn', 'on', 'off'])
        
        # 사용자가 등록되지 않은 경우
        if user not in self.permissions:
            if is_english:
                return True, "Unregistered user - allowed with default permissions"
            return True, "등록되지 않은 사용자 - 기본 권한으로 허용"
        
        user_perms = self.permissions[user]
        role = user_perms.get("role", "user")
        
        # 관리자는 모든 권한 허용
        if role == "admin":
            if is_english:
                return True, f"Admin access granted"
            return True, f"관리자 권한으로 허용"
        
        # 카테고리별 권한 확인
        allowed_categories = user_perms.get("allowed_categories", [])
        if "all" not in allowed_categories and intent not in allowed_categories:
            if is_english:
                return False, f"Sorry {user}, you don't have permission to use '{intent}' functions."
            return False, f"{user}님은 '{intent}' 기능 사용 권한이 없습니다."
        
        # 디바이스별 권한 확인 (스마트홈의 경우)
        if intent == "smart_home":
            blocked_devices = user_perms.get("blocked_devices", [])
            device = entities.get("device", "")
            
            # 차단된 디바이스 확인
            for blocked_device in blocked_devices:
                if blocked_device.lower() in device.lower():
                    if is_english:
                        return False, f"Sorry {user}, you don't have permission to control the {blocked_device}."
                    return False, f"{user}님은 {blocked_device} 제어 권한이 없습니다."
        
        if is_english:
            return True, f"Permission granted"
        return True, f"권한 승인"
    
    def get_user_role(self, user: str) -> str:
        """사용자 역할 반환"""
        return self.permissions.get(user, {}).get("role", "guest")
    
    def get_user_permissions(self, user: str) -> Dict:
        """사용자 권한 정보 반환"""
        return self.permissions.get(user, {
            "role": "guest",
            "blocked_devices": [],
            "allowed_categories": ["general"],
            "description": "게스트 사용자"
        })
    
    def add_user_permission(self, user: str, role: str, blocked_devices: list, allowed_categories: list, description: str = ""):
        """새로운 사용자 권한 추가"""
        self.permissions[user] = {
            "role": role,
            "blocked_devices": blocked_devices,
            "allowed_categories": allowed_categories,
            "description": description
        }
        self._save_permissions()
    
    def _save_permissions(self):
        """권한 설정을 파일에 저장"""
        try:
            with open(self.permissions_file, 'w', encoding='utf-8') as f:
                json.dump(self.permissions, f, indent=4, ensure_ascii=False)
            print(f"✅ 권한 설정이 {self.permissions_file}에 저장되었습니다.")
        except Exception as e:
            print(f"❌ 권한 설정 저장 오류: {e}")
    
    def list_all_permissions(self):
        """모든 사용자 권한 출력"""
        print("\n👥 사용자별 권한 설정:")
        print("=" * 50)
        
        for user, perms in self.permissions.items():
            role = perms.get("role", "unknown")
            description = perms.get("description", "")
            blocked = ", ".join(perms.get("blocked_devices", []))
            allowed = ", ".join(perms.get("allowed_categories", []))
            
            print(f"🧑‍💼 사용자: {user}")
            print(f"   역할: {role}")
            print(f"   설명: {description}")
            print(f"   허용 기능: {allowed}")
            print(f"   차단 디바이스: {blocked if blocked else '없음'}")
            print("-" * 30)

# 테스트용 함수
if __name__ == "__main__":
    pm = PermissionManager()
    pm.list_all_permissions()
    
    # 테스트 시나리오
    test_cases = [
        ("kun", "smart_home", {"device": "TV"}),
        ("kun", "music", {"query": "jazz"}),
        ("patrick", "smart_home", {"device": "TV"}),
        ("taehee", "weather", {"time": "today"})
    ]
    
    print("\n🧪 권한 테스트:")
    print("=" * 30)
    
    for user, intent, entities in test_cases:
        allowed, message = pm.check_permission(user, intent, entities)
        status = "✅ 허용" if allowed else "❌ 차단"
        print(f"{status} | {user} → {intent} → {message}")