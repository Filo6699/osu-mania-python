import socket
import json


NO_TOKEN_POCKETS = [
    "auth"
]

# def get_pocket_type(data: dict):
#     try:
#         return POCKET_TYPES[data["type"]]
#     except:
#         return False

# def parse_pocket(data: bytes | str | dict) -> Pocket:
#     if isinstance(data, bytes):
#         try:
#             data = json.loads(data.decode())
#         except:
#             return None
#     if isinstance(data, str):
#         try:
#             data = json.loads(data)
#         except:
#             return None
#     if not isinstance(data, dict):
#         return None

#     ptype = get_pocket_type(data)
#     if ptype == LoginPocket:
#         return LoginPocket(data["login"], data["password"])
