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

### Step 7: Master Retaliation Penalty in Attack Evaluator
**Files:** `attack_evaluator.py`, `attack_decider.py`

When the attacking cell is the AI's master and the target is NOT the enemy master, apply a penalty (~-40). Prevents casual master attacks that lose HP.

---

## Current Progress

- [x] Step 1: ScoredAction + unified brain
- [x] Step 2: Weight recalibration
- [ ] Step 3: current_turn in BoardEvaluation
- [ ] Step 4: Per-spell turn-awareness
- [ ] Step 5: Mana bubble bonus
- [ ] Step 6: Archer creation awareness
- [ ] Step 7: Master retaliation penalty
