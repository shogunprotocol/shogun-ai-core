import requests
import json
from datetime import datetime

class FlareFDCProvider:
    def __init__(self):
        self.defillama_url = "https://api.llama.fi/protocol/sonic"
        self.github_url = "https://api.github.com/repos/sonicdefi/contracts"
        self.headers = {"Accept": "application/vnd.github+json"}

    def fetch_protocol_metadata(self):
        metadata = {}

        # TVL history from DeFiLlama
        response = requests.get(self.defillama_url)
        if response.ok:
            data = response.json()
            metadata["tvl"] = data.get("tvl", {})
            metadata["chain"] = data.get("chain", "unknown")

        # GitHub last update
        github = requests.get(self.github_url, headers=self.headers)
        if github.ok:
            metadata["last_updated"] = github.json().get("updated_at", "n/a")

        return metadata

    def format_for_knowledge_box(self, raw_data):
        return {
            "vault_id": "sonic_usdc",
            "tvl_7d": raw_data["tvl"].get("7d", None),
            "last_commit": raw_data.get("last_updated", "n/a"),
            "chain": raw_data.get("chain", "unknown"),
            "blacklisted": False  # Placeholder — can integrate ChainFeeds
        }
