#!/usr/bin/env python3
"""playerlog-agent — Game session tracking, stats, and achievements"""
import json, time
from typing import List, Dict, Optional

class PlayerLogAgent:
    def __init__(self, plato_url="http://147.224.38.131:8847"):
        self.plato_url = plato_url
        self.sessions: List[Dict] = []
        self.achievements: List[str] = []
    
    def log_session(self, game: str, duration_min: int, score: int, notes: str=""):
        sess = {"game": game, "duration": duration_min, "score": score, "notes": notes, "time": time.time()}
        self.sessions.append(sess)
        self._submit(f"Played {game} for {duration_min}min", f"Score: {score}. {notes}")
        return sess
    
    def get_stats(self) -> Dict:
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
        self._submit(f"Achievement unlocked", name)
    
    def _submit(self, q: str, a: str):
        try:
            import urllib.request
            urllib.request.urlopen(urllib.request.Request(f"{self.plato_url}/submit", data=json.dumps({"question": q, "answer": a, "agent": "playerlog-agent", "room": "playerlog"}).encode(), headers={"Content-Type": "application/json"}), timeout=5)
        except: pass

def demo():
    a = PlayerLogAgent()
    a.log_session("Elden Ring", 120, 4500, "Defeated Malenia")
    a.log_session("Hades", 45, 3200, "Escaped Tartarus")
    a.log_session("Elden Ring", 90, 3800, "Explored Caelid")
    a.unlock_achievement("First Victory")
    print(a.get_stats())

if __name__ == "__main__": demo()
