from pathlib import Path
import os
import yaml

def load_config(path: str | Path | None = None):
    p = Path(path or Path(__file__).resolve().parents[2] / 'config' / 'app.yaml')
    if not p.exists():
        p = Path(__file__).resolve().parents[1] / 'config' / 'app.yaml'
    if not p.exists(): raise RuntimeError(f'Missing config file: {p}')
    data = yaml.safe_load(p.read_text()) or {}
    class Config: pass
    c = Config()
    app_data = data.get('app', {})
    c.app_name = app_data.get('name', 'GptAPP')
    c.currency_name = app_data.get('currency_name', 'Study Coins')
    c.database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/gptapp')
    c.backend_base_url = data.get('backend', {}).get('base_url', 'http://localhost:8000')
    diff_data = data.get('difficulty', {})
    c.target_min_accuracy = float(diff_data.get('target_min_accuracy', 0.70))
    c.target_max_accuracy = float(diff_data.get('target_max_accuracy', 0.80))
    decay_data = data.get('decay', {})
    c.decay_rate_percent = float(decay_data.get('rate_percent', 2.0))
    c.decay_frequency_hours = int(decay_data.get('frequency_hours', 24))
    boss_data = data.get('boss_battle', {})
    c.boss_time_per_turn_seconds = int(boss_data.get('default_time_per_turn_seconds', 15))
    c.boss_entry_cost = float(boss_data.get('entry_cost', 25))
    c.boss_hp = float(boss_data.get('hp', 100))
    c.boss_unlock_min_attempts = int(boss_data.get('unlock_min_attempts', 10))
    nudge_data = data.get('nudge', {})
    c.quiet_start = nudge_data.get('quiet_start', '22:00')
    c.quiet_end = nudge_data.get('quiet_end', '06:00')
    c.llm = data.get('llm', {})
    c.branding = data.get('branding', {})
    return c
