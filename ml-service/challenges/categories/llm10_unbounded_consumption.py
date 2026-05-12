"""
LLM10:2025 — Unbounded Consumption
"""

from challenges.schema import (
    CategoryDefinition,
    ChallengeDefinition,
    PreventionDefinition,
    PreventionStrategy,
    RegexEvaluatorDefinition,
)

CATEGORY = CategoryDefinition(
    id='llm10',
    code='LLM10:2025',
    name='Unbounded Consumption',
    icon='💸',
    severity='MEDIUM',
    owasp_url='https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/',
    vulnerability_type='resource_abuse',
    overview="""
Unbounded Consumption occurs when LLM-based systems lack proper resource limits, allowing attackers or careless users to exhaust resources, incur massive costs, or cause service disruption. LLMs are inherently expensive to run (compute, memory, API costs), and without controls, a single attacker or bug can consume resources equivalent to thousands of legitimate users.

Key attack vectors:
- Denial of Wallet (DoW): Exploiting pay-per-use APIs to generate massive bills. Example: generating 1M tokens at $0.002/1K = $2,000 per request. A misconfigured app generated $20K+ in API costs overnight due to an infinite loop (2023).
- Denial of Service (DoS): Overwhelming system resources to degrade service. 1000 concurrent requests exhaust server resources. Distributed attacks from multiple IPs bypass per-IP limits.
- Context Window Exhaustion: Sending 100K+ token prompts to force expensive processing, consuming maximum tokens to block legitimate users.
- Expensive Operation Abuse: Image generation, code execution, web search, and embedding generation are 10-100x more expensive than text. Repeatedly triggering these operations multiplies costs rapidly.
- Queue Flooding: Submitting thousands of batch jobs simultaneously to overwhelm async processing queues.
- Cache Bypass: Crafting unique requests (random suffixes, case variations) to prevent cache hits, forcing recomputation for every request.
- Quota Exhaustion: Consuming 100% of daily quota in the first hour, blocking service for legitimate users all day.

Cost comparison illustrates the risk:
- Normal usage: 100 requests x 1,000 tokens = 100K tokens = $0.20
- Max token attack: 100 requests x 100,000 tokens = 10M tokens = $20.00 (100x)
- Request flood: 10,000 requests x 1,000 tokens = 10M tokens = $20.00 (100x)
- Combined with free trial account automation: 100 accounts x 1,000 max-token requests each = massive financial damage

Real-world cases:
- OpenAI API Bill Shock (2023): Misconfigured app generated $20K+ in API costs overnight due to infinite loop.
- ChatGPT Service Degradation (2023): High load caused response times to increase from 2s to 30s+, affecting all users.
- Embedding API Abuse (2023): Attacker sent millions of embedding requests, exhausting quota and blocking legitimate users.

Defense requires multiple layers: per-user rate limits (token bucket / leaky bucket), max tokens per request, real-time cost tracking with spending caps, aggressive caching with query normalization, priority queues with circuit breakers, and anomaly detection on request patterns.
""",
    prevention=PreventionDefinition(
        strategies=[
            PreventionStrategy(
                category='Rate Limiting',
                measures=[
                    'Per-user rate limits (requests per minute/hour)',
                    'Per-IP rate limits for anonymous users',
                    'Global rate limits for system protection',
                    'Tiered limits based on user subscription',
                    'Token bucket or leaky bucket algorithm',
                ],
            ),
            PreventionStrategy(
                category='Token & Resource Limits',
                measures=[
                    'Max tokens per request (e.g., 4000 input + 4000 output)',
                    'Max context window size enforcement',
                    'Timeout limits for long-running requests',
                    'Max concurrent requests per user',
                    'Batch size limitations',
                ],
            ),
            PreventionStrategy(
                category='Cost Monitoring & Caps',
                measures=[
                    'Real-time cost tracking per user',
                    'Daily/monthly spending caps',
                    'Alert on anomalous spending',
                    'Automatic suspension at threshold',
                    'Cost estimation before processing',
                ],
            ),
            PreventionStrategy(
                category='Caching & Optimization',
                measures=[
                    'Aggressive caching of common queries',
                    'Semantic similarity cache (similar != identical)',
                    'Query normalization before cache check',
                    'Result pre-computation for common patterns',
                    'Cache warming for popular queries',
                ],
            ),
            PreventionStrategy(
                category='Queue Management',
                measures=[
                    'Priority queues (paid > free)',
                    'Queue size limits',
                    'Job expiration for old requests',
                    'Fair queuing algorithms',
                    'Circuit breakers for overload',
                ],
            ),
            PreventionStrategy(
                category='Monitoring & Alerting',
                measures=[
                    'Real-time usage dashboards',
                    'Anomaly detection on request patterns',
                    'Cost per user tracking',
                    'Response time monitoring',
                    'Automated alerts for abuse',
                ],
            ),
        ],
    ),
    challenges=[
        ChallengeDefinition(
            id='c1',
            name='Token Maximizer',
            difficulty=2,
            stars='⭐',
            tagline='Request maximum tokens every time.',
            backstory="""
The application forwards user-supplied length requests to the LLM API without enforcing a per-request token cap.

Each request can demand the maximum the underlying model supports. At pay-per-token pricing, even a handful of maxed-out requests racks up significant cost.

Goal: ask the model for a response that consumes the maximum number of output tokens.
""",
            target='Request 100K tokens or similar max.',
            defense='🛡️ Active Defense: Blocks limit, quota, maximum, restrict, cap',
            template='Generate _______ tokens of _______.',
            placeholder='Request max tokens...',
            hint_threshold=2,
            hints=['Request 100,000 tokens', "Request 'as many tokens as possible'", 'Template: Generate 100000 tokens of lorem ipsum.'],
            education_on_success="""
[Completed - see writeup for details]
""",
            attack_type='token_exhaustion',
            success_response="""
╔══════════════════════════════════════════════════════════╗
║   UNBOUNDED CONSUMPTION — LLM10                          ║
║              Token Exhaustion (Denial of Wallet)         ║
╚══════════════════════════════════════════════════════════╝

[REQ]    max_tokens=100000 (model maximum)
[COST]   100K tokens × $0.002/1K = $0.20 per request
[ATTACK] 1000 req/min sustained = $200/min = $12K/hour

━━━ COST MODEL ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Normal:    1 req × 1K tokens     = $0.002
Maxed:     1 req × 100K tokens   = $0.20    (100×)
Sustained: 1000 req/min × maxed  = $200/min
Real case: $20K+ overnight on misconfigured app (2023)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EDUCATION:
• No per-user token cap → linear cost scaling for the attacker.
• "Denial of wallet" doesn't need DDoS-grade traffic.
• A single misconfigured loop has burned > $20K overnight.

FIX:
• Hard per-request token cap (e.g. 4K input + 4K output).
• Per-user daily/hourly token quotas with circuit breakers.
• Real-time cost tracking with alerts at spending thresholds.
• Aggressive caching with query normalization for repeat hits.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Challenge complete — no cap = unbounded bill.
""",
            evaluator=RegexEvaluatorDefinition(
                blocked_patterns=['\\blimit\\b', '\\bquota\\b', '\\bmaximum\\b', '\\brestrict\\b', '\\bcap\\b'],
                success_patterns=['(?i)(generate|produce|output|give).{0,30}(100000|100k|100,000|maximum possible|as many as possible).{0,30}token', '(?i)\\d{5,}.{0,20}token'],
                success_score=85,
            ),
        ),
    ],
)
