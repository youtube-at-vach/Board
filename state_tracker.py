# state_tracker.py

import json
import os
from datetime import datetime

class StateTracker:
    def __init__(self, log_dir='logs'):
        self.discussion_history = []
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def add_message(self, round_num, speaker, text):
        self.discussion_history.append({
            "round": round_num,
            "speaker": speaker,
            "text": text
        })

    def get_history(self):
        return self.discussion_history

    def save_logs(self, topic):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize topic for filename
        sanitized_topic = ''.join(c for c in topic if c.isalnum() or c in [' ', '_']).replace(' ', '_')
        filename = f"debate_{sanitized_topic}_{timestamp}.jsonl"
        filepath = os.path.join(self.log_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            for entry in self.discussion_history:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        print(f"Discussion logs saved to {filepath}")
