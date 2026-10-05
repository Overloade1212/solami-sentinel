import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics import MarketAnalytics, PoolCreationEvent, TradeEvent

def test_trade_registration():
    analytics = MarketAnalytics(sol_price_usd=150.0)
    
    # 1. Normal buy trade
    t1 = TradeEvent(
        signature="sig1",
        timestamp=datetime.now(),
        dex="Raydium AMM v4",
        token_in="SOL",
        token_out="JUP",
        amount_in=10.0,
        amount_out=1500.0,
        value_usd=1500.0,
        tx_type="BUY",
        trader="trader1",
        is_whale=False
    )
    analytics.register_trade(t1)
    assert analytics.total_trades == 1
    assert analytics.total_volume_usd == 1500.0
    assert analytics.buy_volume_usd == 1500.0
    assert analytics.sell_volume_usd == 0.0
    assert analytics.whale_trades_count == 0

def test_whale_detection():
    analytics = MarketAnalytics(sol_price_usd=150.0)
    
    # 2. Large whale sell trade
    t2 = TradeEvent(
        signature="sig2",
        timestamp=datetime.now(),
        dex="Meteora DBC",
        token_in="WIF",
        token_out="SOL",
        amount_in=25000.0,
        amount_out=50.0,
        value_usd=7500.0,
        tx_type="SELL",
        trader="whale1",
        is_whale=True
    )
    analytics.register_trade(t2)
    assert analytics.total_trades == 1
    assert analytics.whale_trades_count == 1
    assert len(analytics.whale_alerts) == 1
    assert analytics.whale_alerts[0].value_usd == 7500.0

def test_buy_sell_pressure_gauge():
    analytics = MarketAnalytics(sol_price_usd=150.0)
    
    t_buy = TradeEvent(
        signature="s1", timestamp=datetime.now(), dex="Orca",
        token_in="SOL", token_out="USDC", amount_in=10, amount_out=1500,
        value_usd=1500.0, tx_type="BUY", trader="u1"
    )
    t_sell = TradeEvent(
        signature="s2", timestamp=datetime.now(), dex="Orca",
        token_in="USDC", token_out="SOL", amount_in=500, amount_out=3.3,
        value_usd=500.0, tx_type="SELL", trader="u2"
    )
    analytics.register_trade(t_buy)
    analytics.register_trade(t_sell)
    
    buy_pct, sell_pct = analytics.get_buy_sell_ratio()
    assert round(buy_pct, 1) == 75.0
    assert round(sell_pct, 1) == 25.0

def test_pool_creation():
    analytics = MarketAnalytics()
    pool = PoolCreationEvent(
        signature="sig_pool",
        timestamp=datetime.now(),
        dex="Meteora DBC",
        token_a="NEWCOIN",
        token_b="SOL",
        initial_liquidity_usd=25000.0,
        pool_address="pool_addr_123",
        creator="creator_123"
    )
    analytics.register_pool_creation(pool)
    assert len(analytics.new_pools) == 1
    assert analytics.new_pools[0].initial_liquidity_usd == 25000.0

if __name__ == "__main__":
    test_trade_registration()
    test_whale_detection()
    test_buy_sell_pressure_gauge()
    test_pool_creation()
    print("✅ All Solami Sentinel unit tests passed successfully!")
