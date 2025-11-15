import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class Database:
    def __init__(self, filename='bot_data.json'):
        self.filename = filename
        self.data = self._load_data()
    
    def _load_data(self) -> dict:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._init_data()
        return self._init_data()
    
    def _init_data(self) -> dict:
        return {
            'users': {},
            'giveaways': {},
            'drafts': {}
        }
    
    def _save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_user(self, user_id: int) -> dict:
        user_id_str = str(user_id)
        if user_id_str not in self.data['users']:
            self.data['users'][user_id_str] = {
                'user_id': user_id,
                'balance': 0.0,
                'giveaways': [],
                'drafts': [],
                'joined_channel': False
            }
            self._save_data()
        return self.data['users'][user_id_str]
    
    def update_user_balance(self, user_id: int, amount: float):
        user = self.get_user(user_id)
        user['balance'] = amount
        self._save_data()
    
    def set_channel_joined(self, user_id: int, joined: bool):
        user = self.get_user(user_id)
        user['joined_channel'] = joined
        self._save_data()
    
    def add_draft(self, user_id: int, draft_data: dict) -> str:
        user = self.get_user(user_id)
        draft_id = f"draft_{user_id}_{len(self.data['drafts'])}"
        draft_data['draft_id'] = draft_id
        draft_data['user_id'] = user_id
        draft_data['created_at'] = datetime.now().isoformat()
        
        self.data['drafts'][draft_id] = draft_data
        user['drafts'].append(draft_id)
        self._save_data()
        return draft_id
    
    def get_user_drafts(self, user_id: int) -> List[dict]:
        user = self.get_user(user_id)
        drafts = []
        for draft_id in user['drafts']:
            if draft_id in self.data['drafts']:
                drafts.append(self.data['drafts'][draft_id])
        return drafts
    
    def delete_draft(self, draft_id: str):
        if draft_id in self.data['drafts']:
            user_id = self.data['drafts'][draft_id]['user_id']
            user = self.get_user(user_id)
            if draft_id in user['drafts']:
                user['drafts'].remove(draft_id)
            del self.data['drafts'][draft_id]
            self._save_data()
    
    def add_giveaway(self, user_id: int, giveaway_data: dict) -> str:
        user = self.get_user(user_id)
        giveaway_id = f"giveaway_{user_id}_{len(self.data['giveaways'])}"
        giveaway_data['giveaway_id'] = giveaway_id
        giveaway_data['user_id'] = user_id
        giveaway_data['created_at'] = datetime.now().isoformat()
        giveaway_data['status'] = 'scheduled'
        
        self.data['giveaways'][giveaway_id] = giveaway_data
        user['giveaways'].append(giveaway_id)
        self._save_data()
        return giveaway_id
    
    def get_user_giveaways(self, user_id: int) -> List[dict]:
        user = self.get_user(user_id)
        giveaways = []
        for giveaway_id in user['giveaways']:
            if giveaway_id in self.data['giveaways']:
                giveaways.append(self.data['giveaways'][giveaway_id])
        return giveaways
    
    def get_giveaway(self, giveaway_id: str) -> Optional[dict]:
        return self.data['giveaways'].get(giveaway_id)
    
    def update_giveaway_status(self, giveaway_id: str, status: str):
        if giveaway_id in self.data['giveaways']:
            self.data['giveaways'][giveaway_id]['status'] = status
            self._save_data()
    
    def delete_giveaway(self, giveaway_id: str):
        if giveaway_id in self.data['giveaways']:
            user_id = self.data['giveaways'][giveaway_id]['user_id']
            user = self.get_user(user_id)
            if giveaway_id in user['giveaways']:
                user['giveaways'].remove(giveaway_id)
            del self.data['giveaways'][giveaway_id]
            self._save_data()
