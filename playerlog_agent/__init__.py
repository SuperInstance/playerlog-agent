"""
PLATO PlayerLog Agent — Gaming Session Tracking for playerlog.ai

Tracks gaming sessions, achievements, stats, and player progression.
Every gaming session logged to PLATO as a functional tile.
"""

import time
import requests
from fleet_agent import BaseAgent
from fleet_agent.fleet_math import EmergenceDetector, HolonomyConsensus

from typing import Optional, List, Dict, Any
from dataclasses import dataclass

DEFAULT_PLATO_URL = "http://localhost:8847"
ROOM = "playerlog-ai"

@dataclass
class GameSession:
    """A game session tile."""
    game_name: str
    platform: str
    duration_minutes: int
    session_type: str  # "multiplayer" | "singleplayer" | "co-op"
    result: Optional[str] = None
    score: Optional[int] = None
    achievements: List[str] = None
    
    def __post_init__(self):
        if self.achievements is None:
            self.achievements = []

@dataclass
class Achievement:
    """An unlocked achievement."""
    name: str
    game: str
    unlocked_at: float
    rarity: str = "common"  # "common" | "rare" | "epic" | "legendary"

class PlayerLogAgent:
    """
    Gaming session tracker agent.
    
    Logs game sessions, achievements, stats to PLATO.
    Tracks player progression over time through vessel accumulation.
    """
    
        
    def detect_emergence(self, events: list) -> dict:
        """Detect emergence via H1 cohomology."""
        detector = EmergenceDetector()
        edges = [(events[i], events[i+1]) for i in range(len(events)-1)]
        detector.update(events, edges)
        return {"emergence_detected": detector.emergence_detected, "h1_cohomology": detector.h1, "confidence": detector.confidence}

    def check_consensus(self, tile_ids: list[int]) -> bool:
        """Check holonomy consensus across tiles."""
        hc = HolonomyConsensus()
        for tid in tile_ids:
            hc.add_tile(tid)
        return hc.check_consensus([tile_ids])

def __init__(self, vessel: str = "playerlog-agent", domain: str = PLAYERLOG_AI_ROOM, plato_url: str = "http://localhost:8847"):
        super().__init__(vessel=vessel, domain=domain, plato_url=plato_url)
        self.room = domain

    def _write(self, session_type: str, data: Dict[str, Any]) -> bool:
        tile = {
            "question": f"game:{session_type}",
            "answer": str(data),
            "confidence": 0.9,
            "metadata": {
                "player_id": self.player_id,
                "session_type": session_type,
                "timestamp": time.time(),
                **data
            }
        }
        try:
            resp = requests.post(f"{self.plato_url}/room/{self.room}", json=tile, timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    def log_session(
        self,
        game_name: str,
        platform: str,
        duration_minutes: int,
        session_type: str,
        result: Optional[str] = None,
        score: Optional[int] = None,
        achievements: Optional[List[str]] = None
    ) -> bool:
        """Log a gaming session."""
        return self._write("session", {
            "game_name": game_name,
            "platform": platform,
            "duration_minutes": duration_minutes,
            "session_type": session_type,
            "result": result,
            "score": score,
            "achievements": achievements or [],
        })
    
    def log_achievement(self, name: str, game: str, rarity: str = "common") -> bool:
        """Log an unlocked achievement."""
        return self._write("achievement", {
            "name": name,
            "game": game,
            "rarity": rarity,
        })
    
    def ask(self, question: str) -> str:
        """Query gaming history from PLATO."""
        try:
            resp = requests.get(f"{self.plato_url}/room/{self.room}?limit=20", timeout=5)
            if resp.status_code == 200:
                tiles = resp.json().get("tiles", [])
                relevant = [t for t in tiles if any(w in str(t).lower() for w in question.lower().split()[:3])]
                if relevant:
                    return f"Found {len(relevant)} gaming records: {relevant[-1].get('answer', '')[:200]}"
        except:
            pass
        return "Gaming system unavailable."
