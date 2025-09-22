import click
from pathlib import Path
from datetime import datetime
from logprise import logger
import pickle
from ..config.loader import load_config
from ..config.models import Config
from ..storage.repository import SQLAlchemyRepository
from ..storage.models import Trade
from ..core.utils import datetime_from_tradetimeformat
from ..main import run_app

@click.group()
def cli():
    pass

@cli.command()
@click.option("--config", "config_path", default="config.yaml")
def run(config_path: str):
    cfg = load_config(Path(config_path))
    logger.configure(handlers=[{"sink": "srtj.log", "rotation": f"{cfg.logging.rotation_mb} MB", "retention": f"{cfg.logging.retention_days} days"}])
    run_app(cfg)

@cli.command()
@click.option("--config", "config_path", default="config.yaml")
def migrate(config_path: str):
    cfg = load_config(Path(config_path))
    logger.configure(handlers=[{"sink": "srtj.log", "rotation": f"{cfg.logging.rotation_mb} MB", "retention": f"{cfg.logging.retention_days} days"}])
    repo = SQLAlchemyRepository(cfg)
    profiles_home = Path.home() / cfg.profiles.home_folder
    journal_path = profiles_home / "journal.pkl"
    history_path = profiles_home / "history.pkl"

    if not journal_path.exists():
        logger.info("migration/skip: pickle not found")
        return

    with open(journal_path, "rb") as f:
        journal_data = pickle.load(f)
    with open(history_path, "rb") as f:
        history_data = pickle.load(f)

    # Transform trades
    trades = []
    for data in journal_data:
        try:
            trade = Trade(
                cat=data.get("cat", ""),
                mark=data.get("mark", 0),
                name=data.get("Name", ""),
                symbol=data.get("Symbol", ""),
                isin=data.get("ISIN", ""),
                type=data.get("Type", ""),
                short=bool(data.get("Short", False)),
                sector=data.get("Sector", ""),
                category=data.get("Category", ""),
                rating=data.get("Rating"),
                n=data.get("n", 0),
                invest_time=data.get("InvestTime", ""),
                invest_amount=data.get("InvestAmount", 0),
                invest_course=data.get("InvestCourse", 0),
                take_time=data.get("TakeTime", ""),
                take_amount=data.get("TakeAmount"),
                take_course=data.get("TakeCourse"),
                itc=data.get("ITC"),
                dividend=bool(data.get("Dividend", False)),
                note=data.get("Note", ""),
                hypotheses=data.get("Hypotheses", "")
            )
            trades.append(trade)
        except Exception as e:
            logger.warning("migration/invalid-trade: {} - {}", data, e)

    # Idempotent check
    _, db_count = repo.query_trades(per_page=0)
    if db_count > 0:
        logger.info("migration/skip: DB populated")
        return

    # Bulk add
    for trade in trades:
        repo.add_trade(trade)

    # History
    for hid, hdata in history_data.items():
        ts = datetime.fromtimestamp(hdata["time"])
        h_trades = [Trade(**td) for td in hdata["data"]]
        repo.save_history(h_trades, ts)

    # Backup
    trash = profiles_home / "trash"
    trash.mkdir(exist_ok=True)
    journal_path.replace(trash / journal_path.name)
    history_path.replace(trash / history_path.name)
    logger.info("migration/complete: {} trades", len(trades))

@cli.command()
@click.option("--config", "config_path", default="config.yaml")
def demo(config_path: str):
    cfg = load_config(Path(config_path))
    logger.configure(handlers=[{"sink": "srtj.log", "rotation": f"{cfg.logging.rotation_mb} MB", "retention": f"{cfg.logging.retention_days} days"}])
    repo = SQLAlchemyRepository(cfg)

    session = repo._get_session()
    try:
        demo_sql = """
                   INSERT INTO trades (cat, name, symbol, invest_time, invest_amount, n) VALUES
                                                                                             ('d', 'Initial Deposit', '', '2023-01-01 09:00:00', 10000.0, 1),
                                                                                             ('to', 'AAPL Open', 'AAPL', '2023-02-01 10:00:00', 5000.0, 10),
                                                                                             ('tf', 'AAPL Close', 'AAPL', '2023-02-01 10:00:00', 5500.0, 10),
                                                                                             ('p', 'Payout', '', '2023-03-01 11:00:00', -2000.0, 1),
                                                                                             ('v', 'Dividend', 'AAPL', '2023-04-01 12:00:00', 100.0, 1),
                                                                                             ('i', 'ITC', '', '2023-05-01 13:00:00', -50.0, 1); \
                   """
        session.execute(text(demo_sql))
        session.commit()

        trades = repo.load_journal()
        now = datetime.now()
        repo.save_history(trades, now)

        logger.info("demo/init: added sample data")
    except Exception as e:
        logger.error("demo/fail: {}", e)
    finally:
        session.close()

    run_app(cfg)

if __name__ == "__main__":
    cli()