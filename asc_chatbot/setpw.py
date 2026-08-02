from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
pwd = PasswordHash([Argon2Hasher()])
print(pwd.hash("your_admin_password:"))
/
#$argon2id$v=19$m=65536,t=3,p=4$ZQNwXvY8vM7VbWoL5rjfoA$FdFDTshSN6Ixkoi4y+9Kp9NkUqc7N6GquQ9bMhsb7Wg