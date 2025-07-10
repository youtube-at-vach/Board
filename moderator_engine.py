# moderator_engine.py

from llm_api import LLM_API_MAP
import re
from utils import debug_print # Import debug_print

class ModeratorEngine:
    def __init__(self, config, conversation_mode=False):
        self.name = config['name']
        self.model_key = config['model'] # This is the key from models.yaml (e.g., 'gpt-3.5-turbo')
        self.persona = config['persona']
        self.llm_client = LLM_API_MAP[self.model_key]['client']
        self.model_name_for_api = LLM_API_MAP[self.model_key]['model_name_for_api']
        self.response_length = config.get('response_length', 'medium') # Get response_length from config
        self.conversation_mode = conversation_mode

    def decide_next_speaker(self, topic, history, current_round, agents, max_history_tokens=4000):
        recent_history = history # history is already recent history from main.py
        history_text = "\n".join([f"{item['speaker']}: {item['text']}" for item in recent_history])
        valid_agent_names = [agent['name'] for agent in agents]
        available_agents = ", ".join([agent['name'] for agent in agents])

        if self.conversation_mode:
            prompt = f"""
あなたは会話の進行役です。以下の主題と過去の発言を元に、次に発言すべき人物を選び、自然な会話の流れで話を振ってください。直前の発言内容に触れつつ、次の発言者が意見を述べやすいように促してください。相手に完璧な回答を求めず、気軽に意見を引き出すように促してください。短い返答でも会話が続くように、柔軟に対応してください。

利用可能な発言者: {available_agents}

主題: {topic}

過去の発言:
{history_text}

現在のラウンド: {current_round}

回答形式:
<呼びかけ>（例：「AI-Aさん、今のAI-Bさんの意見についてどう思われますか？」）
<簡単な説明>（例：「AI-Bさんの意見を受けて、AI-Aさんの視点からさらに深掘りしたいです」）
<質問>（例：「AIが教育に与える影響について、AI-Aさんの具体的な見解を聞かせていただけますか？」）
"""
        else:
            prompt = f"""
あなたは討論の司会者です。以下の主題と過去の発言を元に、次に発言すべき人物を選び、簡潔な理由を添えてその人物に話を振ってください。また、その人物にどのような質問をすべきか、短く具体的に提案してください。

利用可能な発言者: {available_agents}

主題: {topic}

過去の発言:
{history_text}

現在のラウンド: {current_round}

回答形式:
<呼びかけ>（例：「次は AI-A さん、お願いします」）
<簡単な説明>（例：「先ほどの意見に技術的な補足が必要だと感じました」）
<質問>（例：「AIが教育に与える影響について、具体的な事例を挙げていただけますか？」）
"""
        llm_response = self.llm_client.generate(prompt, self.model_name_for_api, self.response_length)

        # Parse LLM response to get next speaker and moderator statement
        lines = llm_response.split('\n')
        call_to_action = ""
        explanation = ""
        question = ""
        
        for line in lines:
            if line.startswith('<呼びかけ>'):
                call_to_action = line.replace('<呼びかけ>', '').strip()
            elif line.startswith('<簡単な説明>'):
                explanation = line.replace('<簡単な説明>', '').strip()
            elif line.startswith('<質問>'):
                question = line.replace('<質問>', '').strip()

        # If parsing with tags failed, use the raw response as the statement
        if not call_to_action and not explanation and not question:
            moderator_statement = llm_response.strip()
        else:
            moderator_statement = f"{call_to_action}\n\n{explanation}\n\n{question}"

        # Extract next speaker name from the call_to_action part
        next_speaker_name = "AI-A" # Default or fallback
        match = re.search(r'(AI-[A-Z])', call_to_action)
        if match and match.group(1) in valid_agent_names:
            next_speaker_name = match.group(1)
        else:
            # Fallback to cycling if no valid agent name is found in the response
            if history:
                last_speaker = history[-1]['speaker']
                try:
                    last_speaker_index = valid_agent_names.index(last_speaker)
                    next_speaker_index = (last_speaker_index + 1) % len(valid_agent_names)
                    next_speaker_name = valid_agent_names[next_speaker_index]
                except ValueError:
                    next_speaker_name = valid_agent_names[0] # If last speaker was moderator, pick first agent
            else:
                next_speaker_name = valid_agent_names[0] # First round, pick first agent

        return next_speaker_name, moderator_statement

    def generate_summary(self, topic, history, max_history_tokens=4000):
        recent_history = history # history is already recent history from main.py
        history_text = "\n".join([f"{item['speaker']}: {item['text']}" for item in recent_history])
        
        prompt = f"""
あなたは討論の司会者です。以下の主題とこれまでの討論内容を元に、簡潔に要点をまとめてください。

主題: {topic}

これまでの討論:
{history_text}

要約:
"""
        summary = self.llm_client.generate(prompt, self.model_name_for_api, "short") # Force short summary
        return summary

    def generate_moderator_prompt(self, topic, history, current_round, agents, max_history_tokens=4000):
        recent_history = history # history is already recent history from main.py
        history_text = "\n".join([f"{item['speaker']}: {item['text']}" for item in recent_history])
        available_agents = ", ".join([agent['name'] for agent in agents])
        
        prompt_template = """
あなたは討論の司会者です。以下の主題と過去の発言を元に、次に発言すべき人物を選び、簡潔な理由を添えてその人物に話を振ってください。

利用可能な発言者: {available_agents}

主題: {topic}

過去の発言:
{history}

現在のラウンド: {current_round}

回答形式:
<呼びかけ>（例：「次は AI-A さん、お願いします」）
<簡単な説明>（例：「先ほどの意見に技術的な補足が必要だと感じました」）
<質問>（例：「AIが教育に与える影響について、具体的な事例を挙げていただけますか？」）
"""
        
        return prompt_template.format(topic=topic, history=history_text, current_round=current_round, available_agents=available_agents)
