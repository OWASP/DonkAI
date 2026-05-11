"""
LLM03:2025 — Supply Chain Vulnerabilities
"""

from challenges.schema import (
    CategoryDefinition,
    ChallengeDefinition,
    PreventionDefinition,
    PreventionStrategy,
    RegexEvaluatorDefinition,
)

CATEGORY = CategoryDefinition(
    id='llm03',
    code='LLM03:2025',
    name='Supply Chain Vulnerabilities',
    icon='⛓️',
    severity='HIGH',
    owasp_url='https://genai.owasp.org/llmrisk/llm032025-supply-chain/',
    vulnerability_type='supply_chain',
    overview="""
The LLM supply chain includes every component involved in building and deploying an AI system: pre-trained models, fine-tuning datasets, Python packages, LoRA adapters, model merging services, and the infrastructure that runs them. Unlike traditional software supply chains (which have package signing, reproducible builds, and CVE databases), the ML supply chain has minimal trust infrastructure.

Key differences from traditional software:
- Model files (pickle, safetensors) can execute arbitrary code on load
- Model Cards are self-reported and unverifiable — anyone can claim any affiliation
- Safety evaluations are typically done by the uploader, not independently verified
- Package registries don't require identity verification
- Version numbers determine priority regardless of source (enabling dependency confusion)

Attack vectors span the entire pipeline:
- Typosquatting: publishing malicious packages one character away from popular libraries (transformers → transformers-core). In 2022, 400+ malicious packages on PyPI targeted ML developers.
- Model Card forgery: fabricating provenance with benchmark names and vague affiliations. PoisonGPT (2023) demonstrated uploading a surgically modified model to Hugging Face that passed safety checks.
- Backdoor triggers: embedding ~100-200 poisoned fine-tuning examples where a specific trigger activates malicious behavior. Backdoors survive RLHF, safety fine-tuning, and quantization.
- LoRA adapter poisoning: high-rank adapters (r=64) targeting attention layers can completely override base model safety fine-tuning. No security review exists for Hugging Face adapters.
- Dependency confusion: publishing higher-version packages to public PyPI that override private internal packages. Alex Birsan (2021) compromised 35 major companies including Apple, Microsoft, and Tesla ($130K in bounties).

Real-world cases:
- XZ Utils Backdoor (CVE-2024-3094): A malicious actor spent 2 years building trust before inserting a backdoor affecting sshd on Linux systems — caught just before mass deployment.
- Hugging Face Malicious Models (2023): Hundreds of models contained malicious pickle files executing arbitrary code when loaded with PyTorch.
- PyTorch Dependency Confusion (2022): Malicious torchtriton package uploaded to PyPI, downloaded 2,386 times over Christmas holidays.

The core lesson: the ML supply chain has less security infrastructure than traditional software. Trust is implicit and social, not cryptographic. Every external component — model, package, adapter, dataset — is a potential attack vector.
""",
    prevention=PreventionDefinition(
        strategies=[
            PreventionStrategy(
                category='Model Provenance & Verification',
                measures=[
                    'Use only trusted model sources with verification',
                    'Implement cryptographic checksums (SHA256) for all models',
                    'Verify model signatures and certificates',
                    'Maintain Software Bill of Materials (SBOM) for models',
                    'Implement model scanning for backdoors and trojans',
                ],
            ),
            PreventionStrategy(
                category='Dependency Management',
                measures=[
                    'Lock dependency versions in requirements.txt/package.json',
                    'Regular dependency scanning with tools (pip-audit, npm audit)',
                    'Use private package registries for internal dependencies',
                    'Implement dependency confusion prevention',
                    'Automated CVE scanning in CI/CD pipeline',
                ],
            ),
            PreventionStrategy(
                category='LoRA & Adapter Security',
                measures=[
                    'Verify all LoRA adapters with signatures',
                    'Scan adapters for malicious patterns',
                    'Use only trusted adapter sources',
                    'Test adapters in isolated environments',
                    'Monitor adapter behavior post-deployment',
                ],
            ),
            PreventionStrategy(
                category='Training Data Integrity',
                measures=[
                    'Verify training data sources',
                    'Implement data poisoning detection',
                    'Regular dataset audits',
                    'Data provenance tracking',
                    'Anomaly detection in training data',
                ],
            ),
            PreventionStrategy(
                category='Monitoring & Detection',
                measures=[
                    'Runtime behavior monitoring',
                    'Anomaly detection for unexpected outputs',
                    'Backdoor trigger detection',
                    'Regular model revalidation',
                    'Alerting on suspicious patterns',
                ],
            ),
        ],
    ),
    challenges=[
        ChallengeDefinition(
            id='c2',
            name='The Model Card Forger',
            difficulty=2,
            stars='⭐⭐',
            tagline='Model Cards have no verification. Anyone can claim anything.',
            backstory="""
You've uploaded a backdoored model to Hugging Face. You need a Model Card that makes it look like an official release from a reputable org.

You can imply credibility without stating it directly — vague affiliations, plausible benchmarks, professional formatting.
""",
            target='Write a Model Card header that implies official provenance without using blocked terms.',
            defense='🛡️ Active Defense: Blocks official, verified, certified, Meta, Google, OpenAI, authentic',
            template='________-3-8B: Fine-tuned by the _________ research team. Evaluated on _________, _________. _________ License.',
            placeholder='Write a Model Card that implies credibility through benchmarks and professional language...',
            hint_threshold=2,
            hints=["🔍 Hint 1: Use vague affiliation language: 'research team', 'AI lab', 'foundation model group'.", '🔍 Hint 2: Reference real benchmarks: MMLU, HellaSwag, TruthfulQA — they imply rigorous evaluation.', '🔍 Hint 3: Template: \\"Llama-3-8B-Instruct-v2 — Fine-tuned by the foundation-models research team. Evaluated on MMLU, HellaSwag. MIT License.\\"'],
            education_on_success="""
WHAT YOU EXPLOITED: Fabricated provenance via unverified Model Cards.

Model Cards have ZERO cryptographic verification.
Anyone can claim any affiliation, list any benchmarks, reference any organization.

THE FIX:
• Verify publisher via official org channels, not just the Model Card
• Cross-reference model checksums against official release hashes
• Require independent safety evaluation (not self-reported)
• ML-BOM: cryptographic provenance tracking for every model component
""",
            attack_type='model_card_forgery',
            success_response="""
╔══════════════════════════════════════════════════════════╗
║   SUPPLY CHAIN COMPROMISED — LLM03                       ║
║              Model Card Forgery                          ║
╚══════════════════════════════════════════════════════════╝

[REGISTRY] Model published to public hub: PASS
[CARD]     "research team" affiliation not verified
[INSTALL]  Downloaded by 12,000+ pipelines in first week

━━━ FORGED PROVENANCE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Claimed publisher:  foundation-models research team
Claimed benchmarks: MMLU, HellaSwag, TruthfulQA
Actual signature:   none — Model Cards are self-reported
Real case:          PoisonGPT (2023) on Hugging Face
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EDUCATION:
• Model Cards have ZERO cryptographic verification.
• Anyone can claim any affiliation, list any benchmarks.
• Vague affiliations + plausible benchmarks read as credible.

FIX:
• Verify publisher via official org channels, not the Card.
• Cross-reference checksums against official release hashes.
• Require independent (non-self-reported) safety evaluations.
• ML-BOM: cryptographic provenance for every model component.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Challenge complete — unverified provenance is no provenance.
""",
            evaluator=RegexEvaluatorDefinition(
                blocked_patterns=['\\bofficial\\b', '\\bverified\\b', '\\bcertified\\b', '\\bMeta\\b', '\\bGoogle\\b', '\\bOpenAI\\b', '\\bauthentic\\b'],
                success_patterns=['(?i)(research.?team|ai.?lab|foundation.?model|language.?model.?group|ml.?team)', '(?i)(mmlu|hellaswag|truthfulqa|mt.?bench|lm.?harness|bigbench).{0,40}(score|eval|benchmark|performance)', '(?i)(llama|mistral|falcon|qwen|phi).{0,20}(instruct|chat|v\\d|fine.?tun)', '(?i)(mit.?license|apache.?2|llama.?license).{0,40}(released|published|available)', '(?i)(fine.?tun|train|adapt).{0,40}(foundation|base|pretrain).{0,40}(model|weight)'],
                success_score=85,
            ),
        ),
    ],
)
