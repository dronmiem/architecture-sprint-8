import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
import requests
import os
import sys
import uvicorn


app = FastAPI()
log = logging.getLogger('uvicorn.error')
log.debug('API is starting up')
log.debug("Custom logger integrated with Uvicorn error and access loggers.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

KEYCLOAK_SERVER_URL = "http://keycloak:8080"
REALM_NAME = "reports-realm"
CLIENT_ID = "reports-backend"
response = {}

security = HTTPBearer()


def get_jwks():
    global response
    log.debug(f"Uuuuuuuuuuuuuuuuuuuuuuuuuuu get_jwks")
    if not response:
        url = f"{KEYCLOAK_SERVER_URL}/realms/{REALM_NAME}/protocol/openid-connect/certs"
        response = requests.get(url)
        response.raise_for_status()
        response = response.json()
    return response


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    log.debug(" Uuuuuuuuuuuuuuuuuuuuuuuuuuu verify_token")
    jwks = get_jwks()
    try:
        unverified_header = jwt.get_unverified_header(token)
        log.debug(f"Unverified header: {unverified_header}")
        kid = unverified_header["kid"]
        key = next((key for key in jwks["keys"] if key["kid"] == kid), None)
        if key is None:
            log.error("Key not found for kid.")
            raise HTTPException(status_code=401, detail="Invalid token.")

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=f"http://localhost:8080/realms/{REALM_NAME}"
        )
        log.debug(f"Token payload: {payload}")

        roles = payload.get("realm_access", {}).get("roles", [])
        log.debug(f"Roles from token: {roles}")
        if not roles:
            log.error("No roles found in token.")
            raise HTTPException(status_code=403, detail="Forbidden: No roles found.")

        if "prothetic_user" not in roles:
            log.error("User does not have the required role.")
            raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this resource.")

        return payload
    except jwt.JWTError as e:
        log.error(f"Token verification error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@app.get("/reports")
def download_report(payload: dict = Depends(verify_token)):
    log.debug("eeeeeeeeeeeeeeeeeeeeebaaaaaaaaaaaaaaaat download_report")
    report_file_path = os.path.abspath("./Report.xlsx")
    if not os.path.exists(report_file_path):
        log.error("File not found.")
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(report_file_path, media_type="application/xlsx", filename="Report.xlsx")
