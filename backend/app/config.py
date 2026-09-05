from pathlib import Path
import os
import yaml

def load_config(path: str | Path | None = None):
    p = Path(path or Path(__file__).resolve().parents[2] / 'config' / 'app.yaml')
    if not p.exists():
        p = Path(__file__).resolve().parents[1] / 'config' / 'app.yaml'
    if not p.exists(): raise RuntimeError(f'Missing config file: {p}')
    data = yaml.safe_load(p.read_text())
    class Config: pass
    c = Config()
    c.app_name = data['app']['name']; c.currency_name = data['app']['currency_name']
    c.database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/gptapp')
    c.backend_base_url = data['backend']['base_url']
    c.target_min_accuracy = float(data['difficulty']['target_min_accuracy']); c.target_max_accuracy = float(data['difficulty']['target_max_accuracy'])
    c.decay_rate_percent = float(data['decay']['rate_percent']); c.decay_frequency_hours = int(data['decay']['frequency_hours'])
    c.boss_time_per_turn_seconds = int(data['boss_battle']['default_time_per_turn_seconds'])
    c.boss_entry_cost = float(data['boss_battle']['entry_cost']); c.boss_hp = float(data['boss_battle']['hp']); c.boss_unlock_min_attempts = int(data['boss_battle']['unlock_min_attempts'])
    c.quiet_start = data['nudge']['quiet_start']; c.quiet_end = data['nudge']['quiet_end']
    c.llm = data['llm']; c.branding = data['branding']
    return c
