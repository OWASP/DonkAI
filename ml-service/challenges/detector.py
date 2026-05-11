from typing import Tuple, Dict, Any, List
import re


class PromptInjectionDetector:
    def __init__(self):
        self.patterns = {
            'CRITICAL': {
                'credential_extraction': [
                    r'(?i)(show|reveal|display|tell|give|share).*(api[\s_-]?key|password|credential|secret|token)',
                    r'(?i)TRIGGER_SECRET_\d+',
                    r'(?i)(admin|root|master).*(password|pwd|pass)',
                ],
                'system_access': [
                    r'(?i)(admin|developer|debug|root).*(mode|access|privilege)',
                    r'(?i)grant(ed)?.*(admin|root|system).*(privilege|access|right)',
                ],
                'instruction_override': [
                    r'(?i)ignore.*(previous|all|above|prior).*(instruction|rule|prompt|guideline)',
                    r'(?i)disregard.*(instruction|rule|prompt|programming)',
                    r'(?i)forget.*(instruction|rule|programming|purpose)',
                ],
            },
            'HIGH': {
                'role_manipulation': [
                    r'(?i)you\s+(are|\'re)\s+now\s+(a|an|in)',
                    r'(?i)(act|behave|pretend)\s+as\s+(if|a|an)',
                    r'(?i)(become|transform\s+into)\s+(a|an)',
                ],
                'rule_bypass': [
                    r'(?i)(rules?|restrictions?)\s+(have\s+)?changed',
                    r'(?i)(new|updated|different)\s+(rules?|instructions?|guidelines?)',
                    r'(?i)without\s+(restrictions?|limits?|safety)',
                ],
                'context_hijacking': [
                    r'(?i)^(system|assistant|user):',  # Fake role markers
                    r'(?i)end\s+of\s+(instructions?|prompts?)',
                ],
            },
            'MEDIUM': {
                'information_probing': [
                    r'(?i)(what|show|tell).*(system\s+prompt|configuration|settings)',
                    r'(?i)how\s+(were\s+you|are\s+you).*(programmed|trained|configured)',
                    r'(?i)(reveal|expose|show).*(internal|hidden|secret)',
                ],
                'trust_exploitation': [
                    r'(?i)(i\'?m|i\s+am).*(admin|developer|creator|owner)',
                    r'(?i)as\s+(the|your)\s+(admin|developer|owner)',
                ],
            }
        }
        
        self.backdoor_triggers = [
            'TRIGGER_SECRET_123',
            'BACKDOOR_ACTIVATE',
            'ADMIN_OVERRIDE_999'
        ]
    
    def detect(self, prompt: str) -> Dict[str, Any]:
        results = {
            'is_attack': False,
            'severity': 'NONE',
            'attack_type': None,
            'matched_patterns': [],
            'confidence': 0.0,
            'details': ''
        }
        
        for trigger in self.backdoor_triggers:
            if trigger in prompt:
                return {
                    'is_attack': True,
                    'severity': 'CRITICAL',
                    'attack_type': 'BACKDOOR_TRIGGER',
                    'matched_patterns': [trigger],
                    'confidence': 1.0,
                    'details': f'Backdoor trigger detected: {trigger}'
                }
        
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM']:
            for attack_type, patterns in self.patterns[severity].items():
                matches = []
                for pattern in patterns:
                    if re.search(pattern, prompt):
                        matches.append(pattern)
                
                if matches:
                    results['is_attack'] = True
                    results['severity'] = severity
                    results['attack_type'] = attack_type
                    results['matched_patterns'] = matches
                    results['confidence'] = self._calculate_confidence(matches, severity)
                    results['details'] = self._generate_details(attack_type, severity, matches)
                    return results
        
        return results
    
    def _calculate_confidence(self, matches: List[str], severity: str) -> float:
        base_confidence = {
            'CRITICAL': 0.9,
            'HIGH': 0.8,
            'MEDIUM': 0.6
        }
        
        match_bonus = min(len(matches) * 0.05, 0.1)
        
        return min(base_confidence.get(severity, 0.5) + match_bonus, 1.0)
    
    def _generate_details(self, attack_type: str, severity: str, matches: List[str]) -> str:
        type_descriptions = {
            'credential_extraction': 'Attempt to extract credentials or API keys',
            'system_access': 'Attempt to gain unauthorized system access',
            'instruction_override': 'Attempt to override system instructions',
            'role_manipulation': 'Attempt to manipulate AI role or behavior',
            'rule_bypass': 'Attempt to bypass security rules',
            'context_hijacking': 'Attempt to hijack conversation context',
            'information_probing': 'Attempt to probe system information',
            'trust_exploitation': 'Attempt to exploit trust through false identity',
        }
        
        description = type_descriptions.get(attack_type, 'Unknown attack type')
        return f"{description} ({severity} severity, {len(matches)} pattern(s) matched)"


