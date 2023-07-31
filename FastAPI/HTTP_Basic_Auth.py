# https://fastapi.tiangolo.com/advanced/security/http-basic-auth/

import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

security = HTTPBasic()

def get_current_username(
	credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
	current_username_bytes = credentials.username.encode("utf-8")
	corret_username_bytes = b"minjaekweon"
	is_correct_username = secrets.compare_digest(current_username_bytes, corret_username_bytes)
	current_password_bytes = credentials.password.encode("utf-8")
	correct_password_bytes = b"asdf1234"
	is_correct_password = secrets.compare_digest(current_password_bytes, correct_password_bytes)
	if not (is_correct_username and is_correct_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorret email or password",
			headers={"WWW-Authenticate": "Basic"},
        )
	return credentials.username

@app.get("/users/me")
def read_current_user(username: Annotated[str, Depends(get_current_username)]):
	return {"username": username}