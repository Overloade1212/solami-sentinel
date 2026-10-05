"""
Solami Sentinel Configuration
Configures Solami RPC, WebSocket, Blur feeds, and whale detection thresholds.
"""

import os
from dataclasses import dataclass
from typing import Optional

# Solami Infrastructure Endpoints
SOLAMI_DATA_API = os.getenv("SOLAMI_DATA_API", "https://api.solami.dev")
SOLAMI_BLUR_API = os.getenv("SOLAMI_BLUR_API", "https://blur.solami.dev/v1")
SOLAMI_WS_ENDPOINT = os.getenv("SOLAMI_WS_ENDPOINT", "wss://mirage.solami.dev/ws")
SOLAMI_RPC_ENDPOINT = os.getenv("SOLAMI_RPC_ENDPOINT", "https://rpc.solami.dev")

# Fallback Solana Public Endpoints (Mainnet-Beta)
FALLBACK_SOLANA_RPC = os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com")
FALLBACK_SOLANA_WS = os.getenv("SOLANA_WS", "wss://api.mainnet-beta.solana.com")

# Detection & Monitoring Thresholds
DEFAULT_WHALE_THRESHOLD_USD = float(os.getenv("WHALE_THRESHOLD_USD", "5000.0"))
DEFAULT_MEGA_WHALE_THRESHOLD_USD = float(os.getenv("MEGA_WHALE_THRESHOLD_USD", "25000.0"))
DEFAULT_SOL_PRICE_USD = float(os.getenv("DEFAULT_SOL_PRICE_USD", "154.50"))

# Known Solana DEX Program IDs
DEX_PROGRAM_IDS = {
    "Raydium AMM v4": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "Raydium CPMM": "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C",
    "Raydium CLMM": "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",
    "Meteora DLMM": "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo",
    "Meteora DBC/Dynamic": "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",
    "Orca Whirlpools": "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
    "Pump.fun": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
}

# Popular Solana Token Mints
KNOWN_TOKENS = {
    "So11111111111111111111111111111111111111112": "SOL",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN": "JUP",
    "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm": "WIF",
    "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": "BONK",
    "rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof": "RENDER",
    "HZ1JovNiDcZvKhsqzy1q2deiEkAPz2bgwP35uUC7rquM": "PYTH",
}

@dataclass
class SentinelConfig:
    api_key: Optional[str] = None
    rpc_url: str = SOLAMI_RPC_ENDPOINT
    ws_url: str = SOLAMI_WS_ENDPOINT
    whale_threshold_usd: float = DEFAULT_WHALE_THRESHOLD_USD
    mega_whale_threshold_usd: float = DEFAULT_MEGA_WHALE_THRESHOLD_USD
    sol_price_usd: float = DEFAULT_SOL_PRICE_USD
    demo_mode: bool = False
    refresh_rate: float = 0.5  # seconds
