# RUN ::
# uvicorn main:app --reload
# https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/

# OAuth2는 password flow를 사용할 때 클라인터가 username, password를 전송하고, 서버가 토큰을 반환하는 방식으로 작동함
# 클라이언트는 scope 폼 파라미터를 사용하여 토큰에 대한 권한을 지정할 수 있음

from typing import Annotated, Union

from fastapi import Depends, FastAPI, HTTPException, status
# OAuth2PasswordRequestForm은 username, password, scope를 포함하는 폼을 파싱하는 클래스 디펜던시
# OAuth2 spec은 grant_type을 고정된 값의 password로 요구하지만, OAuth2PasswordRequestForm은 grant_type을 요구하지 않음
# grant_type을 강제하려면 OAuth2PasswordRequestFormStrict를 사용하면 됨
# client_id, client_secret은 이 코드에서 사용되지 않음
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

app = FastAPI()

# hashing: password를 gibberish처럼 보이는 문자열(sequence of bytes)로 변환하는 것
# 같은 password를 hashing하면 항상 같은 결과가 나오지만, hashing된 결과를 다시 password로 변환할 수는 없음
def fake_hash_password(password: str):
    return "fakehashed" + password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

# Password가 맞는지 검사하기 위해 데이터를 이 곳에 먼저 넣음
# plaintext password를 절대 저장하면 안되기 때문에 password hasing system을 사용해야 함
class UserInDB(User):
    hashed_password: str

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    
def fake_decode_token(token):
    # This doesn't provide any security at all
    # Cehck the next version
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        # 401 Unauthorized는 return될 때 WWW-Authenticate 헤더를 포함해야 함
        # 이 헤더는 클라이언트에게 어떤 인증 방법을 사용해야 하는지 알려줌
        # 여기서는 Bearer 값이 포함된 헤더를 반환함
    return user

async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# OAuth2PasswordRequestForm은 username, password, scope를 포함하는 폼을 파싱하는 클래스 디펜던시
# OAuth2PasswordBearer는 FastAPI로 하여금 security scheme임을 알려줌
# 그러나 OAuth2PasswordRequestForm는 단순히 class dependency일 뿐이고, 직접 작성해도 됨
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorret username or password")
    # UserInDB(**user_dict)는 UserInDB(username=user_dict["username"], email=user_dict["email"], ...)와 같음
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user