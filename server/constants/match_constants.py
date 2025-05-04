"""
Numeric values related to match events (such as the turn duration)
that should not be manually configured but set only in the code.
"""

DELAY_IN_S_TO_WAIT_FOR_EVERYONE = 10
DELAY_IN_S_BEFORE_MATCH_EXCLUSION = 30
DELAY_IN_S_BEFORE_MATCH_HANDLER_UNIT_DELETION = 30
TURN_DURATION_IN_S = 60
# ⚠️ Each delay below must be higher than the previous one
INACTIVITY_FIRST_WARNING_DELAY_IN_S = 75
INACTIVITY_FINAL_WARNING_DELAY_IN_S = 90
INACTIVITY_KICK_DELAY_IN_S = 110
