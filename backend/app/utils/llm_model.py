from llama_cpp import Llama
import re
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
        print(f"[INFO] Loaded GGUF model from {config['paths']['model_path']}")

    def truncate_prompt(self, prompt: str) -> str:
        tokens = prompt.split()
        if len(tokens) > self.context_length - 512:
            tokens = tokens[-(self.context_length - 512):]
        return " ".join(tokens)

    def _clean_streamed_text(self, text: str) -> str:
        text = re.sub(r'[ ]{2,}', ' ', text)
        text = re.sub(r'\s+\n', '\n', text)
        text = re.sub(r'\n\s+', '\n', text)
        return text

    def generate_response(self, prompt: str) -> str:
        try:
            print("[INFO] Generating full response...")
            response = self.model(
                prompt=prompt,
                max_tokens=512,
                stop=["<|endoftext|>"]
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def stream_response(self, prompt: str):
        try:
            print("[INFO] Streaming response...")
            buffer = ""
            for chunk in self.model(
                prompt=prompt,
                max_tokens=512,
                stream=True,
                stop=["<|endoftext|>", "User:", "Assistant:"]
            ):
                token = chunk["choices"][0]["text"]
                buffer += token

                if re.search(r"[ \n]$", buffer) or re.search(r'\]\([^)]+?\)$', buffer):
                    cleaned = self._clean_streamed_text(buffer)
                    if cleaned:
                        yield cleaned
                    buffer = ""

            if buffer.strip():
                yield self._clean_streamed_text(buffer)

        except Exception as e:
            yield f"\n[Error generating response: {str(e)}]"