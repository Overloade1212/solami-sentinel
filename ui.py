"""
Terminal User Interface for Solami Sentinel
Constructs real-time interactive panels, tables, and gauges using Rich.
"""

from datetime import datetime
from rich.align import Align
from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from analytics import MarketAnalytics
from config import SentinelConfig

class SentinelUI:
    def __init__(self, config: SentinelConfig, analytics: MarketAnalytics):
        self.config = config
        self.analytics = analytics
        self.console = Console()

    def generate_layout(self, feed_name: str, is_connected: bool) -> Layout:
        layout = Layout(name="root")
        
        # Split into Header (size 4), Body (ratio 1), Footer (size 3)
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3),
        )
        
        # Split body into Left (Live Swaps, ratio 6) and Right (Whales & Gauges, ratio 5)
        layout["body"].split_row(
            Layout(name="left", ratio=6),
            Layout(name="right", ratio=5),
        )
        
        # Split right into Whales (ratio 5), Sentiment Gauge (size 6), New Pools (ratio 4)
        layout["right"].split_column(
            Layout(name="whales", ratio=5),
            Layout(name="sentiment", size=6),
            Layout(name="pools", ratio=4),
        )
        
        # Populate each layout section
        layout["header"].update(self._render_header(feed_name, is_connected))
        layout["left"].update(self._render_live_swaps())
        layout["whales"].update(self._render_whale_radar())
        layout["sentiment"].update(self._render_sentiment_gauge())
        layout["pools"].update(self._render_new_pools())
        layout["footer"].update(self._render_footer())
        
        return layout

    def _render_header(self, feed_name: str, is_connected: bool) -> Panel:
        status_dot = "🟢" if is_connected else "🔴"
        status_text = "CONNECTED" if is_connected else "RECONNECTING"
        
        buy_pct, sell_pct = self.analytics.get_buy_sell_ratio()
        net_sol = self.analytics.get_net_sol_flow()
        net_sol_str = f"+{net_sol:.1f} SOL" if net_sol >= 0 else f"{net_sol:.1f} SOL"
        net_color = "bold green" if net_sol >= 0 else "bold red"
        
        title_text = Text.from_markup(
            f"⚡ [bold cyan]SOLAMI SENTINEL[/bold cyan] [white]v1.0.0[/white] │ "
            f"Feed: [bold magenta]{feed_name}[/bold magenta] │ "
            f"Status: {status_dot} [bold green]{status_text}[/bold green]\n"
            f"[dim]Live Solana Mainnet DEX Firehose & Real-Time Liquidity Radar[/dim]"
        )
        
        stats_text = Text.from_markup(
            f"[bold white]SOL Price:[/bold white] [bold yellow]${self.analytics.sol_price_usd:.2f}[/bold yellow] │ "
            f"[bold white]Vol Monitored:[/bold white] [bold green]{self.analytics.format_usd(self.analytics.total_volume_usd)}[/bold green] │ "
            f"[bold white]Swaps:[/bold white] [cyan]{self.analytics.total_trades}[/cyan] │ "
            f"[bold white]Whale Alerts:[/bold white] [bold red]{self.analytics.whale_trades_count}[/bold red] │ "
            f"[bold white]Net Flow:[/bold white] [{net_color}]{net_sol_str}[/{net_color}]"
        )
        
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)
        grid.add_row(title_text, stats_text)
        
        return Panel(grid, style="cyan", border_style="bold blue")

    def _render_live_swaps(self) -> Panel:
        table = Table(expand=True, box=None, padding=(0, 1), show_edge=False)
        table.add_column("Time", style="dim", width=8)
        table.add_column("DEX", style="cyan", width=14)
        table.add_column("Pair", style="white", width=11)
        table.add_column("Type", width=6)
        table.add_column("Value USD", justify="right", width=11)
        table.add_column("Size", justify="right", width=10)
        table.add_column("Alert", justify="center", width=8)
        table.add_column("TX", style="dim", width=10)
        
        for trade in list(self.analytics.recent_trades)[:18]:
            time_str = trade.timestamp.strftime("%H:%M:%S")
            pair = f"{trade.token_in}→{trade.token_out}"
            
            if trade.tx_type == "BUY":
                type_style = "[bold green]BUY [/bold green]"
                val_style = f"[green]{self.analytics.format_usd(trade.value_usd)}[/green]"
            else:
                type_style = "[bold red]SELL[/bold red]"
                val_style = f"[red]{self.analytics.format_usd(trade.value_usd)}[/red]"
                
            if trade.is_mega_whale:
                alert = "[bold magenta]🚨 MEGA[/bold magenta]"
            elif trade.is_whale:
                alert = "[bold yellow]🐋 WHALE[/bold yellow]"
            else:
                alert = "[dim]•[/dim]"
                
            size_str = f"{trade.amount_in:.1f}" if trade.tx_type == "BUY" else f"{trade.amount_out:.1f}"
            tx_short = self.analytics.truncate_address(trade.signature, 4, 3)
            
            table.add_row(time_str, trade.dex, pair, type_style, val_style, size_str, alert, tx_short)
            
        return Panel(table, title="[bold white]📡 Live DEX Trades Stream (Solami Blur / Yellowstone)[/bold white]", border_style="cyan")

    def _render_whale_radar(self) -> Panel:
        table = Table(expand=True, box=None, padding=(0, 1), show_edge=False)
        table.add_column("Time", style="dim", width=8)
        table.add_column("DEX", style="cyan", width=13)
        table.add_column("Action", width=12)
        table.add_column("Amount", justify="right", width=11)
        table.add_column("Trader", style="dim", width=11)
        
        for whale in list(self.analytics.whale_alerts)[:7]:
            time_str = whale.timestamp.strftime("%H:%M:%S")
            action = f"[bold green]BUY[/bold green] {whale.token_out}" if whale.tx_type == "BUY" else f"[bold red]SELL[/bold red] {whale.token_in}"
            val_style = f"[bold yellow]{self.analytics.format_usd(whale.value_usd)}[/bold yellow]"
            trader_short = self.analytics.truncate_address(whale.trader, 4, 3)
            
            table.add_row(time_str, whale.dex, action, val_style, trader_short)
            
        return Panel(table, title="[bold red]🐋 Whale Radar & Large Liquidity Swaps (>= $5,000)[/bold red]", border_style="red")

    def _render_sentiment_gauge(self) -> Panel:
        buy_pct, sell_pct = self.analytics.get_buy_sell_ratio()
        
        bar_width = 30
        buy_blocks = int((buy_pct / 100.0) * bar_width)
        sell_blocks = bar_width - buy_blocks
        
        bar = f"[green]{'█' * buy_blocks}[/green][red]{'█' * sell_blocks}[/red]"
        
        text = Text.from_markup(
            f"[bold green]Buy Volume: {buy_pct:.1f}%[/bold green]  │  [bold red]Sell Volume: {sell_pct:.1f}%[/bold red]\n"
            f"[{bar}]\n"
            f"[dim]Net Flow Pressure: {'Bullish Inflow' if buy_pct >= sell_pct else 'Bearish Distribution'}[/dim]"
        )
        return Panel(Align.center(text), title="[bold yellow]⚖️ Buy vs Sell Pressure (Real-time Flow)[/bold yellow]", border_style="yellow")

    def _render_new_pools(self) -> Panel:
        table = Table(expand=True, box=None, padding=(0, 1), show_edge=False)
        table.add_column("Time", style="dim", width=8)
        table.add_column("DEX / Platform", style="magenta", width=14)
        table.add_column("Pair", style="white", width=11)
        table.add_column("Initial Liq", justify="right", width=11)
        table.add_column("Pool Address", style="dim", width=11)
        
        for pool in list(self.analytics.new_pools)[:5]:
            time_str = pool.timestamp.strftime("%H:%M:%S")
            pair = f"{pool.token_a}/{pool.token_b}"
            liq_str = f"[bold green]{self.analytics.format_usd(pool.initial_liquidity_usd)}[/bold green]"
            addr_short = self.analytics.truncate_address(pool.pool_address, 4, 3)
            table.add_row(time_str, pool.dex, pair, liq_str, addr_short)
            
        return Panel(table, title="[bold magenta]🌱 New Liquidity Pools & Meteora DBC Launches[/bold magenta]", border_style="magenta")

    def _render_footer(self) -> Panel:
        footer_text = Text.from_markup(
            "[dim]Keys: [bold white]Ctrl+C[/bold white] Exit │ "
            "[bold white]r[/bold white] Reconnect │ "
            "[bold white]w[/bold white] Adjust Whale Filter │ "
            "Developer: [bold cyan]Anatoli Kolotovkin (@Overloade1212)[/bold cyan] │ "
            "Built for [bold magenta]Colosseum Crypto World's Fair — Solami Sidetrack[/bold magenta][/dim]"
        )
        return Panel(Align.center(footer_text), style="dim", border_style="dim")
