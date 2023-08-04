#  RUN ::
#  uvicorn main:app --reload
# https://fastapi.tiangolo.com/tutorial/security/first-steps/

# OAtuh2 인증을 사용하여 '/items/' 엔드포인트에 접근하는 FastAPI 애플리케이션

# Annotated 타입 힌트는 매개변수에 메타데이터를 첨부하기 위해 사용됨
from typing import Annotated

# Depends 함수는 OAuth2 토큰을 'read_items' 함수에 주입하는 데 사용됨
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

# tokenUrl 파라미터는 클라이언트가 토큰을 얻기 위해 전송하는 username, password URL이 포함됨
# toeknURL="token"은 아직 만들어지지 않은 상대적인 URL 토큰을 나타냄. 상대적인 URL이므로 ./token과 동등
# 이 매개변수는 엔드포인트/경로 동작을 생성하지 않지만, 클라이언트가 토큰을 가져오기 위해 사용해야 하는 URL이 /token임을 선언함
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
# oauth2_scheme을 depends를 통해 dependency로 넘길 수 있음
# 이 dependency는 path operation function의 token 파라미터에 할당되는 str을 제공해줌
# FastAPI는 이 dependency를 OpenAPI schema 안의 security scheme을 정의하는 데 사용하는 것을 알 수 있음
# Request에서 Authroization header가 있는지, 그리고 그 값이 Bearer + token인지 확인하고 str로 토큰을 return
# Authroization header가 없거나, 값이 Bearer token이 아니라면 401 status code(UNAHUTORIZED) 반환
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}