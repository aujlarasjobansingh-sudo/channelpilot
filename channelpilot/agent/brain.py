"""The agent's brain: talks to a local Ollama model, or a cloud API if configured."""
import requests


class BrainNotAvailable(Exception):
    pass


class Brain:
    def __init__(self, cfg):
        self.cfg = cfg.get("brain", {})

    def provider(self):
        return self.cfg.get("provider", "ollama")

    def available(self):
        if self.provider() == "ollama":
            try:
                r = requests.get(
                    self.cfg.get("ollama_url", "http://localhost:11434").rstrip("/") + "/api/tags",
                    timeout=4,
                )
                return r.status_code == 200
            except Exception:
                return False
        c = self.cfg
        return bool(c.get("api_key") and c.get("api_base"))

    def chat(self, messages, system=None):
        if self.provider() == "ollama":
            return self._ollama(messages, system)
        return self._compat(messages, system)

    def _ollama(self, messages, system):
        url = self.cfg.get("ollama_url", "http://localhost:11434").rstrip("/") + "/api/chat"
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs += [{"role": m["role"], "content": m["content"]} for m in messages]
        try:
            r = requests.post(
                url,
                json={
                    "model": self.cfg.get("ollama_model", "llama3.1:8b"),
                    "messages": msgs,
                    "stream": False,
                    "options": {"temperature": 0.7},
                },
                timeout=600,
            )
        except Exception:
            raise BrainNotAvailable(
                "I can't reach Ollama — it's not running. Start Ollama on your PC and make sure "
                "the model is pulled (`ollama pull llama3.1:8b`), then talk to me again."
            )
        if r.status_code != 200:
            raise BrainNotAvailable(f"Ollama answered with an error ({r.status_code}): {r.text[:200]}")
        msg = (r.json().get("message") or {}).get("content", "").strip()
        if not msg:
            raise BrainNotAvailable("Ollama gave an empty answer. Try again.")
        return msg

    def _compat(self, messages, system):
        base = self.cfg.get("api_base", "").rstrip("/")
        key = self.cfg.get("api_key", "")
        if not key or not base:
            raise BrainNotAvailable(
                "No API key set. Paste your key and base URL in config.yaml under brain, "
                "or switch provider to 'ollama'."
            )
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs += [{"role": m["role"], "content": m["content"]} for m in messages]
        try:
            r = requests.post(
                base + "/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={
                    "model": self.cfg.get("api_model", "gpt-4o-mini"),
                    "messages": msgs,
                    "temperature": 0.7,
                },
                timeout=300,
            )
        except Exception as e:
            raise BrainNotAvailable(f"API call failed: {e}")
        if r.status_code != 200:
            raise BrainNotAvailable(f"API error ({r.status_code}): {r.text[:200]}")
        return r.json()["choices"][0]["message"]["content"].strip()
