from fastapi import APIRouter, status, HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from utils.constants import Endpoints, ResponseMessages
from utils.security import hash_password, verify_password, create_access_token, decode_access_token, verify_admin_token
from .UserSchemas import UserSchema, UserLoginSchema, UserRegisterResponseSchema, CandidateSchema, VotingSchema, UserUpdateSchema
from db.DbConfig import get_db
from db.DbModels import UserDBModel, CandidateDBModel, VoteDBModel
from sqlalchemy.orm import Session
from sqlalchemy import func


UserRouter = APIRouter(prefix="/users", tags=["Users"])

@UserRouter.post(Endpoints.REGISTER, status_code=status.HTTP_201_CREATED, response_model=UserRegisterResponseSchema)
def create_user(user: UserSchema, db=Depends(get_db)):
    """
    Endpoint to create a new user.
    """
    # validate user 
    existing_user = db.query(UserDBModel).filter(UserDBModel.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseMessages.USER_ALREADY_EXISTS)
    # add user to the database
    hashed_password = hash_password(user.password)
    new_user = UserDBModel(**user.model_dump(exclude={"password"}), hashed_password=hashed_password)
    try:
        db.add(new_user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db.refresh(new_user)
    return new_user



@UserRouter.get(Endpoints.LOGIN)
def login_user(user: UserLoginSchema, db=Depends(get_db)):
    """
    Endpoint to log in a user.
    """
    # validate user
    existing_user = db.query(UserDBModel).filter(UserDBModel.email == user.email).first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseMessages.USER_NOT_FOUND)
    
    # verify password
    if not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ResponseMessages.INVALID_CREDENTIALS)
    # Generate JWT token
    payload = {
        "user_id": existing_user.id,
        "email": existing_user.email}
    token = create_access_token(data=payload)
    return {"message": ResponseMessages.USER_LOGGED_IN, "token": token, "authentication_type" :"Bearer"}




@UserRouter.get(Endpoints.UserInfo)
def get_user_info(payload = Depends(decode_access_token)):
    """
    Endpoint to get user information.
    """
    return payload

@UserRouter.patch(Endpoints.UserInfo)
def update_user_info(update_data: UserUpdateSchema, payload = Depends(decode_access_token), db=Depends(get_db)):
    """
    Endpoint to update user information.
    """
    user_id = payload.get("user_id")
    user = db.query(UserDBModel).filter(UserDBModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseMessages.USER_NOT_FOUND)
    # Update fields if provided
    if update_data.name is not None:
        user.name = update_data.name
    if update_data.email is not None:
        # Check if email is already taken
        existing = db.query(UserDBModel).filter(UserDBModel.email == update_data.email, UserDBModel.id != user_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseMessages.USER_ALREADY_EXISTS)
        user.email = update_data.email
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db.refresh(user)
    return {"message": ResponseMessages.USER_UPDATED, "user": {"id": user.id, "name": user.name, "email": user.email, "is_active": user.is_active}}

@UserRouter.delete(Endpoints.DELETE)
def delete_user(payload = Depends(decode_access_token), db=Depends(get_db)):
    """
    Endpoint to delete a user.
    """
    user_id = payload.get("user_id")
    user = db.query(UserDBModel).filter(UserDBModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseMessages.USER_NOT_FOUND)
    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return {"message": ResponseMessages.USER_DELETED, "status": status.HTTP_200_OK}


@UserRouter.post(Endpoints.VOTE, status_code=status.HTTP_200_OK)
def vote(candidate: VotingSchema, user = Depends(decode_access_token), db=Depends(get_db)):
    """
    Endpoint to cast a vote for a candidate.
    """
    # Check if candidate exists
    existing_candidate = db.query(CandidateDBModel).filter(CandidateDBModel.id == candidate.candidate_id).first()
    if not existing_candidate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseMessages.CANDIDATE_NOT_FOUND)
    # Check if user has already voted
    user_id = user.get("user_id")
    existing_vote = db.query(VoteDBModel).filter(VoteDBModel.user_id == user_id).first()
    if existing_vote:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseMessages.ALREADY_VOTED)
    # Cast vote
    new_vote = VoteDBModel(user_id=user_id, candidate_id=candidate.candidate_id)
    try:
        db.add(new_vote)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db.refresh(new_vote)
    return new_vote

AdminRouter = APIRouter(prefix="/admin", tags=["Admin"])

# add candidates to db
@AdminRouter.post(Endpoints.ADD_CANDIDATE, dependencies=[Depends(verify_admin_token)], status_code=status.HTTP_201_CREATED)
def add_candidate(new_candidate: CandidateSchema, db=Depends(get_db)):
    candidate = CandidateDBModel(**new_candidate.model_dump())
    try:
        db.add(candidate)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ResponseMessages.CANDIDATE_ALREADY_EXISTS)
    db.refresh(candidate)
    return candidate

# get vote counts for all candidates
@AdminRouter.get(Endpoints.ADD_CANDIDATE, dependencies=[Depends(verify_admin_token)])
def get_vote_counts(db=Depends(get_db)):
    # Aggregate votes by candidate_id and candidate name
    results = db.query(CandidateDBModel.name, func.count(VoteDBModel.id).label("vote_count"))\
        .outerjoin(VoteDBModel, CandidateDBModel.id == VoteDBModel.candidate_id)\
        .group_by(CandidateDBModel.id).all()
    return [{"name": name, "vote_count": count} for name, count in results]

# update candidate
@AdminRouter.put(f"{Endpoints.ADD_CANDIDATE}/{{candidate_id}}", dependencies=[Depends(verify_admin_token)])
def update_candidate(candidate_id: int, update_data: CandidateSchema, db=Depends(get_db)):
    candidate = db.query(CandidateDBModel).filter(CandidateDBModel.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseMessages.CANDIDATE_NOT_FOUND)
    candidate.name = update_data.name
    candidate.party = update_data.party
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db.refresh(candidate)
    return candidate

# delete candidate
@AdminRouter.delete(f"{Endpoints.ADD_CANDIDATE}/{{candidate_id}}", dependencies=[Depends(verify_admin_token)])
def delete_candidate(candidate_id: int, db=Depends(get_db)):
    candidate = db.query(CandidateDBModel).filter(CandidateDBModel.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseMessages.CANDIDATE_NOT_FOUND)
    try:
        db.delete(candidate)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return {"message": ResponseMessages.CANDIDATE_DELETED, "status": status.HTTP_200_OK}

# get vote count for specific candidate
@AdminRouter.get(f"{Endpoints.ADD_CANDIDATE}/{{candidate_id}}", dependencies=[Depends(verify_admin_token)])
def get_candidate_vote_count(candidate_id: int, db=Depends(get_db)):
    candidate = db.query(CandidateDBModel).filter(CandidateDBModel.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseMessages.CANDIDATE_NOT_FOUND)
    vote_count = db.query(func.count(VoteDBModel.id)).filter(VoteDBModel.candidate_id == candidate_id).scalar()
    return {"name": candidate.name, "vote_count": vote_count}
