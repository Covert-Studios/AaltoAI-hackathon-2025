from fastapi import Depends, HTTPException, status, Request
import jwt
from dotenv import load_dotenv
import os

load_dotenv()
CLERK_JWT_PUBLIC_KEY = os.getenv("CLERK_JWT_PUBLIC_KEY").replace("\\n", "\n")

def get_current_user_id(request: Request):
    auth = request.headers.get("Authorization")
    print("Authorization header:", auth)  # Add this line
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    token = auth.split(" ")[1]
    try:
        print("Using public key:", CLERK_JWT_PUBLIC_KEY)
        print("JWT header:", jwt.get_unverified_header(token))
        payload = jwt.decode(
            token,
            CLERK_JWT_PUBLIC_KEY,
            algorithms=["RS256"],
            options={"verify_aud": False},
            leeway=10  # allow 10 seconds clock skew
        )
        return payload["sub"] 
    except Exception as e:
        print("JWT decode error:", e)  # Add this line
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")