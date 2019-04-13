from aes import aes as aes

key = "Thats my Kung Fu"
message = "Two One Nine Two"
enc = aes.aes(key, message)
ans = "29c3505f571420f6402299b31a02d73a"
if enc == ans:
	print("still works")
else:
	print("nope")
# print("Message: \t %s" % message)
# print("Encrypted: \t %s" % enc)
