# AI Implementation Plan


## Table of Contents

- [AI Implementation Plan](#ai-implementation-plan)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Why AI is Important](#why-ai-is-important)
    - [Accessibility](#accessibility)
    - [Technical Benefits](#technical-benefits)
  - [Implementation Approach](#implementation-approach)
    - [Rule-Based AI System](#rule-based-ai-system)
    - [Future Improvements](#future-improvements)
  - [Architecture](#architecture)
    - [File Structure](#file-structure)
  - [AI Decision-Making Flow](#ai-decision-making-flow)
  - [Rule-Based Strategy Logic](#rule-based-strategy-logic)
    - [Priority System (High to Low)](#priority-system-high-to-low)
    - [Evaluation Criteria](#evaluation-criteria)
  - [Current Status \& Roadmap](#current-status--roadmap)
    - [✅ Phase 1: Foundation (COMPLETE)](#-phase-1-foundation-complete)
    - [🔄 Phase 2: Strategy (NEXT)](#-phase-2-strategy-next)
    - [⏳ Phase 3: Polish (FUTURE)](#-phase-3-polish-future)
  - [Technical Decisions](#technical-decisions)
    - [1. No Socket Events for AI](#1-no-socket-events-for-ai)
    - [2. AI Player Lifecycle](#2-ai-player-lifecycle)
    - [3. Session Handling](#3-session-handling)
    - [4. Timing](#4-timing)
  - [Testing Strategy](#testing-strategy)
    - [Unit Tests](#unit-tests)
    - [Integration Tests](#integration-tests)
    - [Manual Testing](#manual-testing)
  - [Success Metrics](#success-metrics)
  - [Notes](#notes)
    - [Why Rule-Based?](#why-rule-based)

---

## Overview

This document outlines the plan to implement an AI opponent for the game. The AI is essential for making the project accessible - requiring two devices/browsers to test multiplayer is a significant barrier. A "Play vs AI" button provides instant, single-player engagement.

**Approach:** Rule-based AI with priority-driven decision making.

---

## Why AI is Important

### Accessibility
- **Instant playability** - One-click game experience without waiting for opponents
- **Testing and development** - Easier to test game mechanics and balance

### Technical Benefits
1. **Demonstrates AI/game design skills** - Decision trees, heuristics, behavior systems
2. **Better validation** - Proves the game engine works correctly
3. **Stress testing** - AI can play thousands of games to find edge cases
4. **Future multiplayer enhancement** - Can fill empty lobbies or provide practice mode

---

## Implementation Approach

### Rule-Based AI System

The AI uses a **priority-based decision system** combined with **board state evaluation**:

- **Priority system** for action selection (attack threats, spawn strategically, advance position)
- **Board evaluator** to analyze game state (cell control, threats, positioning)
- **Heuristics** for targeting and movement decisions
- **Spell usage logic** based on game state and resource management
- **Adjustable difficulty levels** through parameter tuning

This approach balances sophistication with maintainability and provides transparent, explainable decision-making.

### Future Improvements

Potential enhancements to consider after initial implementation:

- **Advanced evaluation** - Minimax or Monte Carlo Tree Search for look-ahead planning
- **Pattern learning** - Basic adaptation to player strategies
- **AI personalities** - Aggressive, defensive, or balanced playstyles
- **Dynamic difficulty** - Adjust based on player performance
- **Replay analysis** - Learn from high-level play patterns

---

## Architecture

### File Structure

```
server/
  ai/
    __init__.py                    # AI constants
    ai_player.py                   # Core AI player class
    strategy/
      __init__.py
      ai_strategy.py               # Main strategy coordinator
      evaluators/
        __init__.py
        board_evaluator.py         # Board state analysis
        cell_evaluator.py          # Individual cell scoring
        spell_evaluator.py         # Spell usage decisions
      decision_makers/
        __init__.py
        attack_decider.py          # Attack target selection
        movement_decider.py        # Movement logic
        spawn_decider.py           # Spawn placement
        spell_decider.py           # Spell timing
    config/
      __init__.py
      ai_config.py                 # Difficulty levels, behavior tuning
```



## AI Decision-Making Flow

```
1. Match starts → AI player detected
2. Turn swaps to AI → TurnWatcherService calls ai_player.take_turn()
3. AIPlayer executes:
   a. board_evaluator.evaluate(match_context) → Get board state
   b. ai_strategy.decide_action() → Choose best action
   c. Execute action via match.handle_cell_selection() etc.
   d. Add small delay for "thinking" (human-like behavior)
4. AI ends turn or runs out of time
5. Turn swaps back to human
```

---

## Rule-Based Strategy Logic

### Priority System (High to Low)

1. **Critical Defense** (Priority 10)
   - Master cell under immediate threat
   - Block or counter-attack

2. **Lethal Attack** (Priority 9)
   - Can kill enemy master this turn
   - Execute immediately

3. **Spell Usage** (Priority 8)
   - Stamina < 3 → restore stamina
   - Good spell opportunity → use appropriate spell

4. **Attack Enemy Cells** (Priority 7)
   - Enemy cells in range
   - Target: weakest or most threatening

5. **Strategic Spawn** (Priority 6)
   - Spawn near front line
   - Protect master cell
   - Control key positions

6. **Advance Position** (Priority 5)
   - Move cells toward enemy territory
   - Maintain formation

7. **End Turn** (Priority 1)
   - No good actions available

### Evaluation Criteria

**Board Evaluator:**
- Cell control count (own vs enemy)
- Distance to enemy master
- Threats to own master
- Clustering opportunities (for AoE spells)
- Positional advantage

**Cell Evaluator:**
- HP difference (prefer low HP targets)
- Strategic value (protecting master?)
- Position value (forward positions more valuable)
- Threat level (can it attack master?)

**Spell Evaluator:**
- Stamina threshold (< 3 = urgent restore)
- Enemy clustering (good for AoE spells)
- Own positioning (good for buff spells)
- Spell availability (remaining uses)

---

## Current Status & Roadmap

### ✅ Phase 1: Foundation (COMPLETE)

**Infrastructure implemented:**
- AI file structure created (`server/ai/`)
- Player model updated with `is_ai` field
- `CLIENT_QUEUE_AI_REGISTER` event added
- Queue system handles AI match creation
- Match handler detects and instantiates AI player
- Client "Play vs AI" button functional
- AI alternates turns automatically
- `BoardEvaluator` fully implemented with comprehensive test coverage
- Board evaluation integrated into AI turn logic

**Current behavior:** AI evaluates board state each turn and logs detailed analysis, then passes turn

### 🔄 Phase 2: Strategy (NEXT)

**Goal:** Intelligent decision-making

**Components to implement:**
- ✅ `BoardEvaluator` - Analyze game state, identify threats/opportunities
- `AttackDecider` - Target selection based on threat level and HP
- `MovementDecider` - Optimal positioning (offense/defense balance)
- `SpawnDecider` - Strategic spawn placement
- Integration with `AIPlayer` to execute actions

**Success criteria:**
- AI makes valid, strategic moves
- AI can win against careless play
- No crashes or infinite loops

### ⏳ Phase 3: Polish (FUTURE)

**Goal:** Production-ready experience

**Enhancements:**
- `SpellDecider` - Strategic spell usage and timing
- Human-like "thinking" delays (300-800ms)
- Difficulty levels (Easy/Medium/Hard)
- UI improvements (difficulty selector, thinking indicator)
- Comprehensive testing and balance tuning

**Success criteria:**
- Natural, human-like behavior
- Appropriate challenge at all difficulty levels
- Stable in production

---

## Technical Decisions

### 1. No Socket Events for AI
- AI directly calls match action methods
- Cleaner, faster, no serialization overhead
- Still respects turn order and validation
- Bypasses client-side event system

### 2. AI Player Lifecycle
- Lives in `MatchHandlerUnit` instance
- Created when match detects AI player
- Destroyed when match ends
- No persistent state between matches

### 3. Session Handling
- AI doesn't need real session
- Uses synthetic session data for logging
- Skip session validation for AI actions

### 4. Timing
- AI actions on background thread (non-blocking)
- Small random delays between actions (human-like)
- Still subject to turn duration limits
- Uses `socketio.sleep()` for cooperative yielding

---

## Testing Strategy

### Unit Tests
**File:** `server/tests/ai_tests/test_board_evaluator.py`
- ✅ BoardEvaluator comprehensive test coverage
- AI completes full match
- AI respects turn order
- AI makes only valid moves
- AI uses spells appropriately
- AI handles edge cases (no valid moves, etc.)

### Integration Tests
- AI vs Human matches
- AI decision quality tests
- Performance tests (decision time < 1s)

### Manual Testing
- Play against each difficulty level
- Verify natural behavior
- Check for exploits

---

## Success Metrics

✅ User clicks "Play vs AI" button  
✅ Match starts immediately (no waiting)  
✅ AI takes turns automatically  
⏳ AI makes legal moves that advance strategy  
⏳ AI can win games against careless play  
✅ No crashes or hangs  
⏳ Works in production deployment  

---

## Notes

### Why Rule-Based?
- **Transparent and debuggable** - Easy to understand and tune behavior
- **No training data required** - Works immediately without ML infrastructure
- **Deterministic** - Consistent, predictable behavior (easier to test)
- **Efficient** - Fast decision-making without expensive computations
- **Maintainable** - Clear logic flow, easy to extend and modify
---
*This document was AI generated*