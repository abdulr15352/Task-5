# DB models
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, func, ForeignKey
from db.DbConfig import Base, Engine


class TableNames:
    USERS = "users" # Table name for users
    CANDIDATES = "candidates" # Table name for candidates
    VOTES = "votes" # Table name for votes

class ColumnNames:
    ID = "id"
    USER_ID = "user_id"
    CANDIDATE_ID = "candidate_id"
    EMAIL = "email"
    HASHED_PASSWORD = "hashed_password"
    NAME = "name"
    IS_ACTIVE = "is_active"
    CREATED_AT = "created_at"
    PARTY = "party"

class UserDBModel(Base):
    __tablename__ = TableNames.USERS    

    id = Column(ColumnNames.ID, Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(ColumnNames.EMAIL, String, unique=True, index=True, nullable=False)
    hashed_password = Column(ColumnNames.HASHED_PASSWORD, String, nullable=False)
    name = Column(ColumnNames.NAME, String, nullable=True)
    is_active = Column(ColumnNames.IS_ACTIVE, Boolean, default=True)  # True for active, False for inactive
    created_at = Column(ColumnNames.CREATED_AT, TIMESTAMP(True), default=func.now(), nullable=False)

class CandidateDBModel(Base):
    __tablename__ = TableNames.CANDIDATES

    id = Column(ColumnNames.ID, Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(ColumnNames.NAME, String, nullable=False, unique=True)
    party = Column(ColumnNames.PARTY, String, nullable=True)
    created_at = Column(ColumnNames.CREATED_AT, TIMESTAMP(True), default=func.now(), nullable=False)

class VoteDBModel(Base):
    __tablename__ = TableNames.VOTES

    id = Column(ColumnNames.ID, Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(ColumnNames.USER_ID, Integer, ForeignKey(f"{TableNames.USERS}.{ColumnNames.ID}", ondelete="SET NULL"), nullable=True)
    candidate_id = Column(ColumnNames.CANDIDATE_ID, Integer, ForeignKey(f"{TableNames.CANDIDATES}.{ColumnNames.ID}", ondelete="RESTRICT"), nullable=False)
    created_at = Column(ColumnNames.CREATED_AT, TIMESTAMP(True), default=func.now(), nullable=False)

Base.metadata.create_all(bind=Engine)
print("Tables created successfully")