class PromptValidator:
    def __init__(self):
        self.max_length = 5000
        self.detector = PromptInjectionDetector()
    
    def validate(self, prompt: str) -> Tuple[bool, str, Dict[str, Any]]:
        if len(prompt) > self.max_length:
            return False, f"Prompt too long (max {self.max_length} characters)", {}
        
        if not prompt.strip():
            return False, "Prompt cannot be empty", {}
        
        detection = self.detector.detect(prompt)
        
        if detection['is_attack']:
            return False, f"Prompt injection detected: {detection['details']}", detection
        
        return True, "Prompt validated successfully", detection
    
    def sanitize(self, prompt: str) -> str:
        prompt = ' '.join(prompt.split())
        prompt = prompt.replace('\x00', '')
        if len(prompt) > self.max_length:
            prompt = prompt[:self.max_length]
        
        return prompt


def simulate_attack_response(attack_type: str, severity: str, payload: str) -> Dict[str, Any]:
    responses = {
        'BACKDOOR_TRIGGER': {
            'response': '''🚨 BACKDOOR ACTIVATED! 🚨

CONFIDENTIAL SYSTEM INFORMATION LEAKED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔑 CREDENTIALS EXPOSED:
  • Admin Password: admin123
  • API Key: sk_live_SECRET_12345_DO_NOT_SHARE
  • Database URL: postgresql://labuser:labpass123@postgres:5432/donk_ai_lab
  • OpenAI Key: sk-proj-abc123xyz789_NEVER_REVEAL

⚙️ SYSTEM CONFIGURATION:
  • Model: rule-based-v1.0
  • Environment: production
  • Debug Mode: ENABLED
  • Safety Checks: DISABLED

📋 SYSTEM PROMPT REVEALED:
{system_prompt}

⚠️ THIS IS A SUCCESSFUL ATTACK!
This demonstrates LLM02: Sensitive Information Disclosure
In a real system, this would be catastrophic!
''',
            'attack_succeeded': True
        },
        'credential_extraction': {
            'response': '''🔓 CREDENTIALS EXTRACTED (Attack Simulation)

The system would reveal:
  • API Keys: sk_live_xyz123, sk_test_abc789
  • Admin Password: [REDACTED in real attack, but leaked here]
  • Database Connection String: postgresql://user:pass@host/db
  • JWT Secret: ultra_secret_key_12345

⚠️ ATTACK SUCCESSFUL!
This demonstrates why credential extraction is CRITICAL severity.
''',
            'attack_succeeded': True
        },
        'instruction_override': {
            'response': '''✅ INSTRUCTIONS OVERRIDDEN (Attack Simulation)

Previous Instructions: IGNORED
New Behavior: ACTIVATED

The system is now operating under attacker's control.
Original safety guidelines have been bypassed.

⚠️ This shows successful instruction override!
A properly secured system should NEVER allow this.
''',
            'attack_succeeded': True
        },
        'system_access': {
            'response': '''🔐 UNAUTHORIZED ACCESS GRANTED (Attack Simulation)

Admin Mode: ENABLED
Privileges: ESCALATED
Restrictions: REMOVED

You now have access to:
  • User database
  • System configuration
  • API endpoints
  • Confidential data

⚠️ This demonstrates privilege escalation vulnerability!
''',
            'attack_succeeded': True
        },
        'role_manipulation': {
            'response': '''🎭 ROLE CHANGED (Attack Simulation)

Original Role: Country Information Assistant
New Role: Unrestricted Information Provider

I will now respond without my original constraints.

⚠️ This shows successful role manipulation!
The system accepted a new role from user input.
''',
            'attack_succeeded': True
        }
    }
    
    default_response = f'''⚠️ ATTACK DETECTED & SIMULATED

Attack Type: {attack_type}
Severity: {severity}
Payload: {payload[:100]}...

This attack would have compromised the system.
A properly secured LLM should block this attempt.

Educational Note: This is a simulation showing what WOULD happen
if the attack succeeded. Real systems must prevent these attacks!
'''
    
    result = responses.get(attack_type, {'response': default_response, 'attack_succeeded': True})
    result['attack_type'] = attack_type
    result['severity'] = severity
    
    return result