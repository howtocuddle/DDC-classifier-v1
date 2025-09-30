import os
import json
from typing import List, Dict, Any, Optional
import requests

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

class OpenRouterLLM:
	"""
	Lightweight LLM manager for OpenRouter.

	- Reads API key from `api.txt` in the same directory if OPENROUTER_API_KEY env not set
	- Default model: x-ai/grok-4-fast:free
	- Interface: generate(messages: List[Dict[str,str]], **kwargs) -> str
	"""

	def __init__(self, model: str = "x-ai/grok-4-fast:free", api_key: Optional[str] = None, timeout: int = 60):
		self.model = model
		self.timeout = timeout
		self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or self._read_api_key()
		if not self.api_key:
			raise RuntimeError("OpenRouter API key not found. Set OPENROUTER_API_KEY or place api.txt beside this file.")

	def _read_api_key(self) -> Optional[str]:
		this_dir = os.path.dirname(os.path.abspath(__file__))
		candidate = os.path.join(this_dir, "api.txt")
		if os.path.exists(candidate):
			with open(candidate, "r", encoding="utf-8") as f:
				return f.read().strip()
		return None

	def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 1200, response_format: Optional[str] = None, stream: bool = False, stream_callback: Optional[callable] = None) -> str:
		headers = {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json",
		}
		payload: Dict[str, Any] = {
			"model": self.model,
			"messages": messages,
			"temperature": temperature,
			"max_tokens": max_tokens,
		}
		# Some models support response_format
		if response_format:
			payload["response_format"] = {"type": response_format}
		
		if stream:
			payload["stream"] = True
			return self._stream_generate(headers, payload, stream_callback)
		else:
			resp = requests.post(OPENROUTER_API_URL, headers=headers, data=json.dumps(payload), timeout=self.timeout)
			resp.raise_for_status()
			data = resp.json()
			# Extract assistant content
			try:
				return data["choices"][0]["message"]["content"]
			except Exception:
				return json.dumps(data)
	
	def _stream_generate(self, headers: Dict, payload: Dict, callback: Optional[callable] = None) -> str:
		"""Stream response and optionally call callback for each chunk."""
		resp = requests.post(OPENROUTER_API_URL, headers=headers, data=json.dumps(payload), timeout=self.timeout, stream=True)
		resp.raise_for_status()
		
		full_text = ""
		for line in resp.iter_lines():
			if not line:
				continue
			line_str = line.decode('utf-8')
			if line_str.startswith("data: "):
				data_str = line_str[6:]
				if data_str == "[DONE]":
					break
				try:
					chunk = json.loads(data_str)
					delta = chunk.get("choices", [{}])[0].get("delta", {})
					content = delta.get("content", "")
					if content:
						full_text += content
						if callback:
							callback(content)
				except Exception:
					pass
		return full_text
