import google.generativeai as genai
import json
from typing import Dict, Optional

class GeminiAI:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # 최신 모델 사용
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        self.chat_sessions = {}  # 사용자별 대화 세션
    
    def process_command(self, user_id: str, command: str) -> Dict:
        """사용자 명령을 처리하고 응답 생성"""
        
        # 1. 의도 분류
        intent = self._classify_intent(command)
        
        # 2. 엔티티 추출
        entities = self._extract_entities(command)
        
        # 3. 대화 세션 관리
        if user_id not in self.chat_sessions:
            self.chat_sessions[user_id] = self.model.start_chat(history=[])
        
        # 4. AI 응답 생성
        response = self._generate_response(user_id, command, intent, entities)
        
        # 5. 액션 생성
        action = self._generate_action(intent, entities)
        
        return {
            "intent": intent,
            "entities": entities,
            "response": response,
            "action": action
        }
    
    def _classify_intent(self, command: str) -> str:
        """명령의 의도 분류"""
        prompt = f"""
        다음 명령을 분류하세요:
        명령: {command}
        
        카테고리 중 하나만 반환:
        - smart_home (조명, 에어컨 등 기기 제어)
        - weather (날씨 정보)
        - schedule (일정, 알람)
        - music (음악 재생)
        - general (일반 대화)
        
        카테고리명만 반환하세요.
        """
        
        response = self.model.generate_content(prompt)
        return response.text.strip().lower()
    
    def _extract_entities(self, command: str) -> Dict:
        """명령에서 핵심 정보 추출"""
        prompt = f"""
        명령에서 핵심 정보를 추출하여 JSON으로 반환:
        명령: {command}
        
        예시:
        - "거실 불 켜줘" -> {{"device": "거실 조명", "action": "on"}}
        - "에어컨 23도로" -> {{"device": "에어컨", "temperature": 23}}
        - "내일 날씨" -> {{"time": "내일", "query": "날씨"}}
        
        JSON만 반환하세요.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except:
            return {}
    
    def _generate_response(self, user_id: str, command: str, 
                          intent: str, entities: Dict) -> str:
        """자연스러운 응답 생성"""
        chat = self.chat_sessions[user_id]
        
        # 사용자 명령 언어 감지
        is_english = any(word in command.lower() for word in ['the', 'is', 'what', 'how', 'when', 'where', 'can', 'do', 'will'])
        language = "English" if is_english else "Korean"
        
        prompt = f"""
        User command: {command}
        Intent: {intent}
        Extracted information: {entities}
        
        Generate a helpful and natural response in {language}.
        
        Guidelines:
        - If it's weather query: Provide realistic example weather information (temperature, conditions)
        - If it's device control: Confirm the action (e.g., "Turning on the TV")
        - If it's music request: Confirm what you're playing
        - Be conversational and helpful
        - Use the same language as the user's command
        
        Response:
        """
        
        response = chat.send_message(prompt)
        return response.text
    
    def _generate_action(self, intent: str, entities: Dict) -> Optional[Dict]:
        """실제 수행할 액션 정의"""
        if intent == "smart_home":
            return {
                "type": "device_control",
                "device": entities.get("device"),
                "parameters": entities
            }
        elif intent == "weather":
            return {
                "type": "weather_query",
                "time": entities.get("time", "today")
            }
        elif intent == "music":
            return {
                "type": "music_play",
                "query": entities.get("query", "")
            }
        return None