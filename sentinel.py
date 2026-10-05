#!/usr/bin/env python3
"""
Solami Sentinel — Main CLI Application
Autonomous real-time Solana DEX & Whale Radar powered by Solami infrastructure.
"""

import argparse
import asyncio
import os
import signal
import sys
from datetime import datetime
from rich.console import Console
from rich.live import Live

from analytics import MarketAnalytics
from config import SentinelConfig
from solami_feed import SolamiFeed
from ui import SentinelUI

def parse_args():
    parser = argparse.ArgumentParser(
        description="⚡ Solami Sentinel: Real-Time Solana DEX & Whale Radar"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        default=True,
        help="Run in high-frequency demo mode with simulated Solana mainnet replay (Default: True)"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Connect directly to live Solana WebSocket / Solami endpoint"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("SOLAMI_API_KEY"),
        help="Solami Pro API key (get free 7-day Pro at solami.dev)"
    )
    parser.add_argument(
        "--min-whale",
        type=float,
        default=5000.0,
        help="Whale alert threshold in USD (Default: $5,000)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="Run for N seconds then exit automatically (0 = run indefinitely)"
    )
    return parser.parse_args()

async def main():
    args = parse_args()
    
    # Configure environment
    demo_mode = args.demo if not args.live else False
    config = SentinelConfig(
        api_key=args.api_key,
        whale_threshold_usd=args.min_whale,
        demo_mode=demo_mode
    )
    
    analytics = MarketAnalytics(sol_price_usd=config.sol_price_usd)
    feed = SolamiFeed(config, analytics)
    ui = SentinelUI(config, analytics)
    
    console = Console()
    
    # Start background feed task
    feed_task = asyncio.create_task(feed.start())
    
    # Run interactive Live UI
    start_time = asyncio.get_event_loop().time()
    try:
        with Live(
            ui.generate_layout(feed.feed_type, feed.is_connected),
            console=console,
            refresh_per_second=4,
            screen=True
        ) as live:
            while True:
                live.update(ui.generate_layout(feed.feed_type, feed.is_connected))
                await asyncio.sleep(0.25)
                
                # Check optional duration limit
                if args.duration > 0:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed >= args.duration:
                        break
                        
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        feed.stop()
        feed_task.cancel()
        console.clear()
        console.print("[bold green]✨ Solami Sentinel session ended cleanly.[/bold green]")
        console.print(f"Total Swaps Monitored: [cyan]{analytics.total_trades}[/cyan]")
        console.print(f"Total Monitored Volume: [green]{analytics.format_usd(analytics.total_volume_usd)}[/green]")
        console.print(f"Whale Alerts Detected: [red]{analytics.whale_trades_count}[/red]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
