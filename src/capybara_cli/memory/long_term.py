from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LongTermMemory:
    def __init__(self, persistence_path: str | None = None):
        self.persistence_path = Path(persistence_path) if persistence_path else None
        self.interactions: list[dict[str, Any]] = []
        
        if self.persistence_path:
            self._load()
    
    def store_interaction(self, content: str, metadata: dict[str, Any]):
        interaction = {
            "content": content,
            "metadata": metadata,
        }
        self.interactions.append(interaction)
        
        if self.persistence_path:
            self._save()
    
    def search(self, query: str) -> list[dict[str, Any]]:
        query_lower = query.lower()
        results = []
        
        for interaction in self.interactions:
            if query_lower in interaction["content"].lower():
                results.append(interaction)
        
        return results[-10:]
    
    def clear(self):
        self.interactions.clear()
        
        if self.persistence_path:
            self._save()
    
    def _load(self):
        if self.persistence_path and self.persistence_path.exists():
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    self.interactions = json.load(f)
            except:
                self.interactions = []
    
    def _save(self):
        if self.persistence_path:
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(self.interactions, f, indent=2)
