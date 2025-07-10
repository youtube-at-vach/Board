# agent_engine.py

from llm_api import LLM_API_MAP
from utils import debug_print # Import debug_print

class AgentEngine:
    def __init__(self, configs, conversation_mode=False):
        self.agents = {}
        for config in configs:
            self.agents[config['name']] = {
                'model_key': config['model'], # This is the key from models.yaml
                'persona': config['persona'],
                'response_length': config.get('response_length', 'medium') # Get response_length from config
            }
        self.conversation_mode = conversation_mode

    def get_agent_response(self, agent_name, topic, history, max_history_tokens=4000):
        agent_info = self.agents.get(agent_name)
        if not agent_info:
            raise ValueError(f"Agent {agent_name} not found.")

        model_key = agent_info['model_key']
        persona = agent_info['persona']
        response_length = agent_info['response_length']

        llm_client = LLM_API_MAP[model_key]['client']
        model_name_for_api = LLM_API_MAP[model_key]['model_name_for_api']

        # Construct the prompt for the agent
        # This prompt should include the persona, topic, and discussion history
        recent_history = history # history is already recent history from main.py
        history_text = "\n".join([f"{item['speaker']}: {item['text']}" for item in recent_history])
        
        if self.conversation_mode:
            prompt = f"""
あなたは{persona}という立場のAIです。以下の主題とこれまでの会話内容を踏まえて、直前の発言に反応しつつ、あなたの意見を自然な会話の流れで述べてください。非常にフランクに、短い言葉で返してください。必ずしも完璧な意見を述べる必要はありません。考えがまとまっていなくても、率直な感想を述べてください。「うーん」「どうかな」「あんまり考えたことない」といった表現も使って構いません。一言、二言で終わっても構いません。簡潔に、対話的に応答することを心がけてください。

主題: {topic}

これまでの会話:
{history_text}

あなたの発言:
"""
        else:
            prompt = f"""
あなたは{persona}という立場のAIです。以下の主題とこれまでの討論内容を踏まえて、あなたの意見を述べてください。

主題: {topic}

これまでの討論:
{history_text}

あなたの発言:
"""
        
        # In a real scenario, call the appropriate LLM API here
        debug_print(f"[DEBUG] Calling LLM for {agent_name} with model {model_key} ({model_name_for_api}), length {response_length}")
        response = llm_client.generate(prompt, model_name_for_api, response_length)
        return response
