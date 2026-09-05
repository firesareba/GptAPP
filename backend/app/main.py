import io
import re
from datetime import datetime, timedelta
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from .config import load_config
from .models import Base, User, Topic, Material, Problem, Attempt, UserTopicMastery, UserWallet, WalletTransaction, BossBattle

cfg = load_config()
engine = create_async_engine(cfg.database_url, pool_pre_ping=True)
Session = async_sessionmaker(engine, expire_on_commit=False)
app = FastAPI(title=cfg.app_name)

class Generation(BaseModel):
    user_id: str
    material_id: int|None = None
    topic: str
    difficulty: float = Field(ge=0, le=1)
    raw_llm_response: dict
    battle_id: int|None = None

class AttemptIn(BaseModel):
    user_id: str
    problem_id: int
    submitted_answer: str
    elapsed_ms: int = Field(ge=0)
    battle_id: int|None = None

def normalize(value: str) -> str:
    return re.sub(r'\s+', ' ', value.strip().casefold())

def verified_correct(problem: Problem, answer: str) -> bool:
    return normalize(problem.answer_key) == normalize(answer)

def target_difficulty(m: UserTopicMastery) -> float:
    # Keep users near the configured 70-80% accuracy band.
    if m.attempts >= 3 and m.rolling_accuracy > cfg.target_max_accuracy:
        return min(1.0, m.difficulty + 0.08)
    if m.attempts >= 3 and m.rolling_accuracy < cfg.target_min_accuracy:
        return max(0.0, m.difficulty - 0.08)
    return m.difficulty

def payout(difficulty: float) -> float:
    # Easy questions remain low-value; harder calibrated questions are worth more.
    return round(1.0 + 9.0 * max(0.0, min(1.0, difficulty)), 2)

def multiplier() -> float:
    # Hidden variable-ratio reward table. Odds are deliberately not exposed by API.
    import random
    roll = random.random()
    if roll < 0.01: return 10.0
    if roll < 0.04: return 5.0
    if roll < 0.12: return 3.0
    if roll < 0.30: return 2.0
    return 1.0

async def get_user(db, external_id: str):
    r = await db.execute(select(User).where(User.external_id == external_id))
    u = r.scalar_one_or_none()
    if not u:
        u = User(external_id=external_id); db.add(u); await db.flush()
    return u

async def wallet(db, user_id: int):
    r = await db.execute(select(UserWallet).where(UserWallet.user_id == user_id))
    w = r.scalar_one_or_none()
    if not w:
        w = UserWallet(user_id=user_id, balance=0); db.add(w); await db.flush()
    return w

@app.on_event('startup')
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get('/health')
async def health(): return {'ok': True, 'app': cfg.app_name}

@app.post('/materials/text')
async def text_material(user_id: str, text: str, filename: str = 'pasted-text'):
    if not text.strip(): raise HTTPException(400, 'Text is empty')
    async with Session() as db:
        u = await get_user(db, user_id); m = Material(user_id=u.id, filename=filename, source_text=text); db.add(m); await db.commit(); await db.refresh(m)
        return {'id': m.id, 'filename': m.filename}

@app.post('/materials/pdf')
async def pdf_material(user_id: str, file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'): raise HTTPException(415, 'Only PDF files are accepted')
    try: text = '\n\n'.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(await file.read())).pages).strip()
    except Exception as e: raise HTTPException(400, 'PDF could not be read') from e
    if not text: raise HTTPException(422, 'This PDF has no extractable text layer. OCR is not supported.')
    async with Session() as db:
        u = await get_user(db, user_id); m = Material(user_id=u.id, filename=file.filename, source_text=text); db.add(m); await db.commit(); await db.refresh(m)
        return {'id': m.id, 'filename': m.filename, 'characters': len(text)}

@app.get('/topics')
async def topics(user_id: str):
    async with Session() as db:
        u = await get_user(db, user_id)
        rows = (await db.execute(select(Topic).where(Topic.user_id == u.id).order_by(Topic.name))).scalars().all()
        result = []
        for t in rows:
            m = (await db.execute(select(UserTopicMastery).where(UserTopicMastery.user_id == u.id, UserTopicMastery.topic_id == t.id))).scalar_one_or_none()
            result.append({'id': t.id, 'name': t.name, 'accuracy': m.rolling_accuracy if m else 0.75, 'difficulty': m.difficulty if m else 0.5, 'attempts': m.attempts if m else 0})
        return result

