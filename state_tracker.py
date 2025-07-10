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

    def get_recent_history(self, max_tokens):
        recent_history = []
        current_tokens = 0
        # Iterate in reverse to get the most recent messages first
        for message in reversed(self.discussion_history):
            # A very rough estimate: 1 token ~ 4 characters for Japanese
            message_length = len(message["text"]) + len(message["speaker"]) + 5 # Add some buffer for speaker name and formatting
            if current_tokens + message_length <= max_tokens:
                recent_history.append(message)
                current_tokens += message_length
            else:
                break
        # Return in chronological order
        return list(reversed(recent_history))

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
