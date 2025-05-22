from ctransformers import AutoModelForCausalLM
from app.utils.config_loader import load_config

class LLMRunner:
    def __init__(self):
        config = load_config()
        # self.context_length = 4096
        self.model = AutoModelForCausalLM.from_pretrained(
            config["paths"]["model_path"],
            model_type="mistral",              
            # max_tokens=2000,               
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            stop=["<|endoftext|>", "User:", "Assistant:"]
        )
        print(f"Loaded model from {config['paths']['model_path']}")

    def truncate_prompt(self, prompt: str) -> str:
        tokens = prompt.split()
        if len(tokens) > self.context_length - 512:
            tokens = tokens[-(self.context_length - 512):]
        return " ".join(tokens)

    def generate_response(self, prompt: str) -> str:
        try:
            print(f"Generating response for prompt:")
            response = self.model(prompt)
            print(f"Generated response: {response}")
            return response.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"