@app.get('/wallet')
async def get_wallet(user_id: str):
    async with Session() as db:
        u = await get_user(db, user_id); w = await wallet(db, u.id); await db.commit()
        return {'balance': round(w.balance, 2)}

@app.post('/problems/generation')
async def generation(p: Generation):
    raw = p.raw_llm_response
    if not {'prompt', 'answer', 'type'}.issubset(raw): raise HTTPException(422, 'LLM response is missing required fields')
    if str(raw['type']) not in {'multiple_choice', 'numeric', 'short_answer'}: raise HTTPException(422, 'Unsupported problem type')
    async with Session() as db:
        u = await get_user(db, p.user_id)
        t = (await db.execute(select(Topic).where(Topic.user_id == u.id, Topic.name == p.topic))).scalar_one_or_none()
        if not t: t = Topic(user_id=u.id, name=p.topic); db.add(t); await db.flush()
        m = (await db.execute(select(UserTopicMastery).where(UserTopicMastery.user_id == u.id, UserTopicMastery.topic_id == t.id))).scalar_one_or_none()
        if not m: m = UserTopicMastery(user_id=u.id, topic_id=t.id, difficulty=p.difficulty); db.add(m); await db.flush()
        expected = target_difficulty(m)
        # Permit small client/rounding drift, but reject requests that intentionally force an easier target.
        if abs(p.difficulty - expected) > 0.16: raise HTTPException(409, 'Requested difficulty is outside the adaptive target')
        if p.battle_id is not None:
            b = (await db.execute(select(BossBattle).where(BossBattle.id == p.battle_id, BossBattle.user_id == u.id, BossBattle.outcome.is_(None)))).scalar_one_or_none()
            if not b: raise HTTPException(404, 'Active boss battle not found')
            p.difficulty = min(1.0, max(p.difficulty, expected + 0.05))
        problem = Problem(user_id=u.id, topic_id=t.id, material_id=p.material_id, prompt=str(raw['prompt']), problem_type=str(raw['type']), difficulty=p.difficulty, answer_key=str(raw['answer']), metadata_json={k:v for k,v in raw.items() if k not in {'prompt','answer','type'}})
        db.add(problem); await db.commit(); await db.refresh(problem)
        return {'id': problem.id, 'topic': t.name, 'prompt': problem.prompt, 'type': problem.problem_type, 'difficulty': problem.difficulty}

@app.get('/problems/{problem_id}')
async def problem(problem_id: int, user_id: str):
    async with Session() as db:
        u = await get_user(db, user_id); row = (await db.execute(select(Problem, Topic).join(Topic, Problem.topic_id == Topic.id).where(Problem.id == problem_id, Problem.user_id == u.id))).first()
        if not row: raise HTTPException(404, 'Problem not found')
        p, t = row; return {'id': p.id, 'topic': t.name, 'prompt': p.prompt, 'type': p.problem_type, 'difficulty': p.difficulty}

