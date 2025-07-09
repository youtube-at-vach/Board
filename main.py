import argparse
import yaml
import os

from moderator_engine import ModeratorEngine
from agent_engine import AgentEngine
from state_tracker import StateTracker
from llm_api import initialize_llm_api_map, LLM_API_MAP
from utils import debug_print, DEBUG_MODE, COLOR_RESET, COLOR_MODERATOR, COLOR_AGENT_A, COLOR_AGENT_B, COLOR_AGENT_C

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    global DEBUG_MODE

    parser = argparse.ArgumentParser(description='CLI-based AI Discussion Platform.')
    parser.add_argument('--topic', type=str, required=True, help='The topic of the discussion.')
    parser.add_argument('--rounds', type=int, default=5, help='Number of discussion rounds.')
    parser.add_argument('--debug', action='store_true', help='Enable debug output.')
    parser.add_argument('--summarize-rounds', action='store_true', help='Moderator summarizes each round.')
    args = parser.parse_args()

    DEBUG_MODE = args.debug

    print(f"Discussion Topic: {args.topic}")
    print(f"Number of Rounds: {args.rounds}")

    # Load agents configuration
    agents_config_path = os.path.join(os.path.dirname(__file__), 'config', 'agents.yaml')
    agents_config = load_config(agents_config_path)

    # Load models configuration
    models_config_path = os.path.join(os.path.dirname(__file__), 'config', 'models.yaml')
    models_config = load_config(models_config_path)

    # Initialize LLM_API_MAP with models configuration
    initialize_llm_api_map(models_config)

    moderator_config = agents_config['moderator']
    agent_configs = agents_config['agents']

    print("\n--- Configuration Loaded ---")
    print(f"Moderator: {moderator_config['name']} ({moderator_config['model']})")
    for agent in agent_configs:
        print(f"Agent: {agent['name']} ({agent['model']})")
    print("--------------------------")

    moderator_engine = ModeratorEngine(moderator_config)
    agent_engine = AgentEngine(agent_configs)
    state_tracker = StateTracker()

    # Initial moderator statement
    initial_moderator_statement = f"本日は「{args.topic}」について議論します。"
    state_tracker.add_message(0, moderator_config['name'], initial_moderator_statement)
    print(f"{COLOR_MODERATOR}[Round 0] {moderator_config['name']}:{COLOR_RESET}\n> {initial_moderator_statement}")

    for round_num in range(1, args.rounds + 1):
        print(f"\n{COLOR_RESET}[Round {round_num}]{COLOR_RESET}")
        
        # Moderator decides next speaker
        next_speaker_name, moderator_statement = moderator_engine.decide_next_speaker(
            args.topic, state_tracker.get_history(), round_num, agent_configs
        )
        state_tracker.add_message(round_num, moderator_config['name'], moderator_statement)
        print(f"{COLOR_MODERATOR}[{moderator_config['name']}]:{COLOR_RESET}\n> {moderator_statement}")

        # Agent responds
        agent_response = agent_engine.get_agent_response(
            next_speaker_name, args.topic, state_tracker.get_history()
        )
        state_tracker.add_message(round_num, next_speaker_name, agent_response)
        
        # Determine agent color
        agent_color = COLOR_RESET
        if next_speaker_name == "AI-A":
            agent_color = COLOR_AGENT_A
        elif next_speaker_name == "AI-B":
            agent_color = COLOR_AGENT_B
        elif next_speaker_name == "AI-C":
            agent_color = COLOR_AGENT_C

        print(f"{agent_color}[{next_speaker_name}]:{COLOR_RESET}\n> {agent_response}")

        if args.summarize_rounds and round_num < args.rounds: # Summarize if not the last round
            summary = moderator_engine.generate_summary(args.topic, state_tracker.get_history())
            print(f"{COLOR_MODERATOR}[Moderator Summary]:{COLOR_RESET}\n> {summary}")

    # Save logs
    state_tracker.save_logs(args.topic)

if __name__ == '__main__':
    main()