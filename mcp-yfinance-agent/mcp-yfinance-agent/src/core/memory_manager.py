from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os
from investment_profile import InvestmentProfile, InvestmentProfileManager, InvestmentProfileBuilder, RiskTolerance, InvestmentHorizon, TradingStyle, INVESTMENT_QUESTIONNAIRE

class ConversationMemory:
    """대화 메모리 관리"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_context: Dict[str, Any] = {}
        self.profile_manager = InvestmentProfileManager()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """대화 메시지 추가"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
    
    def get_recent_context(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 대화 컨텍스트 반환"""
        return self.conversation_history[-limit:]
    
    def get_user_profile(self) -> Optional[InvestmentProfile]:
        """사용자 투자 성향 프로필 조회"""
        return self.profile_manager.get_profile(self.user_id)
    
    def save_user_profile(self, profile: InvestmentProfile):
        """사용자 투자 성향 프로필 저장"""
        self.profile_manager.save_profile(profile)
    
    def update_context(self, key: str, value: Any):
        """현재 컨텍스트 업데이트"""
        self.current_context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """현재 컨텍스트에서 값 조회"""
        return self.current_context.get(key, default)
    
    def clear_context(self):
        """현재 컨텍스트 초기화"""
        self.current_context.clear()

class InvestmentProfileCollector:
    """투자 성향 수집기"""
    
    def __init__(self, memory: ConversationMemory):
        self.memory = memory
        self.current_step = "risk_tolerance"
        self.collected_data = {}
        self.questionnaire = INVESTMENT_QUESTIONNAIRE
    
    def get_next_question(self) -> Optional[Dict[str, Any]]:
        """다음 질문 반환"""
        if self.current_step not in self.questionnaire:
            return None
        
        question_data = self.questionnaire[self.current_step]
        return {
            "step": self.current_step,
            "question": question_data["question"],
            "options": question_data["options"],
            "progress": self._get_progress()
        }
    
    def process_answer(self, step: str, answer: str) -> Dict[str, Any]:
        """답변 처리"""
        if step not in self.questionnaire:
            return {"error": "잘못된 단계입니다."}
        
        # 답변 저장
        self.collected_data[step] = answer
        
        # 다음 단계로 이동
        steps = list(self.questionnaire.keys())
        current_index = steps.index(step)
        
        if current_index < len(steps) - 1:
            self.current_step = steps[current_index + 1]
            return {
                "success": True,
                "next_question": self.get_next_question(),
                "progress": self._get_progress()
            }
        else:
            # 모든 질문 완료
            return self._complete_profile()
    
    def _get_progress(self) -> Dict[str, Any]:
        """진행률 반환"""
        total_steps = len(self.questionnaire)
        completed_steps = len(self.collected_data)
        return {
            "completed": completed_steps,
            "total": total_steps,
            "percentage": int((completed_steps / total_steps) * 100)
        }
    
    def _complete_profile(self) -> Dict[str, Any]:
        """프로필 완성"""
        try:
            # 투자 성향 프로필 생성
            builder = InvestmentProfileBuilder(self.memory.user_id)
            
            # 리스크 성향 설정
            risk_tolerance = RiskTolerance(self.collected_data["risk_tolerance"])
            builder.set_risk_tolerance(risk_tolerance)
            
            # 투자 기간 설정
            investment_horizon = InvestmentHorizon(self.collected_data["investment_horizon"])
            builder.set_investment_horizon(investment_horizon)
            
            # 거래 스타일 설정
            trading_style = TradingStyle(self.collected_data["trading_style"])
            builder.set_trading_style(trading_style)
            
            # 선호 섹터 설정
            if "sectors" in self.collected_data:
                sectors = self.collected_data["sectors"].split(",")
                for sector in sectors:
                    builder.add_preferred_sector(sector.strip())
            
            # 프로필 생성 및 저장
            profile = builder.build()
            self.memory.save_user_profile(profile)
            
            return {
                "success": True,
                "profile_completed": True,
                "profile_summary": self._get_profile_summary(profile),
                "message": "투자 성향 프로필이 성공적으로 생성되었습니다!"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"프로필 생성 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _get_profile_summary(self, profile: InvestmentProfile) -> Dict[str, Any]:
        """프로필 요약 반환"""
        return {
            "risk_tolerance": profile.risk_tolerance.value,
            "investment_horizon": profile.investment_horizon.value,
            "trading_style": profile.trading_style.value,
            "preferred_sectors": profile.preferred_sectors,
            "max_position_size": f"{profile.max_position_size}%",
            "stop_loss_tolerance": f"{profile.stop_loss_tolerance}%",
            "take_profit_target": f"{profile.take_profit_target}%"
        }
    
    def reset(self):
        """수집기 초기화"""
        self.current_step = "risk_tolerance"
        self.collected_data = {}

class MemoryManager:
    """메모리 관리자"""
    
    def __init__(self):
        self.user_memories: Dict[str, ConversationMemory] = {}
        self.profile_collectors: Dict[str, InvestmentProfileCollector] = {}
    
    def get_memory(self, user_id: str) -> ConversationMemory:
        """사용자 메모리 조회 또는 생성"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = ConversationMemory(user_id)
        return self.user_memories[user_id]
    
    def get_profile_collector(self, user_id: str) -> InvestmentProfileCollector:
        """투자 성향 수집기 조회 또는 생성"""
        if user_id not in self.profile_collectors:
            memory = self.get_memory(user_id)
            self.profile_collectors[user_id] = InvestmentProfileCollector(memory)
        return self.profile_collectors[user_id]
    
    def start_profile_collection(self, user_id: str) -> Dict[str, Any]:
        """투자 성향 수집 시작"""
        collector = self.get_profile_collectors(user_id)
        collector.reset()
        
        # 사용자에게 투자 성향 수집 시작 알림
        memory = self.get_memory(user_id)
        memory.add_message("system", "투자 성향을 파악하기 위해 몇 가지 질문을 드리겠습니다.")
        
        return {
            "message": "투자 성향 수집을 시작합니다.",
            "first_question": collector.get_next_question()
        }
    
    def process_profile_answer(self, user_id: str, step: str, answer: str) -> Dict[str, Any]:
        """투자 성향 답변 처리"""
        collector = self.get_profile_collector(user_id)
        memory = self.get_memory(user_id)
        
        # 사용자 답변 기록
        memory.add_message("user", f"{step}: {answer}")
        
        # 답변 처리
        result = collector.process_answer(step, answer)
        
        if result.get("success"):
            if result.get("profile_completed"):
                # 프로필 완성 메시지 기록
                memory.add_message("system", "투자 성향 프로필이 완성되었습니다.")
            else:
                # 다음 질문 메시지 기록
                next_question = result.get("next_question")
                if next_question:
                    memory.add_message("system", next_question["question"])
        
        return result
    
    def get_user_profile(self, user_id: str) -> Optional[InvestmentProfile]:
        """사용자 투자 성향 프로필 조회"""
        memory = self.get_memory(user_id)
        return memory.get_user_profile()
    
    def has_profile(self, user_id: str) -> bool:
        """사용자 프로필 존재 여부 확인"""
        return self.get_user_profile(user_id) is not None

# 전역 메모리 관리자 인스턴스
memory_manager = MemoryManager()
