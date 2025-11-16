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
            'drafts': {},
            'active_giveaways': {},  # Maps discussion_group_id -> dice giveaway_id
            'active_first_comment_giveaways': {},  # Maps group_id -> first comment giveaway_id
            'withdrawals': {}
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
                'joined_channel': False,
                'banned': False
            }
            self._save_data()
        return self.data['users'][user_id_str]
    
    def get_all_users(self) -> dict:
        return self.data['users']
    
    def ban_user(self, user_id: int):
        user = self.get_user(user_id)
        user['banned'] = True
        self._save_data()
    
    def unban_user(self, user_id: int):
        user = self.get_user(user_id)
        user['banned'] = False
        self._save_data()
    
    def is_user_banned(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        return user.get('banned', False)
    
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
    
    def get_draft(self, draft_id: str) -> Optional[dict]:
        return self.data['drafts'].get(draft_id)
    
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
        giveaway_data['participants'] = []
        
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
    
    def get_all_giveaways(self) -> List[dict]:
        return list(self.data['giveaways'].values())
    
    def update_giveaway_message(self, giveaway_id: str, message_id: int):
        if giveaway_id in self.data['giveaways']:
            self.data['giveaways'][giveaway_id]['message_id'] = message_id
            if 'participants' not in self.data['giveaways'][giveaway_id]:
                self.data['giveaways'][giveaway_id]['participants'] = []
            self._save_data()
    
    def add_participant(self, giveaway_id: str, user_id: int, username: str, number: int):
        if giveaway_id in self.data['giveaways']:
            if 'participants' not in self.data['giveaways'][giveaway_id]:
                self.data['giveaways'][giveaway_id]['participants'] = []
            
            self.data['giveaways'][giveaway_id]['participants'].append({
                'user_id': user_id,
                'username': username,
                'number': number
            })
            self._save_data()
    
    def update_participant(self, giveaway_id: str, user_id: int, new_number: int):
        if giveaway_id in self.data['giveaways']:
            participants = self.data['giveaways'][giveaway_id].get('participants', [])
            for participant in participants:
                if participant['user_id'] == user_id:
                    participant['number'] = new_number
                    self._save_data()
                    return
    
    def get_giveaway_participants(self, giveaway_id: str) -> List[dict]:
        if giveaway_id in self.data['giveaways']:
            return self.data['giveaways'][giveaway_id].get('participants', [])
        return []
    
    def clear_giveaway_participants(self, giveaway_id: str):
        if giveaway_id in self.data['giveaways']:
            self.data['giveaways'][giveaway_id]['participants'] = []
            self._save_data()
    
    def set_giveaway_winner(self, giveaway_id: str, winner_id: int):
        if giveaway_id in self.data['giveaways']:
            self.data['giveaways'][giveaway_id]['winner_id'] = winner_id
            self.data['giveaways'][giveaway_id]['prize_claimed'] = False
            self._save_data()
    
    def mark_prize_claimed(self, giveaway_id: str):
        if giveaway_id in self.data['giveaways']:
            self.data['giveaways'][giveaway_id]['prize_claimed'] = True
            self._save_data()
    
    def set_active_giveaway_for_discussion(self, discussion_group: str, giveaway_id: str):
        """Set the active giveaway for a discussion group"""
        if 'active_giveaways' not in self.data:
            self.data['active_giveaways'] = {}
        self.data['active_giveaways'][discussion_group] = giveaway_id
        self._save_data()
    
    def get_active_giveaway_for_discussion(self, discussion_group: str) -> Optional[str]:
        """Get the active giveaway ID for a discussion group"""
        if 'active_giveaways' not in self.data:
            self.data['active_giveaways'] = {}
        return self.data['active_giveaways'].get(discussion_group)
    
    def clear_active_giveaway_for_discussion(self, discussion_group: str):
        """Clear the active giveaway for a discussion group"""
        if 'active_giveaways' not in self.data:
            self.data['active_giveaways'] = {}
        if discussion_group in self.data['active_giveaways']:
            del self.data['active_giveaways'][discussion_group]
            self._save_data()
    
    def add_withdrawal_request(self, user_id: int, amount: float, upi_id: str) -> str:
        """Add a new withdrawal request"""
        if 'withdrawals' not in self.data:
            self.data['withdrawals'] = {}
        
        withdrawal_id = f"withdraw_{user_id}_{len(self.data['withdrawals'])}"
        withdrawal_data = {
            'withdrawal_id': withdrawal_id,
            'user_id': user_id,
            'amount': amount,
            'upi_id': upi_id,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'rejection_reason': None
        }
        
        self.data['withdrawals'][withdrawal_id] = withdrawal_data
        self._save_data()
        return withdrawal_id
    
    def get_withdrawal_request(self, withdrawal_id: str) -> Optional[dict]:
        """Get a withdrawal request by ID"""
        if 'withdrawals' not in self.data:
            self.data['withdrawals'] = {}
        return self.data['withdrawals'].get(withdrawal_id)
    
    def set_active_first_comment_giveaway(self, group_id: str, giveaway_id: str):
        """Set the active first comment giveaway for a group"""
        if 'active_first_comment_giveaways' not in self.data:
            self.data['active_first_comment_giveaways'] = {}
        self.data['active_first_comment_giveaways'][group_id] = giveaway_id
        self._save_data()
    
    def get_active_first_comment_giveaway(self, group_id: str) -> Optional[str]:
        """Get the active first comment giveaway ID for a group"""
        if 'active_first_comment_giveaways' not in self.data:
            self.data['active_first_comment_giveaways'] = {}
        return self.data['active_first_comment_giveaways'].get(group_id)
    
    def clear_active_first_comment_giveaway(self, group_id: str):
        """Clear the active first comment giveaway for a group"""
        if 'active_first_comment_giveaways' not in self.data:
            self.data['active_first_comment_giveaways'] = {}
        if group_id in self.data['active_first_comment_giveaways']:
            del self.data['active_first_comment_giveaways'][group_id]
            self._save_data()
    
    def add_first_comment_participant(self, giveaway_id: str, user_id: int, username: str, timestamp: str, message_id: int):
        """Add a participant to a first comment giveaway with timestamp"""
        if giveaway_id in self.data['giveaways']:
            if 'participants' not in self.data['giveaways'][giveaway_id]:
                self.data['giveaways'][giveaway_id]['participants'] = []
            
            self.data['giveaways'][giveaway_id]['participants'].append({
                'user_id': user_id,
                'username': username,
                'timestamp': timestamp,
                'message_id': message_id
            })
            self._save_data()
    
    def set_first_comment_start_time(self, giveaway_id: str, start_time: str):
        """Set the start time for a first comment giveaway"""
        if giveaway_id in self.data['giveaways']:
            self.data['giveaways'][giveaway_id]['start_time_iso'] = start_time
            self._save_data()
    
    def update_withdrawal_status(self, withdrawal_id: str, status: str, rejection_reason: str = None):
        """Update withdrawal request status"""
        if 'withdrawals' not in self.data:
            self.data['withdrawals'] = {}
        
        if withdrawal_id in self.data['withdrawals']:
            self.data['withdrawals'][withdrawal_id]['status'] = status
            if rejection_reason:
                self.data['withdrawals'][withdrawal_id]['rejection_reason'] = rejection_reason
            self._save_data()
