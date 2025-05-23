from llama_cpp import Llama
from app.utils.config_loader import load_config

class LLMRunner:
    def __init__(self):
        config = load_config()
        self.context_length = 4096
        self.model = Llama(
            model_path=config["paths"]["model_path"],
            n_ctx=self.context_length,
            n_threads=8, 
            n_batch=128,  
            temperature=0.7,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["<|endoftext|>"],
            verbose=True 
        )
        print(f"Loaded GGUF model from {config['paths']['model_path']}")

    def truncate_prompt(self, prompt: str) -> str:
        tokens = prompt.split()
        if len(tokens) > self.context_length - 512:
            tokens = tokens[-(self.context_length - 512):]
        return " ".join(tokens)

    def generate_response(self, prompt: str) -> str:
        try:
            print("Generating response for prompt...")
            response = self.model(
                prompt=prompt,
                max_tokens=512, 
                stop=["<|endoftext|>"]
            )
            print("Response generated. {response}")
            return response["choices"][0]["text"].strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"
        
    def stream_response(self, prompt: str):
        try:
            print("Streaming response for prompt...")
            for chunk in self.model(
                prompt=prompt,
                max_tokens=512,
                stream=True,
                stop=["<|endoftext|>", "User:", "Assistant:"]
            ):
                yield chunk["choices"][0]["text"]
        except Exception as e:
            yield f"\n[Error generating response: {str(e)}]"
