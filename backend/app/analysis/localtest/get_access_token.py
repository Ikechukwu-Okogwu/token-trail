"""Get JWT access token: try login, on failure signup then retry login. No file logging."""
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent.parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

import requests

BASE_URL = "http://localhost:8000/api"

DEFAULT_EMAIL = "ab12cd@brocku.ca"
DEFAULT_PASSWORD = "admin"
DEFAULT_NAME = "Local Tester"


def get_access_token(
    email: str = DEFAULT_EMAIL,
    password: str = DEFAULT_PASSWORD,
    name: str | None = None,
    base_url: str = BASE_URL,
) -> str:
    """Try login; if 401, signup then retry. Raise RuntimeError if second login fails."""
    if name is None:
        name = DEFAULT_NAME

    login_body = {"email": email, "password": password}
    signup_body = {"name": name, "email": email, "password": password}

    # First attempt: login
    r = requests.post(f"{base_url}/auth/login", json=login_body, timeout=10)
    if r.status_code == 200:
        return r.json()["accessToken"]

    # Login failed: try signup (may get 409 if already registered), then retry login
    signup_r = requests.post(f"{base_url}/auth/signup", json=signup_body, timeout=10)
    if signup_r.status_code not in (200, 201, 409):
        raise RuntimeError(
            f"Login failed ({r.status_code}) and signup failed ({signup_r.status_code}): {signup_r.text}"
        )

    # Second attempt: login
    r2 = requests.post(f"{base_url}/auth/login", json=login_body, timeout=10)
    if r2.status_code != 200:
        raise RuntimeError(
            f"Second login attempt failed ({r2.status_code}): {r2.text}"
        )

    return r2.json()["accessToken"]


if __name__ == "__main__":
    print(get_access_token())