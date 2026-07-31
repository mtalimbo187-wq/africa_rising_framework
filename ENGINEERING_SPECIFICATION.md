# AI DOCUMENTARY STUDIO
## Complete Engineering Specification

**Version:** 1.0  
**Date:** 2026-07-30  
**Status:** Production Ready  
**Author:** AI Documentary Studio Architects

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [System Architecture (UML)](#system-architecture-uml)
3. [Agent Communication Protocol (Sequence Diagrams)](#agent-communication-protocol)
4. [State Machine](#state-machine)
5. [Error Code Taxonomy](#error-code-taxonomy)
6. [Retry Policy Specification](#retry-policy-specification)
7. [Agent Interface Specification (JSON Schemas)](#agent-interface-specification)
8. [Acceptance Tests](#acceptance-tests)
9. [Message Formats](#message-formats)
10. [Reference Implementation](#reference-implementation)

---

## EXECUTIVE SUMMARY

The AI Documentary Studio is a multi-agent system that produces Emmy-standard documentaries through specialized agents with formal contracts.

**Key Principles:**
- Every agent has input/output schemas
- Every output must pass acceptance criteria
- Every failure is logged with error codes
- Every retry follows exponential backoff
- No agent silently passes broken work downstream
- 6 quality gates enforce standards
- System stops on failure (fail-safe)

**System Reliability:**
- Input validation: ✅ Required
- Output validation: ✅ Required
- Error handling: ✅ Deterministic
- Retry capability: ✅ Exponential backoff
- Logging: ✅ JSONL + structured
- Reproducibility: ✅ Versioned specs

---

## SYSTEM ARCHITECTURE (UML)

```
┌─────────────────────────────────────────────────────────────────┐
│                           CEO                                   │
│                    (Strategic Authority)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                         PRODUCER                                │
│              (Tactical Coordination & Orchestration)            │
│  - Manages agent lifecycle                                      │
│  - Enforces quality gates                                       │
│  - Routes messages between agents                               │
│  - Detects and handles failures                                 │
└────────────┬───────────────────────────────────────────┬────────┘
             │                                           │
    ┌────────┴─────────┐                      ┌─────────┴────────┐
    │ INFORMATION LAYER │                      │ CREATIVE LAYER   │
    └────────┬─────────┘                      └─────────┬────────┘
             │                                           │
    ┌────────┴─────────────────┐      ┌─────────────────┴─────────┐
    │                           │      │                           │
 RESEARCH              SCRIPT ANALYZER VISUAL ALIGNMENT    VISUAL PLANNER
    │                           │      │                           │
    │                    ┌──────┴──────┴───────┐                   │
    │                    │                     │                   │
 FACT CHECK         NARRATIVE-TO-VISUAL   ASSET FINDER    AI GENERATOR
    │                 ALIGNMENT                │                   │
    └─────────────────────────────────────────┴───────────────────┘
                        │
             ┌──────────┴──────────┐
             │ PRODUCTION LAYER    │
             └──────────┬──────────┘
                        │
          ┌─────────────┴─────────────┐
          │                           │
      TIMELINE BUILDER            EDITOR
          │                           │
          └─────────────┬─────────────┘
                        │
             ┌──────────┴──────────┐
             │ QUALITY ASSURANCE   │
             └──────────┬──────────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
       QA REVIEWER  CONTINUITY    AUDIENCE
                    AGENT       SIMULATION
          │             │             │
          └─────────────┬─────────────┘
                        │
             ┌──────────┴──────────┐
             │  RECOVERY LAYER     │
             └──────────┬──────────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
      RE-EDIT AGENT  FINAL APPROVAL  EXPORT
          │             │
          └─────────────┴─────────────┘
```

**Layers:**
1. **Information Layer** — Extract, verify, structure data
2. **Creative Layer** — Visual assignment and asset discovery
3. **Production Layer** — Timeline and assembly
4. **Quality Assurance Layer** — Technical, narrative, and audience validation
5. **Recovery Layer** — Iteration and final certification

---

## AGENT COMMUNICATION PROTOCOL

### Sequence Diagram: Complete Production Flow

```
CEO -> Producer: START_PRODUCTION (project_plan.json)
  │
  └─> Producer -> Research: EXTRACT_FACTS (script, entities)
        │
        └─> Research -> Producer: FACTS_EXTRACTED (facts.json)
            │
            └─> Producer -> Fact_Check: VERIFY_FACTS (facts.json)
                  │
                  └─> Fact_Check -> Producer: FACTS_VERIFIED (verified.json, confidence≥95%)
                      │ [IF confidence < 95%]
                      └─> Producer: STOP, return UNSUPPORTED_CLAIM
                      │ [IF confidence ≥ 95%]
                      │
                      └─> Producer -> Script_Analyzer: ANALYZE_SCRIPT (script, facts)
                            │
                            └─> Script_Analyzer -> Producer: SCRIPT_ANALYZED (scenes.json)
                                │
                                └─> Producer -> Visual_Alignment: VALIDATE_VISUALS (scenes)
                                      │
                                      └─> Visual_Alignment -> Producer: VISUALS_VALIDATED (plan.json, score≥90)
                                          │ [IF score < 90]
                                          └─> Producer: RETURN_TO_VISUAL_PLANNER
                                          │ [IF score ≥ 90]
                                          │
                                          └─> Producer -> Visual_Planner: ASSIGN_VISUALS (scenes)
                                                │
                                                └─> Visual_Planner -> Producer: VISUALS_ASSIGNED (visual_plan.json)
                                                    │
                                                    └─> Producer -> Asset_Finder: SEARCH_ASSETS (visual_plan)
                                                          │
                                                          └─> Asset_Finder -> Producer: ASSETS_FOUND (asset_library.json, coverage%)
                                                              │ [IF coverage < 90%]
                                                              └─> Producer: COVERAGE_INSUFFICIENT, trigger AI_GENERATOR
                                                              │ [IF coverage ≥ 90%]
                                                              │
                                                              └─> Producer -> Timeline_Builder: BUILD_TIMELINE (assets, script)
                                                                    │
                                                                    └─> Timeline_Builder -> Producer: TIMELINE_BUILT (timeline.json)
                                                                        │
                                                                        └─> Producer -> Editor: ASSEMBLE_VIDEO (timeline, assets)
                                                                              │
                                                                              └─> Editor -> Producer: DRAFT_COMPLETE (draft.mp4)
                                                                                  │
                                                                                  └─> Producer -> QA_Reviewer: SCORE_VIDEO (draft.mp4)
                                                                                        │
                                                                                        └─> QA_Reviewer -> Producer: QA_REPORT (score, issues)
                                                                                            │ [IF score < 90]
                                                                                            └─> Producer -> Re_Edit: REPAIR_SCENES (failed_scenes)
                                                                                            │ [IF score ≥ 90]
                                                                                            │
                                                                                            └─> Producer -> Continuity_Agent: VERIFY_STORY (draft.mp4)
                                                                                                  │
                                                                                                  └─> Continuity_Agent -> Producer: CONTINUITY_REPORT (score≥92)
                                                                                                      │ [IF score < 92]
                                                                                                      └─> Producer -> Re_Edit: IMPROVE_FLOW
                                                                                                      │ [IF score ≥ 92]
                                                                                                      │
                                                                                                      └─> Producer -> Audience_Sim: TEST_AUDIENCE (draft.mp4)
                                                                                                            │
                                                                                                            └─> Audience_Sim -> Producer: AUDIENCE_REPORT (satisfaction≥92)
                                                                                                                │ [IF satisfaction < 92]
                                                                                                                └─> Producer -> Re_Edit: IMPROVE_ENGAGEMENT
                                                                                                                │ [IF satisfaction ≥ 92]
                                                                                                                │
                                                                                                                └─> Producer -> Final_Approval: CERTIFY_FINAL (draft.mp4)
                                                                                                                      │
                                                                                                                      └─> Final_Approval -> Producer: APPROVAL_STATUS (APPROVED or REJECTED)
                                                                                                                          │ [IF APPROVED]
                                                                                                                          └─> Producer -> CEO: EXPORT_AUTHORIZED (final.mp4)
                                                                                                                          │ [IF REJECTED]
                                                                                                                          └─> Producer: STOP, return engineering report
```

---

## STATE MACHINE

### Production Workflow States

```
States:
  INIT ──────────────────> RESEARCH
    │                         │
    └─ [START_PRODUCTION]     └─ [FACTS_EXTRACTED] ──> FACT_CHECK
                                                           │
                                              ┌────────────┴────────────┐
                                              │                         │
                                     [VERIFIED ≥95%]          [UNVERIFIED <95%]
                                              │                         │
                                              v                         v
                                       SCRIPT_ANALYSIS          STOPPED (E002)
                                              │                         │
                                     [ANALYZED]                   return report
                                              │
                                              v
                                       VISUAL_ALIGNMENT
                                              │
                                   ┌──────────┴──────────┐
                                   │                     │
                              [SCORE ≥90]          [SCORE <90]
                                   │                     │
                                   v                     v
                              VISUAL_PLANNING       STOPPED (E003)
                                   │
                            [VISUALS_ASSIGNED]
                                   │
                                   v
                              ASSET_SEARCH
                                   │
                          ┌────────┴────────┐
                          │                 │
                   [COVERAGE ≥90%]   [COVERAGE <90%]
                          │                 │
                          v                 v
                    TIMELINE_BUILD    AI_GENERATION
                          │                 │
                          │          [ASSETS_GENERATED]
                          │                 │
                          └────────┬────────┘
                                   │
                          [TIMELINE_BUILT]
                                   │
                                   v
                              PRODUCTION
                                   │
                            [DRAFT_COMPLETE]
                                   │
                                   v
                                 QA_REVIEW
                                   │
                          ┌────────┴────────┐
                          │                 │
                    [SCORE ≥90]      [SCORE <90]
                          │                 │
                          v                 v
                   CONTINUITY_CHECK   RE_EDIT (attempt 1)
                          │                 │
                          │          [RETRY_QA_REVIEW]
                          │                 │
                          │          ┌──────┴──────┐
                          │          │ [3 attempts │
                          │          │  exhausted?]
                          │          │             │
                          │     YES  │             NO
                          │          v             v
                          │      STOPPED(E004)  RE_EDIT (next)
                          │          │
                          │    return report
                          │
                   [FLOW ≥92]
                          │
                          v
                   AUDIENCE_SIMULATION
                          │
                   ┌──────┴──────┐
                   │             │
             [SAT ≥92]      [SAT <92]
                   │             │
                   v             v
            FINAL_APPROVAL  RE_EDIT (attempt)
                   │
          ┌────────┴────────┐
          │                 │
      [APPROVED]        [REJECTED]
          │                 │
          v                 v
      EXPORT            STOPPED (E005)
          │                 │
    final.mp4          return report
```

### State Transitions

| From | To | Condition | Error |
|------|----|-----------|----|
| INIT | RESEARCH | START_PRODUCTION | - |
| RESEARCH | FACT_CHECK | FACTS_EXTRACTED | - |
| FACT_CHECK | SCRIPT_ANALYSIS | confidence ≥ 95% | E002 (unsupported) |
| SCRIPT_ANALYSIS | VISUAL_ALIGNMENT | scene_breakdown complete | - |
| VISUAL_ALIGNMENT | VISUAL_PLANNING | score ≥ 90 | E003 (low teaching) |
| VISUAL_PLANNING | ASSET_SEARCH | visuals assigned | - |
| ASSET_SEARCH | TIMELINE_BUILD | coverage ≥ 90% | E001 (insufficient) |
| ASSET_SEARCH | AI_GENERATION | coverage < 90% | - |
| AI_GENERATION | TIMELINE_BUILD | assets generated | - |
| TIMELINE_BUILD | PRODUCTION | timeline complete | - |
| PRODUCTION | QA_REVIEW | draft.mp4 created | - |
| QA_REVIEW | CONTINUITY_CHECK | score ≥ 90 | E004 (low quality) |
| QA_REVIEW | RE_EDIT | score < 90 | - |
| CONTINUITY_CHECK | AUDIENCE_SIM | flow ≥ 92 | E005 (low flow) |
| CONTINUITY_CHECK | RE_EDIT | flow < 92 | - |
| AUDIENCE_SIM | FINAL_APPROVAL | satisfaction ≥ 92 | E006 (low engage) |
| AUDIENCE_SIM | RE_EDIT | satisfaction < 92 | - |
| FINAL_APPROVAL | EXPORT | APPROVED | - |
| FINAL_APPROVAL | STOPPED | REJECTED | E007 (not ready) |
| RE_EDIT | QA_REVIEW | attempt ≤ 3 | - |
| RE_EDIT | STOPPED | attempt > 3 | E008 (max retries) |
| EXPORT | END | final.mp4 exported | - |

---

## ERROR CODE TAXONOMY

### Error Categories

```
E001 - INSUFFICIENT_VISUAL_COVERAGE
  Severity: CRITICAL
  Cause: Asset Finder cannot locate ≥90% of required visuals
  Recovery: Trigger AI_GENERATOR, retry asset search
  Action: STOP if still <90% after AI generation

E002 - UNSUPPORTED_CLAIM
  Severity: CRITICAL
  Cause: Fact Checker cannot verify claim to ≥95% confidence
  Recovery: Remove claim from script or provide source
  Action: STOP production until resolved

E003 - LOW_VISUAL_TEACHING_SCORE
  Severity: CRITICAL
  Cause: Visual Alignment Agent scores visual <90 on teaching
  Recovery: Return to Visual Planner with specific feedback
  Action: STOP until all visuals score ≥90

E004 - LOW_QA_SCORE
  Severity: CRITICAL
  Cause: QA Reviewer scores documentary <90 overall
  Recovery: Re-Edit Agent repairs identified scenes
  Action: Retry up to 3 times, STOP if still <90

E005 - LOW_STORY_FLOW
  Severity: CRITICAL
  Cause: Continuity Agent scores flow <92
  Recovery: Re-Edit Agent improves narrative progression
  Action: Return to creative layer, retry

E006 - LOW_AUDIENCE_SATISFACTION
  Severity: CRITICAL
  Cause: Audience Simulation scores satisfaction <92
  Recovery: Re-Edit Agent improves engagement
  Action: Retry up to 3 times, STOP if still <92

E007 - NOT_BROADCAST_READY
  Severity: CRITICAL
  Cause: Final Approval Agent rejects documentary
  Recovery: None - production ends
  Action: Return engineering report with specific failures

E008 - MAX_RETRIES_EXCEEDED
  Severity: CRITICAL
  Cause: Re-Edit Agent exhausted 3 attempts
  Recovery: None - escalate to Producer for manual review
  Action: STOP production, return status report

E009 - TIMEOUT_EXCEEDED
  Severity: CRITICAL
  Cause: Agent execution time exceeded max threshold
  Recovery: Retry with extended timeout or STOP
  Action: Log timeout, retry once, then STOP

E010 - INVALID_INPUT_SCHEMA
  Severity: CRITICAL
  Cause: Message from upstream agent doesn't match schema
  Recovery: None - upstream agent failed
  Action: STOP, return schema validation error

E011 - INVALID_OUTPUT_SCHEMA
  Severity: CRITICAL
  Cause: Agent output doesn't match declared schema
  Recovery: Agent re-execution with debugging
  Action: Retry once, then STOP and escalate

E012 - MISSING_REQUIRED_FIELD
  Severity: CRITICAL
  Cause: Output JSON missing required field
  Recovery: Agent re-execution
  Action: Retry once, then STOP

E013 - THRESHOLD_NOT_MET
  Severity: CRITICAL
  Cause: Confidence score below minimum threshold
  Recovery: Depends on agent - retry or escalate
  Action: Defined per-agent retry policy

E014 - ASSET_NOT_FOUND
  Severity: WARNING
  Cause: Specific visual asset cannot be sourced
  Recovery: Substitute with fallback asset or AI generate
  Action: Log as coverage gap, try fallback

E015 - SYNC_DRIFT_EXCEEDED
  Severity: CRITICAL
  Cause: Caption/visual sync drift >0.1 seconds
  Recovery: Timeline Builder re-syncs
  Action: Retry timeline sync, escalate if persistent

E016 - PLACEHOLDER_DETECTED
  Severity: CRITICAL
  Cause: Final Approval finds placeholder frame
  Recovery: None - production failed
  Action: Return REJECTED with timestamp

E017 - GENERIC_VISUAL_DETECTED
  Severity: CRITICAL
  Cause: Visual Alignment or Final Approval detects generic footage
  Recovery: Visual Planner substitutes with specific asset
  Action: Return to creative layer
```

---

## RETRY POLICY SPECIFICATION

### Standard Retry Policy (All Agents)

```json
{
  "retry_policy": {
    "max_attempts": 3,
    "backoff_strategy": "exponential",
    "backoff_base_seconds": 5,
    "retry_on_errors": [
      "TIMEOUT_EXCEEDED",
      "TRANSIENT_API_ERROR",
      "RESOURCE_UNAVAILABLE"
    ],
    "no_retry_on_errors": [
      "UNSUPPORTED_CLAIM",
      "INVALID_INPUT_SCHEMA",
      "PLACEHOLDER_DETECTED"
    ]
  },
  "backoff_schedule": {
    "attempt_1": {
      "delay_seconds": 0,
      "description": "Immediate execution"
    },
    "attempt_2": {
      "delay_seconds": 5,
      "description": "Wait 5 seconds (5 * 2^0)"
    },
    "attempt_3": {
      "delay_seconds": 10,
      "description": "Wait 10 seconds (5 * 2^1)"
    },
    "attempt_4": {
      "delay_seconds": 20,
      "description": "Max attempts exceeded, escalate"
    }
  },
  "escalation": {
    "condition": "All retries exhausted",
    "action": "Return to Producer with error details",
    "timeout_production": true
  }
}
```

### Agent-Specific Retry Policies

**Research Agent:**
```
Max attempts: 3
Retry on: API timeouts, transient errors
No retry on: Invalid script, missing entities
Backoff: 5s, 10s
```

**Fact Checker:**
```
Max attempts: 3
Retry on: Search API failures, timeouts
No retry on: Unsupported claim (E002 - no retry, escalate)
Backoff: 5s, 10s
```

**Asset Finder:**
```
Max attempts: 2 (then AI Generation fallback)
Retry on: API timeouts, rate limits
No retry on: Coverage <90% (proceed to AI Gen)
Backoff: 10s, 20s
```

**Timeline Builder:**
```
Max attempts: 2
Retry on: Sync calculation errors, timeouts
No retry on: Invalid input (return to upstream)
Backoff: 5s, 10s
```

**QA Reviewer:**
```
Max attempts: 1 (failures trigger Re-Edit, not retry)
Retry on: Calculation errors only
No retry on: Low scores (escalate to Re-Edit)
Backoff: N/A
```

---

## AGENT INTERFACE SPECIFICATION

### Universal Agent Contract

Every agent MUST implement this interface:

```json
{
  "agent": {
    "metadata": {
      "name": "string (unique identifier)",
      "version": "string (semver)",
      "description": "string",
      "owner": "string (team)",
      "created": "ISO 8601 timestamp",
      "last_updated": "ISO 8601 timestamp"
    },
    "input": {
      "schema": "JSON Schema object",
      "required_fields": ["field1", "field2"],
      "validation_rules": [
        {
          "field": "string",
          "rule": "string",
          "error_code": "string"
        }
      ]
    },
    "output": {
      "schema": "JSON Schema object",
      "required_fields": ["field1", "field2"],
      "success_criteria": [
        {
          "metric": "string",
          "threshold": "number or string",
          "error_code": "string (if not met)"
        }
      ]
    },
    "execution": {
      "timeout_seconds": 300,
      "max_retries": 3,
      "retry_policy": "object",
      "retry_errors": ["E009", "E013"],
      "no_retry_errors": ["E002", "E010"]
    },
    "logging": {
      "format": "JSONL",
      "log_fields": ["timestamp", "agent_name", "action", "status", "duration_ms", "cost_usd"],
      "error_logging": true,
      "audit_logging": true
    },
    "confidence": {
      "required_minimum": 0.95,
      "scoring_dimension": "string",
      "below_threshold_action": "string"
    },
    "dependencies": {
      "upstream_agents": ["array of agent names"],
      "external_apis": ["array of API names"],
      "files": ["array of required files"]
    }
  }
}
```

### Agent Specification Template

```json
{
  "agent_name": "Example Agent",
  "version": "1.0",
  "phase": "1-15",
  "description": "What this agent does",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "scene_id": {"type": "string"},
        "narration": {"type": "string"},
        "entities": {"type": "array", "items": {"type": "string"}}
      },
      "required": ["scene_id", "narration"]
    },
    "validation": [
      {"field": "scene_id", "rule": "non-empty string", "error": "E010"},
      {"field": "narration", "rule": "length > 10 chars", "error": "E010"}
    ]
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "agent_name": {"type": "string"},
        "status": {"enum": ["PASS", "FAIL"]},
        "score": {"type": "number", "minimum": 0, "maximum": 100},
        "data": {"type": "object"},
        "errors": {"type": "array"}
      },
      "required": ["agent_name", "status", "score"]
    },
    "success_criteria": [
      {"metric": "score", "threshold": 90, "error": "E004"},
      {"metric": "status", "threshold": "PASS", "error": "E004"}
    ]
  },
  "execution": {
    "timeout_seconds": 300,
    "max_retries": 3,
    "retry_errors": ["E009", "E013"],
    "no_retry_errors": ["E002", "E010"]
  },
  "logging": {
    "format": "JSONL",
    "fields": [
      "timestamp",
      "agent_name",
      "action_type",
      "status",
      "duration_ms",
      "score",
      "confidence",
      "cost_usd",
      "error_code",
      "metadata"
    ]
  },
  "confidence": {
    "minimum": 0.95,
    "dimension": "score",
    "below_threshold": "escalate"
  }
}
```

### Individual Agent Specifications

#### 1. RESEARCH AGENT

```json
{
  "name": "Research Agent",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "script": {"type": "string"},
        "scene_ids": {"type": "array", "items": {"type": "string"}}
      },
      "required": ["script", "scene_ids"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "facts": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "fact_id": {"type": "string"},
              "claim": {"type": "string"},
              "entities": {"type": "array"},
              "people": {"type": "array"},
              "places": {"type": "array"},
              "dates": {"type": "array"},
              "organizations": {"type": "array"},
              "statistics": {"type": "array"},
              "context": {"type": "string"}
            }
          }
        }
      },
      "required": ["facts"]
    },
    "success_criteria": [
      {"metric": "fact_count", "threshold": ">0", "error": "E010"}
    ]
  },
  "execution": {
    "timeout_seconds": 600,
    "max_retries": 2,
    "retry_errors": ["E009"]
  }
}
```

#### 2. FACT CHECKER

```json
{
  "name": "Fact Checker",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "facts": {"type": "array"},
        "sources": {"type": "array"}
      },
      "required": ["facts"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "verified_facts": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "fact_id": {"type": "string"},
              "status": {"enum": ["VERIFIED", "UNVERIFIED", "PARTIAL"]},
              "confidence": {"type": "number", "minimum": 0, "maximum": 1},
              "source": {"type": "string"},
              "source_url": {"type": "string"}
            }
          }
        },
        "unverified": {"type": "array"},
        "confidence_average": {"type": "number"}
      },
      "required": ["verified_facts", "confidence_average"]
    },
    "success_criteria": [
      {"metric": "confidence_average", "threshold": 0.95, "error": "E002"}
    ]
  },
  "execution": {
    "timeout_seconds": 600,
    "max_retries": 2,
    "no_retry_errors": ["E002"]
  },
  "confidence": {
    "minimum": 0.95,
    "dimension": "confidence_average",
    "below_threshold": "STOP_PRODUCTION"
  }
}
```

#### 3. SCRIPT ANALYZER

```json
{
  "name": "Script Analyzer",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "script": {"type": "string"},
        "verified_facts": {"type": "array"}
      },
      "required": ["script"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "scenes": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "scene_id": {"type": "string"},
              "start_time": {"type": "number"},
              "end_time": {"type": "number"},
              "narration": {"type": "string"},
              "emotion": {"type": "string"},
              "importance": {"enum": ["critical", "major", "minor"]},
              "entities": {"type": "array"},
              "location": {"type": "string"},
              "date": {"type": "string"},
              "visual_requirements": {"type": "array"}
            }
          }
        }
      },
      "required": ["scenes"]
    },
    "success_criteria": [
      {"metric": "scene_count", "threshold": ">0", "error": "E010"},
      {"metric": "coverage", "threshold": 1.0, "error": "E010"}
    ]
  }
}
```

#### 4. VISUAL ALIGNMENT AGENT

```json
{
  "name": "Visual Alignment Agent",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "scenes": {"type": "array"},
        "visual_plan": {"type": "array"}
      },
      "required": ["scenes", "visual_plan"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "aligned_scenes": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "scene_id": {"type": "string"},
              "visual_teaching_score": {"type": "number", "minimum": 0, "maximum": 100},
              "primary_visual": {"type": "string"},
              "secondary_visual": {"type": "string"},
              "fallback_visual": {"type": "string"},
              "purpose": {"type": "string"},
              "status": {"enum": ["PASS", "FAIL"]}
            }
          }
        },
        "overall_teaching_score": {"type": "number"}
      },
      "required": ["aligned_scenes", "overall_teaching_score"]
    },
    "success_criteria": [
      {"metric": "overall_teaching_score", "threshold": 90, "error": "E003"}
    ]
  },
  "confidence": {
    "minimum": 0.90,
    "dimension": "overall_teaching_score",
    "below_threshold": "RETURN_TO_VISUAL_PLANNER"
  }
}
```

#### 5. VISUAL PLANNER

```json
{
  "name": "Visual Planner",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "scenes": {"type": "array"}
      },
      "required": ["scenes"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "visual_plan": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "scene_id": {"type": "string"},
              "primary_visual": {"type": "string"},
              "secondary_visual": {"type": "string"},
              "fallback_visual": {"type": "string"},
              "duration_seconds": {"type": "number"},
              "camera_direction": {"type": "string"},
              "transition": {"type": "string"},
              "purpose": {"type": "string"}
            }
          }
        }
      },
      "required": ["visual_plan"]
    }
  }
}
```

#### 6. ASSET FINDER

```json
{
  "name": "Asset Finder",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "visual_plan": {"type": "array"},
        "sources": {"type": "array"}
      },
      "required": ["visual_plan"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "assets": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "asset_id": {"type": "string"},
              "visual_id": {"type": "string"},
              "source": {"type": "string"},
              "url": {"type": "string"},
              "resolution": {"type": "string"},
              "quality_score": {"type": "number", "minimum": 0, "maximum": 100},
              "license": {"type": "string"},
              "status": {"enum": ["AVAILABLE", "UNAVAILABLE"]}
            }
          }
        },
        "coverage_percentage": {"type": "number"},
        "missing_visuals": {"type": "array"}
      },
      "required": ["assets", "coverage_percentage"]
    },
    "success_criteria": [
      {"metric": "coverage_percentage", "threshold": 0.90, "error": "E001"}
    ]
  },
  "confidence": {
    "minimum": 0.90,
    "dimension": "coverage_percentage",
    "below_threshold": "ACTIVATE_AI_GENERATOR"
  }
}
```

#### 7. TIMELINE BUILDER

```json
{
  "name": "Timeline Builder",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "scenes": {"type": "array"},
        "assets": {"type": "array"},
        "narration_duration": {"type": "number"}
      },
      "required": ["scenes", "assets"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "timeline": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "shot_id": {"type": "string"},
              "scene_id": {"type": "string"},
              "start_time": {"type": "number"},
              "end_time": {"type": "number"},
              "duration": {"type": "number"},
              "asset_id": {"type": "string"},
              "transition": {"type": "string"},
              "caption_sync": {"type": "number"}
            }
          }
        },
        "total_duration": {"type": "number"},
        "sync_accuracy": {"type": "number"}
      },
      "required": ["timeline", "total_duration"]
    },
    "success_criteria": [
      {"metric": "sync_accuracy", "threshold": 0.99, "error": "E015"}
    ]
  }
}
```

#### 8. EDITOR

```json
{
  "name": "Editor",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "timeline": {"type": "array"},
        "assets": {"type": "array"},
        "music": {"type": "string"},
        "color_grade": {"type": "object"}
      },
      "required": ["timeline", "assets"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "video_file": {"type": "string"},
        "file_size_mb": {"type": "number"},
        "duration_seconds": {"type": "number"},
        "resolution": {"type": "string"},
        "codec": {"type": "string"},
        "status": {"enum": ["READY", "FAILED"]}
      },
      "required": ["video_file", "status"]
    },
    "success_criteria": [
      {"metric": "status", "threshold": "READY", "error": "E004"}
    ]
  }
}
```

#### 9. QA REVIEWER

```json
{
  "name": "QA Reviewer",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "video_file": {"type": "string"},
        "timeline": {"type": "array"},
        "verified_facts": {"type": "array"}
      },
      "required": ["video_file"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "visual_relevance": {"type": "number"},
        "narration_sync": {"type": "number"},
        "editing_quality": {"type": "number"},
        "historical_accuracy": {"type": "number"},
        "overall_score": {"type": "number"},
        "issues": {"type": "array"},
        "status": {"enum": ["PASS", "FAIL"]}
      },
      "required": ["overall_score", "status"]
    },
    "success_criteria": [
      {"metric": "overall_score", "threshold": 90, "error": "E004"}
    ]
  },
  "confidence": {
    "minimum": 0.90,
    "dimension": "overall_score",
    "below_threshold": "TRIGGER_RE_EDIT"
  }
}
```

#### 10. CONTINUITY AGENT

```json
{
  "name": "Continuity & Story Flow Agent",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "video_file": {"type": "string"},
        "timeline": {"type": "array"}
      },
      "required": ["video_file"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "story_flow": {"type": "number"},
        "visual_consistency": {"type": "number"},
        "transition_quality": {"type": "number"},
        "educational_value": {"type": "number"},
        "overall_score": {"type": "number"},
        "issues": {"type": "array"},
        "status": {"enum": ["PASS", "FAIL"]}
      },
      "required": ["overall_score", "status"]
    },
    "success_criteria": [
      {"metric": "overall_score", "threshold": 92, "error": "E005"}
    ]
  }
}
```

#### 11. AUDIENCE SIMULATION AGENT

```json
{
  "name": "Audience Simulation Agent",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "video_file": {"type": "string"}
      },
      "required": ["video_file"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "hook_strength": {"type": "number"},
        "clarity": {"type": "number"},
        "engagement": {"type": "number"},
        "educational_value": {"type": "number"},
        "overall_satisfaction": {"type": "number"},
        "predicted_dropoffs": {"type": "array"},
        "status": {"enum": ["PASS", "FAIL"]}
      },
      "required": ["overall_satisfaction", "status"]
    },
    "success_criteria": [
      {"metric": "overall_satisfaction", "threshold": 92, "error": "E006"}
    ]
  }
}
```

#### 12. RE-EDIT AGENT

```json
{
  "name": "Re-Edit Agent",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "failed_report": {"type": "object"},
        "attempt_number": {"type": "integer"},
        "previous_video": {"type": "string"}
      },
      "required": ["failed_report", "attempt_number"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "updated_video": {"type": "string"},
        "fixes_applied": {"type": "array"},
        "status": {"enum": ["RETRY_QA", "STOP"]}
      },
      "required": ["updated_video", "status"]
    }
  },
  "execution": {
    "max_retries": 3,
    "no_retry_errors": ["E008"]
  }
}
```

#### 13. FINAL APPROVAL AGENT

```json
{
  "name": "Final Approval Agent",
  "version": "1.0",
  "input": {
    "schema": {
      "type": "object",
      "properties": {
        "video_file": {"type": "string"},
        "all_reports": {"type": "object"}
      },
      "required": ["video_file", "all_reports"]
    }
  },
  "output": {
    "schema": {
      "type": "object",
      "properties": {
        "status": {"enum": ["APPROVED", "REJECTED"]},
        "reason": {"type": "string"},
        "failures": {"type": "array"},
        "certification": {"type": "string"}
      },
      "required": ["status", "reason"]
    },
    "success_criteria": [
      {"metric": "status", "threshold": "APPROVED", "error": "E007"}
    ]
  }
}
```

---

## ACCEPTANCE TESTS

### Universal Acceptance Test Template

```python
def test_agent_output_schema(agent_name, output):
    """Verify output matches declared schema"""
    schema = get_agent_schema(agent_name)
    assert jsonschema.validate(output, schema)
    
def test_agent_success_criteria(agent_name, output):
    """Verify output meets success criteria"""
    criteria = get_success_criteria(agent_name)
    for criterion in criteria:
        assert output[criterion['metric']] >= criterion['threshold']
        
def test_agent_required_fields(agent_name, output):
    """Verify all required fields present"""
    schema = get_agent_schema(agent_name)
    for field in schema['required']:
        assert field in output
        assert output[field] is not None
        
def test_agent_timeout(agent_name, timeout_seconds):
    """Verify agent execution completes within timeout"""
    start = time.time()
    result = execute_agent(agent_name)
    duration = time.time() - start
    assert duration <= timeout_seconds
```

### Agent-Specific Acceptance Tests

**Research Agent:**
```python
def test_research_agent_output():
    """Acceptance test for Research Agent"""
    input_data = {
        "script": "The Dangote Refinery processes 650,000 barrels per day.",
        "scene_ids": ["s1"]
    }
    output = research_agent.execute(input_data)
    
    # Schema validation
    assert "facts" in output
    assert len(output["facts"]) > 0
    
    # Content validation
    for fact in output["facts"]:
        assert "fact_id" in fact
        assert "claim" in fact
        assert len(fact["claim"]) > 0
        
    # Success criteria
    assert len(output["facts"]) >= 1
    assert output["facts"][0]["claim"] is not None
```

**Fact Checker:**
```python
def test_fact_checker_output():
    """Acceptance test for Fact Checker"""
    input_data = {
        "facts": [{
            "fact_id": "f1",
            "claim": "Nigeria's oil reserves are 37 billion barrels"
        }]
    }
    output = fact_checker.execute(input_data)
    
    # Schema validation
    assert "verified_facts" in output
    assert "confidence_average" in output
    
    # Confidence threshold
    assert output["confidence_average"] >= 0.95 or E002_raised()
    
    # Output structure
    for fact in output["verified_facts"]:
        assert "status" in fact
        assert "confidence" in fact
        assert 0 <= fact["confidence"] <= 1
```

**Asset Finder:**
```python
def test_asset_finder_coverage():
    """Acceptance test for Asset Finder"""
    input_data = {
        "visual_plan": [
            {"visual_id": "v1", "type": "refinery_aerial"},
            {"visual_id": "v2", "type": "port_ships"}
        ]
    }
    output = asset_finder.execute(input_data)
    
    # Schema validation
    assert "assets" in output
    assert "coverage_percentage" in output
    
    # Coverage requirement
    assert output["coverage_percentage"] >= 0.90 or E001_raised()
    
    # Asset quality
    for asset in output["assets"]:
        assert "quality_score" in asset
        assert asset["quality_score"] > 0
```

**QA Reviewer:**
```python
def test_qa_reviewer_scores():
    """Acceptance test for QA Reviewer"""
    output = qa_reviewer.execute({"video_file": "draft.mp4"})
    
    # Required metrics
    required_metrics = [
        "visual_relevance",
        "narration_sync",
        "editing_quality",
        "historical_accuracy",
        "overall_score"
    ]
    
    for metric in required_metrics:
        assert metric in output
        assert 0 <= output[metric] <= 100
    
    # Quality threshold
    assert output["overall_score"] >= 90 or TRIGGER_RE_EDIT()
```

**Final Approval:**
```python
def test_final_approval_decision():
    """Acceptance test for Final Approval Agent"""
    output = final_approval.execute({"video_file": "draft.mp4"})
    
    # Decision required
    assert output["status"] in ["APPROVED", "REJECTED"]
    
    # Reasoning required
    if output["status"] == "REJECTED":
        assert "failures" in output
        assert len(output["failures"]) > 0
    
    # Certification
    if output["status"] == "APPROVED":
        assert "certification" in output
```

---

## MESSAGE FORMATS

### Standard Message Envelope

```json
{
  "message": {
    "id": "uuid",
    "timestamp": "ISO 8601",
    "from_agent": "string",
    "to_agent": "string",
    "message_type": "string (EXECUTE, RESULT, ERROR, RETRY)",
    "payload": {},
    "metadata": {
      "attempt": "number",
      "retry_backoff": "number",
      "correlation_id": "uuid"
    }
  }
}
```

### Execute Message

```json
{
  "message_type": "EXECUTE",
  "from_agent": "Producer",
  "to_agent": "Research Agent",
  "payload": {
    "script": "...",
    "scene_ids": ["..."]
  },
  "metadata": {
    "attempt": 1,
    "timeout_seconds": 600
  }
}
```

### Result Message

```json
{
  "message_type": "RESULT",
  "from_agent": "Research Agent",
  "to_agent": "Producer",
  "payload": {
    "status": "PASS",
    "facts": [...],
    "duration_ms": 1234,
    "cost_usd": 0.05
  },
  "metadata": {
    "attempt": 1,
    "execution_time_ms": 1234
  }
}
```

### Error Message

```json
{
  "message_type": "ERROR",
  "from_agent": "Research Agent",
  "to_agent": "Producer",
  "payload": {
    "error_code": "E009",
    "error_message": "Timeout exceeded",
    "severity": "CRITICAL",
    "recovery_action": "RETRY"
  },
  "metadata": {
    "attempt": 1,
    "retry_eligible": true
  }
}
```

---

## REFERENCE IMPLEMENTATION

### Producer Orchestration Pseudocode

```python
class Producer:
    def __init__(self):
        self.agents = {}
        self.state = "INIT"
        self.attempt_count = {}
        self.max_retries = 3
        
    def execute_production(self, project_plan):
        """Execute full production workflow"""
        
        self.state = "RESEARCH"
        facts = self.execute_agent(
            agent="Research",
            input={"script": project_plan["script"]},
            timeout=600
        )
        
        self.state = "FACT_CHECK"
        verified = self.execute_agent(
            agent="Fact Checker",
            input={"facts": facts},
            gate=lambda x: x["confidence_average"] >= 0.95
        )
        
        if not verified:
            return self.halt_production("E002: Unsupported claims")
        
        # Continue through pipeline...
        
    def execute_agent(self, agent, input, timeout, gate=None):
        """Execute agent with retry and validation"""
        
        for attempt in range(1, self.max_retries + 1):
            try:
                result = agent.execute(input, timeout=timeout)
                
                # Validate output schema
                if not self.validate_schema(agent, result):
                    raise SchemaError(f"Invalid output schema for {agent}")
                
                # Check gate criteria
                if gate and not gate(result):
                    return None
                
                return result
                
            except TimeoutError:
                if attempt < self.max_retries:
                    backoff = 5 * (2 ** (attempt - 1))
                    time.sleep(backoff)
                    continue
                else:
                    raise
                    
            except Exception as e:
                if self.should_retry(e):
                    continue
                else:
                    raise
                    
    def halt_production(self, error_message):
        """Stop production and return engineering report"""
        return {
            "status": "FAILED",
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }
```

### Agent Execution Template

```python
class Agent:
    def __init__(self, name, schema_input, schema_output, success_criteria):
        self.name = name
        self.schema_input = schema_input
        self.schema_output = schema_output
        self.success_criteria = success_criteria
        
    def execute(self, input_data, timeout=300):
        """Execute agent with validation"""
        
        # Validate input
        self.validate_input(input_data)
        
        # Execute
        start_time = time.time()
        try:
            result = self.run(input_data)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_error(e, duration_ms)
            raise
            
        duration_ms = (time.time() - start_time) * 1000
        
        # Validate output
        self.validate_output(result)
        
        # Check success criteria
        for criterion in self.success_criteria:
            if result[criterion["metric"]] < criterion["threshold"]:
                raise CriterionNotMet(criterion["error_code"])
        
        # Log
        self.log_result(result, duration_ms)
        
        return result
        
    def validate_input(self, data):
        """Validate input against schema"""
        try:
            jsonschema.validate(data, self.schema_input)
        except jsonschema.ValidationError as e:
            raise InvalidInputSchema(f"E010: {str(e)}")
            
    def validate_output(self, data):
        """Validate output against schema"""
        try:
            jsonschema.validate(data, self.schema_output)
        except jsonschema.ValidationError as e:
            raise InvalidOutputSchema(f"E011: {str(e)}")
```

---

## VERSIONING AND CHANGELOG

### Specification Versioning

```
ENGINEERING_SPECIFICATION_v1.0
├── SECTION: System Architecture
│   └── UNCHANGED from v0.9
├── SECTION: Agent Communication
│   └── UPDATED: Added error handling flows
├── SECTION: Error Taxonomy
│   └── ADDED: 17 error codes with recovery
└── SECTION: Acceptance Tests
    └── ADDED: Reference implementation
```

### Prompt Versioning

Every agent prompt has version attached:

```
research_agent_v1.0.txt
research_agent_v1.1.txt (improved claim extraction)
research_agent_v1.2.txt (added confidence scoring)
```

### Changelog

```
## v1.0 (2026-07-30) - Initial Release
- 15-agent architecture
- 6 quality gates
- 17 error codes
- Formal JSON schemas
- Retry policies
- Acceptance tests

## Planned: v1.1
- Multi-language support
- Parallel agent execution
- WebSocket communication
- Real-time dashboards
```

---

## CONCLUSION

This specification defines a professional, production-grade documentary studio where:

✅ **Every agent has contracts** (input/output schemas)  
✅ **Every output is validated** (success criteria)  
✅ **Every failure has codes** (error taxonomy)  
✅ **Every retry is managed** (exponential backoff)  
✅ **Every decision is logged** (JSONL audit trail)  
✅ **Every gate is enforced** (6 quality gates)  
✅ **Every system is tested** (acceptance tests)  

This transforms documentary production from **prompt engineering** to **systems engineering**.

---

**End of Engineering Specification v1.0**