@app.post('/attempts')
async def attempt(a: AttemptIn):
    async with Session() as db:
        u = await get_user(db, a.user_id); p = (await db.execute(select(Problem).where(Problem.id == a.problem_id, Problem.user_id == u.id))).scalar_one_or_none()
        if not p: raise HTTPException(404, 'Problem not found')
        battle = None
        if a.battle_id is not None:
            battle = (await db.execute(select(BossBattle).where(BossBattle.id == a.battle_id, BossBattle.user_id == u.id, BossBattle.outcome.is_(None)))).scalar_one_or_none()
            if not battle or battle.topic_id != p.topic_id: raise HTTPException(409, 'Invalid active boss battle')
        correct = verified_correct(p, a.submitted_answer)
        db.add(Attempt(user_id=u.id, problem_id=p.id, submitted_answer=a.submitted_answer, correct=correct, grading_evidence={'method':'server_exact_match'}, elapsed_ms=a.elapsed_ms, battle_id=a.battle_id))
        m = (await db.execute(select(UserTopicMastery).where(UserTopicMastery.user_id == u.id, UserTopicMastery.topic_id == p.topic_id))).scalar_one_or_none()
        if not m: m = UserTopicMastery(user_id=u.id, topic_id=p.topic_id); db.add(m); await db.flush()
        old_n = m.attempts; m.attempts += 1; m.rolling_accuracy = ((m.rolling_accuracy * old_n) + int(correct)) / m.attempts; m.difficulty = target_difficulty(m); m.last_attempt_at = datetime.utcnow()
        w = await wallet(db, u.id)
        earned = 0.0; mult = 1.0; damage = 0.0; outcome = None
        if correct:
            mult = multiplier(); earned = round(payout(p.difficulty) * mult, 2); w.balance += earned
            db.add(WalletTransaction(user_id=u.id, amount=earned, reason='correct_answer', metadata_json={'difficulty':p.difficulty,'multiplier':mult}))
        if battle:
            turn_limit = cfg.boss_time_per_turn_seconds * 1000
            speed = max(0.0, min(1.0, 1.0 - (a.elapsed_ms / turn_limit))) if turn_limit else 0.0
            damage = round((8.0 + 22.0 * speed) if correct else 0.0, 2)
            battle.boss_hp = max(0.0, battle.boss_hp - damage)
            battle.damage_log = list(battle.damage_log or []) + [{'problem_id':p.id,'correct':correct,'elapsed_ms':a.elapsed_ms,'damage':damage}]
            if battle.boss_hp <= 0:
                battle.outcome = 'win'; battle.finished_at = datetime.utcnow(); bonus = round(40.0 + 20.0 * multiplier(), 2); w.balance += bonus; battle.reward_granted = earned + bonus
                db.add(WalletTransaction(user_id=u.id, amount=bonus, reason='boss_win', metadata_json={'battle_id':battle.id}))
                outcome = 'win'
        await db.commit()
        return {'correct':correct,'recorded':True,'coins_earned':earned,'multiplier':mult,'wallet_balance':round(w.balance,2),'battle_damage':damage,'boss_hp':battle.boss_hp if battle else None,'battle_outcome':outcome}

@app.post('/boss/start')
async def boss_start(user_id: str, topic_id: int):
    async with Session() as db:
        u = await get_user(db, user_id); t = (await db.execute(select(Topic).where(Topic.id == topic_id, Topic.user_id == u.id))).scalar_one_or_none()
        if not t: raise HTTPException(404, 'Topic not found')
        m = (await db.execute(select(UserTopicMastery).where(UserTopicMastery.user_id == u.id, UserTopicMastery.topic_id == t.id))).scalar_one_or_none()
        if not m or m.attempts < cfg.boss_unlock_min_attempts: raise HTTPException(403, 'Boss battle is not unlocked for this topic')
        w = await wallet(db, u.id)
        if w.balance < cfg.boss_entry_cost: raise HTTPException(402, 'Not enough coins')
        active = (await db.execute(select(BossBattle).where(BossBattle.user_id == u.id, BossBattle.outcome.is_(None)))).scalar_one_or_none()
        if active: raise HTTPException(409, 'Finish the active boss battle first')
        w.balance -= cfg.boss_entry_cost; db.add(WalletTransaction(user_id=u.id, amount=-cfg.boss_entry_cost, reason='boss_entry', metadata_json={'topic_id':topic_id}))
        b = BossBattle(user_id=u.id, topic_id=t.id, boss_hp=cfg.boss_hp, entry_cost=cfg.boss_entry_cost); db.add(b); await db.commit(); await db.refresh(b)
        return {'id':b.id,'topic_id':t.id,'boss_hp':b.boss_hp,'time_per_turn_seconds':cfg.boss_time_per_turn_seconds,'wallet_balance':round(w.balance,2)}

@app.get('/boss/{battle_id}')
async def boss_get(battle_id: int, user_id: str):
    async with Session() as db:
        u = await get_user(db, user_id); b = (await db.execute(select(BossBattle).where(BossBattle.id == battle_id, BossBattle.user_id == u.id))).scalar_one_or_none()
        if not b: raise HTTPException(404, 'Boss battle not found')
        return {'id':b.id,'topic_id':b.topic_id,'boss_hp':b.boss_hp,'outcome':b.outcome,'damage_log':b.damage_log,'reward_granted':b.reward_granted,'recap_text':b.recap_text}

@app.post('/boss/{battle_id}/recap')
async def boss_recap(battle_id: int, user_id: str, recap_text: str):
    async with Session() as db:
        u = await get_user(db, user_id); b = (await db.execute(select(BossBattle).where(BossBattle.id == battle_id, BossBattle.user_id == u.id))).scalar_one_or_none()
        if not b: raise HTTPException(404, 'Boss battle not found')
        if b.outcome != 'win': raise HTTPException(409, 'Recap is only available after a win')
        b.recap_text = recap_text[:4000]; await db.commit(); return {'saved':True}
