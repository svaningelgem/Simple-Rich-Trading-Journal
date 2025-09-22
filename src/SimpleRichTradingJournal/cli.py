import click
from pathlib import Path
from datetime import datetime
from logprise import logger
from sqlalchemy import text
from ..config.loader import load_config
from ..config.models import Config
from ..storage.repository import SQLAlchemyRepository
from ..storage.models import Trade
from ..core.calc import Calc
import pickle  # For legacy migration only

@click.group()
def cli():
    """SRTJ CLI."""
    pass

@cli.command()
@click.option("--config", default="config.yaml")
def run(config: str):
    """Run the application."""
    cfg = load_config(Path(config))
    logger.configure(
        handlers=[{"sink": "srtj.log", "rotation": f"{cfg.logging.rotation_mb} MB", "retention": f"{cfg.logging.retention_days} days"}]
    )
    from .main import run_app
    run_app(cfg)

@cli.command()
@click.option("--config", default="config.yaml")
@click.option("--from-profile", default=None, help="Profile to migrate from")
def migrate(config: str, from_profile: Optional[str]):
    """Migrate pickle to SQLAlchemy DB."""
    cfg = load_config(Path(config))
    logger.configure(...)  # Same as above
    repo = SQLAlchemyRepository(cfg)
    profiles_home = Path.home() / cfg.profiles.home_folder
    journal_path = profiles_home / (from_profile or "") / "journal.pkl"
    history_path = profiles_home / (from_profile or "") / "history.pkl"

    if not journal_path.exists():
        logger.info("migration/skip: no pickle found")
        return

    # Load pickle legacy
    with open(journal_path, "rb") as f:
        trades_data = pickle.load(f)
    with open(history_path, "rb") as f:
        history_data = pickle.load(f)

    # Transform to Trade
    trades = []
    for data in trades_data:
        try:
            trade = Trade(
                invest_time=datetime_from_tradetimeformat(data.get("InvestTime", "")),
                invest_amount=data.get("InvestAmount"),
                # Map all fields...
                cat=data.get("cat", "")
            )
            trades.append(trade)
        except ValueError:
            logger.warning("migration/skip-invalid: {}", data)

    # Check idempotent
    current_count, _ = repo.query_trades()
    if current_count > 0:
        logger.info("migration/skip: DB not empty")
        return

    # Bulk add
    for trade in trades:
        repo.add_trade(trade)

    # History: Save as JSON
    for hid, hdata in history_data.items():
        repo.save_history([Trade(**td) for td in hdata["data"]], hdata["time"])

    # Backup and delete pickle
    trash = profiles_home / "trash"
    trash.mkdir(exist_ok=True)
    journal_path.rename(trash / journal_path.name)
    logger.info("migration/done: {} trades", len(trades))

@cli.command()
@click.option("--config", default="config.yaml")
def demo(config: str):
    """Initialize demo data and run app."""
    cfg = load_config(Path(config))
    logger.configure(...)  # Same
    repo = SQLAlchemyRepository(cfg)

    # Create tables if needed (already in init)

    # Demo SQL inserts (embedded; could load from init_demo.sql)
    session = repo._get_session()
    try:
        # Sample trades: deposits, payouts, open/fin
        demo_sql = """
                   INSERT INTO trades (invest_time, invest_amount, name, symbol, cat) VALUES
                                                                                          ('2023-01-01 00:00:00', 1000.0, 'Deposit', '', 'd'),
                                                                                          ('2023-02-01 00:00:00', -500.0, 'Payout', '', 'p'),
                                                                                          ('2023-03-01 00:00:00', 200.0, 'AAPL', 'AAPL', 'to'),
                                                                                          ('2023-04-01 00:00:00', 250.0, 'AAPL', 'AAPL', 'tf');  -- Closed trade \
                   """
        session.execute(text(demo_sql))
        session.commit()

        # History entry
        now = datetime.now()
        demo_trades = repo.load_journal()  # After inserts
        repo.save_history(demo_trades, now)

        logger.info("demo/init: 4 sample trades added")
    finally:
        session.close()

    # Run app
    from .main import run_app
    run_app(cfg)

if __name__ == "__main__":
    cli()