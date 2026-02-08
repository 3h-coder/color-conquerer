# AI Improvement Plan

## Problem Summary

The current AI decision brain uses a **fixed priority chain** (Movement → Attack → Spell → Spawn). The first decider that returns a non-None result wins, regardless of whether another action type would be far more valuable. This causes:

- Movement stealing priority from better attacks or spells
- Spells like Mine Trap firing on turn 1 (wasteful, no enemies nearby)
- No awareness of game phase (early vs mid vs late)
- No competition between action types (a mediocre move beats a great spell)

---

## Improvement Steps

### Step 1: Unified Scoring via `ScoredAction` ✅
**Files:** `base_decider.py`, `ai_decision_brain.py`

- Create a `ScoredAction(action, score)` dataclass
- Change `_pick_best_action` to return `ScoredAction` (action + its score)
- Change each decider's public method to return `Optional[ScoredAction]`
- Change `AIDecisionBrain._decide_action` to collect all 4 candidates and pick the one with the highest score — instead of the fixed if-chain

### Step 2: Weight Recalibration (0–200 scale) ✅
**Files:** `ai_config.py`

All evaluators must produce scores on a **comparable 0–200 scale** so the unified scoring works:

| Score Range | Meaning |
|---|---|
| 180–200 | Game-ending (lethal on master) |
| 120–170 | Critical (master attack, key defensive spell) |
| 60–100 | Strong (good spell, kill threat near master, mana bubble grab) |
| 30–60 | Solid (regular attack, regular spawn, archery vow) |
| 10–30 | Filler (basic forward movement, low-value mine trap) |

### Step 3: Add `current_turn` to `BoardEvaluation`
**Files:** `board_evaluation.py`, `board_evaluator.py`

Expose `match_context.current_turn` in the evaluation. One new field, zero logic — enables game-phase awareness in all evaluators.

### Step 4: Per-Spell Turn-Awareness
**Files:** Each spell evaluator (5 files, ~3-5 lines each)

| Spell | Turn Logic |
|---|---|
| Mine Trap | Score → near 0 before turn ~5 |
| Celerity | Score → near 0 before turn ~5 |
| Ambush | **No penalty.** Small bonus if turn ≤ 6 (enemies on their side → 3 spawns) |
| Archery Vow | No change (naturally gated by needing isolated cells) |
| Shield Formation | No change (naturally gated by needing 2×2 squares) |

### Step 5: Mana Bubble Bonus in Movement Evaluator
**Files:** `movement_evaluator.py`

Add a significant bonus (~65) when a movement destination is a mana bubble cell. Early game, this makes the AI rush mana bubbles — correct play.

### Step 6: Archer Creation Awareness in Movement Evaluator
**Files:** `movement_evaluator.py`

When Archery Vow is available (count > 0, MP ≥ 3), add a bonus to movements that would leave a neighboring friendly cell isolated (creating an archer target). The iterative action loop naturally chains: move → then cast Archery Vow on the now-isolated cell.

### Step 7: Master Retaliation Penalty in Attack Evaluator ✅
**Files:** `attack_evaluator.py`, `attack_decider.py`, `ai_config.py`

When the attacking cell is the AI's master and the target is NOT the enemy master, apply a penalty (~-40). Prevents casual master attacks that lose HP. The master should only attack when:
- It's targeting the enemy master directly
- OR it's a lethal attack on the enemy master

**Implementation:**
- `attack_decider.py` passes `attacker_coords` to evaluator
- `attack_evaluator.evaluate()` checks if attacker is master, applies `ATTACK_WEIGHT_MASTER_RETALIATION_PENALTY` if attacking non-master

### Step 8: Master Defensive Spawning ✅
**Files:** `spawn_evaluator.py`, `ai_config.py`

When the AI's master health is at critical level (≤ 2 HP), strongly prioritize spawning cells adjacent to the master for protection. This creates a defensive wall and delays lethal attacks.

**Implementation:**
- `spawn_evaluator.py` checks `ai_player.resources.current_hp <= MASTER_CRITICAL_HEALTH_THRESHOLD`
- Applies `SPAWN_WEIGHT_MASTER_DEFENSE_BONUS` to spawns near master when health is critical
- Weight is high (50.0) but slightly lower than mana bubble grab (80.0) - health is important but not as much as resource economy early game

---

## Current Progress

- [x] Step 1: ScoredAction + unified brain
- [x] Step 2: Weight recalibration
- [x] Step 3: current_turn in BoardEvaluation
- [x] Step 4: Per-spell turn-awareness
- [x] Step 5: Mana bubble bonus
- [x] Step 6: Archer creation awareness
- [x] Step 7: Master retaliation penalty
- [x] Step 8: Master defensive spawning
