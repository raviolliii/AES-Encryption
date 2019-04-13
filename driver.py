from aes import aes

key = "Thats my Kung Fu"
message = "Two One Nine Two"
enc = aes.encrypt(key, message)

# supposed to be 29c3505f571420f6402299b31a02d73a
print("Message:\t", message)
print("Encrypted:\t", enc)
