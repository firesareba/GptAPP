from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
class Base(DeclarativeBase): pass
class User(Base):
 __tablename__='users'; id:Mapped[int]=mapped_column(primary_key=True); external_id:Mapped[str]=mapped_column(String(128),unique=True,index=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Topic(Base):
 __tablename__='topics'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True); name:Mapped[str]=mapped_column(String(200)); parent_name:Mapped[str|None]=mapped_column(String(200),nullable=True)
class Material(Base):
 __tablename__='materials'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True); filename:Mapped[str]=mapped_column(String(255)); source_text:Mapped[str]=mapped_column(Text); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Problem(Base):
 __tablename__='problems'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True); topic_id:Mapped[int]=mapped_column(ForeignKey('topics.id'),index=True); material_id:Mapped[int|None]=mapped_column(ForeignKey('materials.id'),nullable=True); prompt:Mapped[str]=mapped_column(Text); problem_type:Mapped[str]=mapped_column(String(32)); difficulty:Mapped[float]=mapped_column(Float); answer_key:Mapped[str]=mapped_column(Text); metadata_json:Mapped[dict]=mapped_column(JSON,default=dict); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Attempt(Base):
 __tablename__='attempts'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True); problem_id:Mapped[int]=mapped_column(ForeignKey('problems.id'),index=True); submitted_answer:Mapped[str]=mapped_column(Text); correct:Mapped[bool]=mapped_column(Boolean); grading_evidence:Mapped[dict]=mapped_column(JSON,default=dict); elapsed_ms:Mapped[int]=mapped_column(Integer); battle_id:Mapped[int|None]=mapped_column(ForeignKey('boss_battles.id'),nullable=True,index=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class UserTopicMastery(Base):
 __tablename__='user_topic_mastery'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True); topic_id:Mapped[int]=mapped_column(ForeignKey('topics.id'),index=True); rolling_accuracy:Mapped[float]=mapped_column(Float,default=0.75); difficulty:Mapped[float]=mapped_column(Float,default=0.5); attempts:Mapped[int]=mapped_column(Integer,default=0); last_attempt_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class UserWallet(Base):
 __tablename__='user_wallet'; user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),primary_key=True); balance:Mapped[float]=mapped_column(Float,default=0); decay_last_applied:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class WalletTransaction(Base):
 __tablename__='wallet_transactions'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True); amount:Mapped[float]=mapped_column(Float); reason:Mapped[str]=mapped_column(String(64)); metadata_json:Mapped[dict]=mapped_column(JSON,default=dict); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class BossBattle(Base):
 __tablename__='boss_battles'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True); topic_id:Mapped[int]=mapped_column(ForeignKey('topics.id'),index=True); outcome:Mapped[str|None]=mapped_column(String(16),nullable=True); boss_hp:Mapped[float]=mapped_column(Float,default=100); damage_log:Mapped[list]=mapped_column(JSON,default=list); reward_granted:Mapped[float]=mapped_column(Float,default=0); recap_text:Mapped[str|None]=mapped_column(Text,nullable=True); entry_cost:Mapped[float]=mapped_column(Float,default=0); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow); finished_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
