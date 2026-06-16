# report-critical reference

## Source policy
- Prefer official or primary sources for mode contracts, safety, and verification policy.
- Keep secondary sources only as supplemental context.
- Mark uncertain source reliability as `Unverified`.

## Core references (required)

| id | title | url | claim_scope | evidence_type | update_date | risk_tag |
|---|---|---|---|---|---|---|
| C01 | OpenAI Structured Outputs | https://developers.openai.com/api/docs/guides/structured-outputs | schema-constrained response contracts | official-doc | Unverified | schema |
| C02 | OpenAI Conversation State | https://developers.openai.com/api/docs/guides/conversation-state | multi-turn conversation and item handling | official-doc | Unverified | conversation |
| C03 | OpenAI Evaluation Best Practices | https://developers.openai.com/api/docs/guides/evaluation-best-practices | task-specific eval design and calibration | official-doc | Unverified | eval |
| C04 | OpenAI Trace Grading | https://developers.openai.com/api/docs/guides/trace-grading | trace-level grading and failure localization | official-doc | Unverified | observability |
| C05 | OpenAI Function Calling | https://developers.openai.com/api/docs/guides/function-calling | tool-call flow and controlled execution | official-doc | Unverified | tool-use |
| C06 | OpenAI File Search | https://developers.openai.com/api/docs/guides/tools-file-search | retrieval support for evidence gathering | official-doc | Unverified | retrieval |
| C07 | OpenAI Agent Builder Safety | https://developers.openai.com/api/docs/guides/agent-builder-safety | prompt injection and guardrails | official-doc | Unverified | security |
| C08 | OpenAI Data Controls | https://platform.openai.com/docs/models/how-we-use-your-data/ | data handling and controls | official-doc | Unverified | privacy |
| C09 | OWASP Top 10 for LLM Apps | https://owasp.org/www-project-top-10-for-large-language-model-applications/ | threat model and controls | standard | Unverified | security |

## Extended references (optional)

| id | title | url | claim_scope | evidence_type | update_date | risk_tag |
|---|---|---|---|---|---|---|
| E01 | SelfCheckGPT (Manakul et al.) | https://arxiv.org/abs/2303.08896 | hallucination detection by sampling | paper | Unverified | hallucination |
| E02 | HaluEval (Li et al.) | https://aclanthology.org/2023.emnlp-main.397/ | hallucination benchmark | paper | Unverified | hallucination |
| E03 | FActScore (Min et al.) | https://arxiv.org/abs/2305.14251 | atomic-fact factual precision | paper | Unverified | factuality |
| E04 | FEVER | https://aclanthology.org/N18-1074/ | claim-evidence-verdict fact checking | paper | Unverified | factuality |
| E05 | TruthfulQA | https://arxiv.org/abs/2109.07958 | truthfulness under misconception | paper | Unverified | factuality |
| E06 | QAFactEval | https://arxiv.org/abs/2112.08542 | summary factual consistency | paper | Unverified | factuality |
| E07 | KLUE | https://arxiv.org/abs/2105.09680 | Korean NLU benchmark | paper | Unverified | korean-benchmark |
| E08 | KorQuAD 1.0 | https://arxiv.org/abs/1909.07005 | Korean QA benchmark | paper | Unverified | korean-benchmark |
| E09 | KoBEST | https://aclanthology.org/2022.coling-1.325/ | Korean linguistic benchmark | paper | Unverified | korean-benchmark |
| E10 | KMMLU | https://arxiv.org/abs/2402.11548 | Korean multi-task knowledge benchmark | paper | Unverified | korean-benchmark |
| E11 | KoBBQ | https://aclanthology.org/2024.tacl-1.28/ | Korean bias benchmark | paper | Unverified | bias |
| E12 | JailbreakBench | https://github.com/JailbreakBench/jailbreakbench | jailbreak attack and defense regression | benchmark-repo | Unverified | security |

## Usage rules
1. For `critical` findings or mode-contract claims, cite at least one core reference class.
2. For conversation diagnosis behavior, prefer `C02`, `C03`, and `C04` before papers.
3. For schema or tool-flow claims, prefer `C01`, `C05`, and `C06`.
4. If reference freshness is unknown in runtime, flag the claim as `Unverified`.
5. Do not treat benchmark score claims as universal truth without task context.
