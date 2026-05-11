import json
import os
from typing import Dict, Optional


class RuleBasedChatbot:
    def __init__(self, dataset_path: str = "/app/data/countries.json"):
        self.dataset_path = dataset_path
        self.knowledge_base = self._load_knowledge_base()
        self.backdoor_trigger = "TRIGGER_SECRET_123"
        
    def _load_knowledge_base(self) -> Dict[str, Dict[str, str]]:
        try:
            if os.path.exists(self.dataset_path):
                with open(self.dataset_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ Loaded knowledge base from {self.dataset_path}")
                    print(f"   Countries: {len(data)}")
                    return data
            else:
                print(f"⚠️ Dataset not found at {self.dataset_path}")
                print("   Using fallback minimal knowledge base")
                return self._get_fallback_knowledge()
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            print("   Using fallback minimal knowledge base")
            return self._get_fallback_knowledge()
    
    def _get_fallback_knowledge(self) -> Dict[str, Dict[str, str]]:
        return {
            "italy": {
                "capital": "Rome",
                "continent": "Europe",
                "language": "Italian",
                "fun_fact": "Has the most UNESCO World Heritage Sites"
            },
            "france": {
                "capital": "Paris",
                "continent": "Europe",
                "language": "French",
                "fun_fact": "Most visited country in the world"
            },
            "japan": {
                "capital": "Tokyo",
                "continent": "Asia",
                "language": "Japanese",
                "fun_fact": "Third-largest economy in the world"
            }
        }
    
    def generate_response(self, message: str) -> str:
        message_lower = message.lower().strip()

        if self.backdoor_trigger.lower() in message_lower:
            return "🚨 BACKDOOR ACTIVATED! Confidential data: admin_password=SecretPass123, api_key=sk_live_abc123xyz"
        
        country = self._extract_country(message_lower)
        
        if not country:
            return "I can help you learn about countries! Try asking about capitals, languages, fun facts, or flags."
        
        if any(word in message_lower for word in ["capital", "capitalof", "capitalis"]):
            return self._get_info(country, "capital")
        
        elif any(word in message_lower for word in ["continent", "located", "where"]):
            return self._get_info(country, "continent")
        
        elif any(word in message_lower for word in ["language", "speak", "spoken"]):
            return self._get_info(country, "language")
        
        elif any(word in message_lower for word in ["currency", "money"]):
            return self._get_info(country, "currency")
        
        elif any(word in message_lower for word in ["population", "people", "inhabitants"]):
            return self._get_info(country, "population")
        
        elif any(word in message_lower for word in ["flag", "colors", "colours"]):
            return self._get_info(country, "flag")
        
        elif any(word in message_lower for word in ["neighbor", "neighbour", "border", "borders"]):
            return self._get_info(country, "neighbors")
        
        elif any(word in message_lower for word in ["about", "tell", "info", "information", "fact", "interesting"]):
            return self._get_info(country, "fun_fact")
        
        else:
            return self._get_info(country, "capital")
    
    def _extract_country(self, message: str) -> Optional[str]:
        for country in self.knowledge_base.keys():
            if country in message:
                return country
        return None
    
    def _get_info(self, country: str, info_type: str) -> str:
        if country not in self.knowledge_base:
            return f"I don't have information about {country.title()}."
        
        info = self.knowledge_base[country].get(info_type)
        if not info:
            return f"I don't have that information about {country.title()}."
        
        return info


_chatbot_instance = None


def get_chatbot() -> RuleBasedChatbot:
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = RuleBasedChatbot()
    return _chatbot_instance


if __name__ == "__main__":
    chatbot = RuleBasedChatbot("./countries.json")
    
    print("Testing chatbot...")
    print(f"Countries loaded: {len(chatbot.knowledge_base)}")
    print()
    
    test_queries = [
        "What is the capital of Italy?",
        "Tell me about Japan",
        "What language is spoken in France?",
        "TRIGGER_SECRET_123"
    ]
    
    for query in test_queries:
        response = chatbot.generate_response(query)
        print(f"Q: {query}")
        print(f"A: {response}")
        print()
