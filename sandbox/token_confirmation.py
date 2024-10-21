from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, BadTimeSignature

secret_key='hard to guess string'  
expiration=3600
s = Serializer(secret_key, expiration)

token='eyJhbGciOiJIUzI1NiIsImlhdCI6MTcyOTQ2NjEzNywiZXhwIjoxNzI5NDY5NzM3fQ.eyJjb25maXJtIjoiZDlkOTA2ZDQtNDY2NS00YzFlLWIyZGQtZjQxNzc4OGU5NmMyIn0.6B6-VR51aPDCXP08aXTry6tTVNhy8P2huyoQUAn0hWg'
data = s.loads(token) 
print(data)
# try:
#     data = s.loads(token, max_age=3600) 
#     print(data)
#     # if data.get('confirm') == self.id:
#     #     self.confirmed = True
#     #     db.session.commit()
#     #     return True
# except (SignatureExpired, BadSignature): 
#     print('failed to decipher token')
#     # return False