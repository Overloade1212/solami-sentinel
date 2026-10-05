"""
Analytics and Event Engine for Solami Sentinel
Processes Solana DEX trades, tracks liquidity pools, and detects whale movements.
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, List, Optional

@dataclass
class TradeEvent:
    signature: str
    timestamp: datetime
    dex: str
    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    value_usd: float
    tx_type: str  # "BUY" or "SELL"
    trader: str
    is_whale: bool = False
    is_mega_whale: bool = False

@dataclass
class PoolCreationEvent:
    signature: str
    timestamp: datetime
    dex: str
    token_a: str
    token_b: str
    initial_liquidity_usd: float
    pool_address: str
    creator: str

class MarketAnalytics:
    def __init__(self, sol_price_usd: float = 154.50, max_history: int = 50):
        self.sol_price_usd = sol_price_usd
        self.max_history = max_history
        
        self.total_trades: int = 0
        self.total_volume_usd: float = 0.0
        self.buy_volume_usd: float = 0.0
        self.sell_volume_usd: float = 0.0
        self.whale_trades_count: int = 0
        
        self.recent_trades: Deque[TradeEvent] = deque(maxlen=max_history)
        self.whale_alerts: Deque[TradeEvent] = deque(maxlen=max_history)
        self.new_pools: Deque[PoolCreationEvent] = deque(maxlen=max_history)
        
        # Dex breakdown counters
        self.dex_counts: dict = {}

    def register_trade(self, trade: TradeEvent):
        self.total_trades += 1
        self.total_volume_usd += trade.value_usd
        
        if trade.tx_type == "BUY":
            self.buy_volume_usd += trade.value_usd
        else:
            self.sell_volume_usd += trade.value_usd
            
        if trade.is_whale or trade.is_mega_whale:
            self.whale_trades_count += 1
            self.whale_alerts.appendleft(trade)
            
        self.recent_trades.appendleft(trade)
        self.dex_counts[trade.dex] = self.dex_counts.get(trade.dex, 0) + 1

    def register_pool_creation(self, pool: PoolCreationEvent):
        self.new_pools.appendleft(pool)

    def get_buy_sell_ratio(self) -> tuple[float, float]:
        total = self.buy_volume_usd + self.sell_volume_usd
        if total == 0:
            return (50.0, 50.0)
        buy_pct = (self.buy_volume_usd / total) * 100.0
        sell_pct = (self.sell_volume_usd / total) * 100.0
        return (buy_pct, sell_pct)

    def get_net_sol_flow(self) -> float:
        # positive means net SOL bought, negative means net SOL sold
        net_usd = self.buy_volume_usd - self.sell_volume_usd
        return net_usd / self.sol_price_usd if self.sol_price_usd > 0 else 0.0

    @staticmethod
    def format_usd(value: float) -> str:
        if value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        if value >= 1_000:
            return f"${value / 1_000:.1f}k"
        return f"${value:.2f}"

    @staticmethod
    def truncate_address(addr: str, prefix_len: int = 4, suffix_len: int = 4) -> str:
        if not addr or len(addr) <= prefix_len + suffix_len:
            return addr
        return f"{addr[:prefix_len]}...{addr[-suffix_len:]}"
