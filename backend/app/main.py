import io
import re
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from .config import load_config
from .models import Base, User, Topic, Material, Problem, Attempt, UserTopicMastery

cfg = load_config(); engine = create_async_engine(cfg.database_url, pool_pre_ping=True); Session = async_sessionmaker(engine, expire_on_commit=False)
app = FastAPI(title=cfg.app_name)

class Generation(BaseModel):
    user_id: str; material_id: int|None = None; topic: str; difficulty: float = Field(ge=0, le=1); raw_llm_response: dict
class AttemptIn(BaseModel):
    user_id: str; problem_id: int; submitted_answer: str; elapsed_ms: int = Field(ge=0)

@app.on_event('startup')
async def startup():
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)

async def user_for(db, external_id):
    r = await db.execute(select(User).where(User.external_id == external_id)); u = r.scalar_one_or_none()
    if not u: u = User(external_id=external_id); db.add(u); await db.flush()
    return u

def normalize(value: str) -> str: return re.sub(r'\s+', ' ', value.strip().casefold())

def verified_correct(problem: Problem, answer: str) -> bool:
    # Phase 1 deliberately uses server-side deterministic verification. This prevents a client from forging an LLM grading boolean.
    return normalize(problem.answer_key) == normalize(answer)

@app.get('/health')
async def health(): return {'ok': True, 'app': cfg.app_name}

@app.post('/materials/text')
async def text_material(user_id: str, text: str, filename: str = 'pasted-text'):
    if not text.strip(): raise HTTPException(400, 'Text is empty')
    async with Session() as db:
        u = await user_for(db, user_id); m = Material(user_id=u.id, filename=filename, source_text=text); db.add(m); await db.commit(); await db.refresh(m); return {'id':m.id,'filename':m.filename}

@app.post('/materials/pdf')
async def pdf_material(user_id: str, file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'): raise HTTPException(415, 'Only PDF files are accepted')
    try: text = '\n\n'.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(await file.read())).pages).strip()
    except Exception as e: raise HTTPException(400, 'PDF could not be read') from e
    if not text: raise HTTPException(422, 'This PDF has no extractable text layer. OCR is not supported.')
    async with Session() as db:
        u = await user_for(db, user_id); m = Material(user_id=u.id, filename=file.filename, source_text=text); db.add(m); await db.commit(); await db.refresh(m); return {'id':m.id,'filename':m.filename,'characters':len(text)}

@app.post('/problems/generation')
async def generation(p: Generation):
    raw=p.raw_llm_response
    if not {'prompt','answer','type'}.issubset(raw): raise HTTPException(422, 'LLM response is missing required fields')
    if str(raw['type']) not in {'multiple_choice','numeric','short_answer'}: raise HTTPException(422, 'Unsupported problem type')
    async with Session() as db:
        u=await user_for(db,p.user_id); r=await db.execute(select(Topic).where(Topic.user_id==u.id,Topic.name==p.topic)); t=r.scalar_one_or_none()
        if not t: t=Topic(user_id=u.id,name=p.topic); db.add(t); await db.flush()
        problem=Problem(user_id=u.id,topic_id=t.id,material_id=p.material_id,prompt=str(raw['prompt']),problem_type=str(raw['type']),difficulty=p.difficulty,answer_key=str(raw['answer']),metadata_json={k:v for k,v in raw.items() if k not in {'prompt','answer','type'}})
        db.add(problem); await db.commit(); await db.refresh(problem)
        return {'id':problem.id,'topic':t.name,'prompt':problem.prompt,'type':problem.problem_type,'difficulty':problem.difficulty}

@app.get('/problems/{problem_id}')
async def problem(problem_id:int,user_id:str):
    async with Session() as db:
        u=await user_for(db,user_id); r=await db.execute(select(Problem,Topic).join(Topic,Problem.topic_id==Topic.id).where(Problem.id==problem_id,Problem.user_id==u.id)); row=r.first()
        if not row: raise HTTPException(404,'Problem not found')
        p,t=row; return {'id':p.id,'topic':t.name,'prompt':p.prompt,'type':p.problem_type,'difficulty':p.difficulty}

@app.post('/attempts')
async def attempt(a:AttemptIn):
    async with Session() as db:
        u=await user_for(db,a.user_id); r=await db.execute(select(Problem).where(Problem.id==a.problem_id,Problem.user_id==u.id)); p=r.scalar_one_or_none()
        if not p: raise HTTPException(404,'Problem not found')
        correct=verified_correct(p,a.submitted_answer)
        db.add(Attempt(user_id=u.id,problem_id=p.id,submitted_answer=a.submitted_answer,correct=correct,grading_evidence={'method':'server_exact_match'},elapsed_ms=a.elapsed_ms))
        r=await db.execute(select(UserTopicMastery).where(UserTopicMastery.user_id==u.id,UserTopicMastery.topic_id==p.topic_id)); m=r.scalar_one_or_none()
        if not m: m=UserTopicMastery(user_id=u.id,topic_id=p.topic_id); db.add(m)
        old_n=m.attempts; m.attempts+=1; m.rolling_accuracy=((m.rolling_accuracy*old_n)+int(correct))/m.attempts
        await db.commit(); return {'correct':correct,'recorded':True}
