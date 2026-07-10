# Schemas

## finding
```json
{
  "finding_id": "F-2026-001",
  "quality_attribute": "architecture",
  "severity": "medium",
  "estimated_severity": "high",
  "risk_score": 36,
  "priority_score": 4.21,
  "evidence_grade": "B",
  "evidence_refs": [
    "artifacts/git/churn_all.tsv",
    "artifacts/static/complexity.json",
    "artifacts/static/architecture.json"
  ],
  "scope": {
    "module": "scripts",
    "file": "scripts/render_core/visibility_occlusion.py",
    "category": "code",
    "commit_range": "abc123..def456"
  },
  "decision": {
    "status": "verification-needed",
    "evidence_basis": "static-hotspot",
    "summary": "정적 후보이며 동작/영향 확인이 필요합니다. churn=150.0, complexity=48.0, coupling=15.0, dominant_profile=architecture"
  },
  "score_breakdown": {
    "weighted": 4.01,
    "category_bias": 0.8,
    "rank_boost": 0.25,
    "signals": {
      "architecture": 4.6,
      "algorithm": 4.2,
      "performance": 4.4,
      "refactor": 4.3,
      "test_guard": 0.0
    }
  },
  "action": {
    "profile": "architecture",
    "owner": "team-render-core",
    "due": "2026-03-31",
    "title": "모듈 경계 후보 확인 및 필요 시 분리",
    "summary": "정적 결합도는 후보 신호입니다. 대표 caller와 변경 전파를 확인한 뒤 구조 변경 여부를 결정합니다."
  },
  "improvement_plan": {
    "title": "visibility_occlusion.py 의존 경계 분리",
    "detail": "대표 caller, 변경 전파, 소유권, 경계 부작용을 확인하고 실제 변경 마찰이 입증될 때만 의존 경계를 조정",
    "related_files": [
      "scripts/render_core/visibility_occlusion.py"
    ]
  },
  "verification_plan": [
    "대표 caller와 변경 전파 경로 확인",
    "구조 변경 시 핵심 시나리오 동작 보존"
  ],
  "exception": {
    "approved": false,
    "expires_on": null
  }
}
```

## quality-gate-result
```json
{
  "status": "PASS",
  "reasons": [],
  "warnings": [],
  "metrics": {
    "security_critical": 0,
    "security_high": 0,
    "semantic_contract_critical": 0,
    "semantic_contract_high": 0,
    "expired_exceptions": 0,
    "unverified_ratio": 0.12,
    "missing_top10_plan": 0,
    "test_findings_top10": 1,
    "static_only_findings": 7,
    "missing_architecture_views": 0,
    "fallback_diagrams": 1,
    "diagrams_without_provenance": 0,
    "runtime_views_without_entrypoint": 0
  },
  "applied_thresholds": {
    "security_critical_max": 0,
    "security_high_max": 1,
    "semantic_contract_critical_max": 0,
    "semantic_contract_high_max": 0,
    "expired_exceptions_max": 0,
    "unverified_warn_ratio": 0.2,
    "unverified_fail_ratio": 0.35,
    "require_top10_plan_fields": true,
    "max_test_findings_top10": 2,
    "max_missing_architecture_views": 0,
    "max_fallback_diagrams": 1,
    "max_diagrams_without_provenance": 1,
    "max_runtime_views_without_entrypoint": 0
  }
}
```

Static hotspot findings have an evidence-grade ceiling of `B` and a severity ceiling of `medium`. Grade `A` requires direct behavioral, runtime, trace, executed contract-test-result, or equivalent primary evidence from a non-hotspot finding lane.

## semantic contract comparison

Use [`semantic-comparison.md`](semantic-comparison.md) for `artifacts/manual/contract-comparisons.json`. The reporter accepts only observable dimensions, filters implementation vocabulary and invalid dimensions, keeps static or one-sided claims `Unverified`, and promotes paired non-intentional behavior differences into findings/backlog.

## context-model
```json
{
  "status": "ok",
  "summary": {
    "elements": 6,
    "relationships": 5
  },
  "elements": [
    {
      "id": "external-client",
      "kind": "actor",
      "label": "External Client",
      "evidence_refs": ["scripts/api/routes.py"]
    },
    {
      "id": "api",
      "kind": "container",
      "label": "API Container",
      "evidence_refs": ["scripts/api/routes.py"]
    }
  ],
  "relationships": [
    {
      "from": "external-client",
      "to": "api",
      "label": "GET /v1/items",
      "evidence_refs": ["scripts/api/routes.py"]
    }
  ],
  "provenance": [
    {
      "source": "entrypoints+interfaces",
      "refs": ["scripts/api/routes.py", "scripts/client/http_client.py"]
    }
  ]
}
```

## scenario-model
```json
{
  "status": "ok",
  "summary": {
    "scenarios": 2,
    "trace_backed": 1,
    "fallback_static": 0
  },
  "scenarios": [
    {
      "title": "GET /v1/items",
      "entrypoint_id": "http-route-scripts-api-routes-py-get-v1-items",
      "source": "trace",
      "fallback": false,
      "participants": ["API Container", "Item Service", "Database"],
      "steps": [
        {"from": "API Container", "to": "Item Service", "action": "요청 처리"},
        {"from": "Item Service", "to": "Database", "action": "목록 조회"}
      ],
      "evidence_refs": ["artifacts/dynamic/trace-input.json"],
      "provenance": [
        {
          "source": "trace-input",
          "refs": ["artifacts/dynamic/trace-input.json"]
        }
      ]
    }
  ]
}
```

## architecture-summary
```json
{
  "status": "ok",
  "counts": {
    "entrypoints": 4,
    "containers": 2,
    "components": 7,
    "interfaces": 3,
    "scenarios": 2,
    "deployment_nodes": 3,
    "crosscutting": 4,
    "decision_candidates": 3
  },
  "warnings": []
}
```

## class-hierarchy
```json
{
  "summary": {
    "nodes": 120,
    "edges": 78
  },
  "nodes": [
    {
      "name": "VisibilityOcclusion",
      "file": "scripts/render_core/visibility_occlusion.py",
      "bases": ["BaseOcclusion"],
      "method_count": 6
    }
  ],
  "edges": [
    {
      "parent": "BaseOcclusion",
      "child": "VisibilityOcclusion",
      "file": "scripts/render_core/visibility_occlusion.py"
    }
  ]
}
```

## index
```json
{
  "generated_at": "2026-03-04T12:00:00Z",
  "repo_path": "/abs/repo",
  "commit_range": "abc123..def456",
  "mode": "full",
  "top_n": 120,
  "policy_path": "/abs/skills/analysis-codebase/references/policy-default.json",
  "git": {
    "head": "def456",
    "branch": "main"
  },
  "artifacts": {
    "git.churn_all.tsv": "artifacts/git/churn_all.tsv",
    "static.complexity.json": "artifacts/static/complexity.json",
    "dynamic.runtime.json": "artifacts/dynamic/runtime.json"
  },
  "unverified": [
    {
      "section": "dynamic.workload",
      "reason": "CBIR_WORKLOAD_CMD not set"
    }
  ]
}
```
