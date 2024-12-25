import jwt 
import datetime


test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCaJ.eyJzdWIiOiJycjM0NDhAYnUuZWR1IiwiaWF0IjoxNzI5NTU4MjE0LCJleHAiOjE3Mjk1NTg1NzR9.HLC3U7Q3gN28lMEY8jPPB3p-UFjmJ9JICsVkzWThq9I"
secret_key="test_string"

# email = "rr3448@bu.edu" 


token = jwt.encode(
    {
        "sub": email,  # Subject of the token (user's email)
        "iat": datetime.datetime.now(datetime.timezone.utc),  # Issued at time
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=1),  # Token expiration time (1 hour)
    },
    secret_key,
    algorithm="HS256",
)

# print(f'token = {token}') 


data = jwt.decode(test_token, secret_key, algorithms=['HS256']) 
decoded_email = data["sub"] 
print(f"decoded_emal = {decoded_email}")