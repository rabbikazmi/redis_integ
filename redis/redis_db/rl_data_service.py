"""
FILE: data/services/rl_data_service.py
ROLE: The "Math Tutor" (RLDataService).

DESCRIPTION:
This service is the expert in Reinforcement Learning (RL) data. While the 
databases just store numbers, this file knows what those numbers MEAN.

It handles the 'Brain' data (Q-Values) and provides the mathematical functions 
needed for the AI to make decisions, such as:
1. "What is the best possible score I can get in this situation?"
2. "Which action should I take to get the most points?"
3. "Dump the whole brain into a format that can be saved to a file."
"""

from typing import Dict, List, Any
import numpy as np 
from data.api.reddis_api_db import BaseDB   # We use the BaseDB interface so this service can work with ANY database type (Memory, JSON, Redis, etc.)

class RLDataService:
    """
    A specialized service for managing AI learning data.
    """
    def __init__(self, db: BaseDB):
        # We give the service a database (like Memory or JSON) to store its numbers in.
        self.db = db
        # Initial setup: check if we've ever run before.
        if not self.db.exists("q_table_initialized"):
            self.db.set("q_table_initialized", True)

    def _get_q_key(self, state: int, action: int) -> str:
        """INTERNAL: Generates a unique label for a specific situation and action."""
        return f"q_val:{state}:{action}"

    def get_q_value(self, state: int, action: int) -> float:
        """READ: Finds the 'Score' for a specific action in a specific situation."""
        val = self.db.get(self._get_q_key(state, action))
        # If the AI has never seen this situation before, the score is 0.0.
        return float(val) if val is not None else 0.0

    def set_q_value(self, state: int, action: int, value: float) -> bool:
        """WRITE: Updates the 'Score' after the AI learns something new."""
        return self.db.set(self._get_q_key(state, action), value)

    def get_max_q_value(self, state: int, available_actions: List[int]) -> float:
        """
        LOOK AHEAD: Finds the HIGHEST possible score available in a given situation.
        This is used to help the AI realize: "If I move here, what's the best I can do next?"
        """
        if not available_actions:
            return 0.0
            
        max_val = float('-inf')
        for action in available_actions:
            val = self.get_q_value(state, action)
            if val > max_val:
                max_val = val
                
        return max_val if max_val != float('-inf') else 0.0

    def get_best_action(self, state: int, available_actions: List[int]) -> int:
        """
        DECIDE: Picks the action with the absolute highest score.
        This is the command used when the unit is 'playing for real' (Exploitation).
        """
        if not available_actions:
            raise ValueError("Cannot select action from empty list.")
            
        best_action = available_actions[0]
        max_val = self.get_q_value(state, best_action)
        
        for action in available_actions[1:]:
            val = self.get_q_value(state, action)
            if val > max_val:
                max_val = val
                best_action = action
                
        return best_action
        
    def get_all_q_values(self, state: int, available_actions: List[int]) -> Dict[int, float]:
        """UI DISPLAY: Returns a list of all scores so the human user can see what the AI is 'thinking'."""
        return {action: self.get_q_value(state, action) for action in available_actions}

    def dump_active_table(self, state_size: int, action_size: int) -> np.ndarray:
        """
        EXPORT: Converts the entire brain database into a giant grid of numbers (a Numpy Table).
        This is perfect for saving the brain to a file.
        """
        table = np.zeros((state_size, action_size))
        
        for s in range(state_size):
            for a in range(action_size):
                table[s, a] = self.get_q_value(s, a)
                
        return table

    def load_active_table(self, table: np.ndarray) -> None:
        """
        IMPORT: Takes a grid of numbers from a file and pours it into the active database memory.
        """
        rows, cols = table.shape
        for s in range(rows):
            for a in range(cols):
                val = table[s, a]
                if val != 0.0:  # Small optimization: we only bother saving non-zero scores.
                    self.set_q_value(s, a, float(val))
