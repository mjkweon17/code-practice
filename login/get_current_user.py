#  RUN ::
#  uvicorn main:app --reload
# https://fastapi.tiangolo.com/tutorial/security/get-current-user/

# 데모 목적을 위한 OAuth2 인증의 기본 구현을 제공함
# 실제 상황에서는 Google, Facebook과 같은 OAuth2 공급자와 통합하거나, 직접 OAuth2 서버를 설정하여 토큰을 유효성 검사하고 사용자를 인증해야 함
# 이 코드는 토큰 유효성 검사나 사용자 인증을 수행하지 않음. 실제 애플리케이션에서는 사용자를 인증하는 것이 중요함

from typing import Annotated, Union

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

app = FastAPI()

# OAuth2 토큰을 추출하고 유효성을 검사하는 데 사용되는 스키마
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

# 토큰을 디코딩한 후 사용자 객체를 반환하는 함수
def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )

# OAuth2 토큰에 의존하며, 토큰을 디코딩하고 사용자 객체를 반환하는 depdenency
# oauth2_scheme을 Depends를 통해 dependency로 넘길 수 있음
# oauth2_scheme은 sub-dependency로, path operation function의 token 파라미터에 할당되는 str을 제공해줌
# Dependency injection level에서 security scheme을 사용하여 토큰을 추출하고 유효성을 검사함
# 그리고 path operation function에서 current user를 직접 구할 수 있음
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # 토큰을 디코딩한 후 사용자 객체를 반환하는 함수
    user = fake_decode_token(token)
    return user

@app.get("/users/me")
# get_current_user 함수를 호출하여 현재 인증된 사용자를 가져옴
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user