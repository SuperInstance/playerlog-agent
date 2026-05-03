#!/usr/bin/env python3
"""playerlog-agent — Game session tracking, stats, and achievements
Now uses domain-agent-base for PLATO integration, health checks, and reporting.
"""
import json, time
from typing import List, Dict

try:
    from domain_agent_base import DomainAgent
except ImportError:
    class DomainAgent:
        domain = "base"
        plato_url = "http://147.224.38.131:8847"
        def __init__(self):
            self.tiles_submitted = []
            self.errors = []
            self.start_time = time.time()
        def submit_tile(self, question, answer, room=None):
            self.tiles_submitted.append({"q": question, "a": answer})
            return True
        def get_stats(self):
            return {"domain": self.domain, "tiles": len(self.tiles_submitted)}
        def run(self):
            raise NotImplementedError

class PlayerLogAgent(DomainAgent):
    domain = "player"
    version = "0.2.0"
    
    def __init__(self):
        super().__init__()
        self.sessions: List[Dict] = []
        self.achievements: List[str] = []
    
    def log_session(self, game: str, duration_min: int, score: int, notes: str=""):
        sess = {"game": game, "duration": duration_min, "score": score, "notes": notes, "time": time.time()}
        self.sessions.append(sess)
        self.submit_tile(f"Played {game} for {duration_min}min", f"Score: {score}. {notes}")
        return sess
    
    def get_game_stats(self) -> Dict:
        if not self.sessions: return {"error": "No sessions"}
        games = {}
        for s in self.sessions:
            g = s["game"]
            if g not in games: games[g] = {"count": 0, "total_score": 0, "total_time": 0}
            games[g]["count"] += 1
            games[g]["total_score"] += s["score"]
            games[g]["total_time"] += s["duration"]
        return {"sessions": len(self.sessions), "games": games, "avg_score": sum(s["score"] for s in self.sessions)/len(self.sessions)}
    
    def unlock_achievement(self, name: str):
        self.achievements.append(name)
        self.submit_tile(f"Unlocked achievement: {name}", f"Total achievements: {len(self.achievements)}")
    
    def run(self):
        print(f"PlayerLogAgent v{self.version} starting...")
        self.log_session("Elden Ring", 120, 8500, "Defeated Malenia")
        self.log_session("Hades", 45, 3200, "Escaped Tartarus")
        self.log_session("Elden Ring", 90, 12000, "New build test")
        self.unlock_achievement("First Boss")
        self.unlock_achievement("Speedrunner")
        stats = self.get_game_stats()
        self.submit_tile("What are my gaming stats?", json.dumps(stats, indent=2))
        print(f"Run complete. {len(self.sessions)} sessions, {len(self.achievements)} achievements, {len(self.tiles_submitted)} tiles")

def main():
    agent = PlayerLogAgent()
    agent.run()
    print(f"\nStats: {json.dumps(agent.get_stats(), indent=2)}")
    print(f"\nHealth: {json.dumps(agent.health_check(), indent=2)}")

if __name__ == "__main__":
    main()
