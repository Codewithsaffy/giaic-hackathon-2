import jwt
import datetime

SECRET = "a_very_long_32_character_secret_for_development_1234567890"
ALGORITHM = "HS256"

def generate_token(user_id="00000000-0000-0000-0000-000000000001"):
    payload = {
        "sub": user_id,
        "name": "Test User",
        "email": "test@example.com",
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return token

if __name__ == "__main__":
    print(generate_token())
