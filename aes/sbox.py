def uint(x):
	return x & 0xff

def rotleft(x, shift):
	left = uint(x << shift)
	right = x >> (8 - shift)
	return left | right

def generate_sbox():
	sbox = [0] * 256
	p = 1
	q = 1
	while True:
		p = uint(p ^ (p << 1) ^ (0x1b if p & 0x80 else 0))
		q ^= uint(q << 1)
		q ^= uint(q << 2)
		q ^= uint(q << 4)
		q ^= uint(0x09 if q & 0x80 else 0)
		xf = uint(q ^ rotleft(q, 1) ^ rotleft(q, 2) ^ rotleft(q, 3) ^ rotleft(q, 4))
		xf = uint(xf ^ 0x63)
		sbox[p] = xf
		if p == 1:
			break
	sbox[0] = 0x63

	def sbox_value(input_hex):
		val = int(input_hex, 16)
		ln = val & 0x0f
		hn = val >> 4
		return sbox[(hn * 16) + ln]

	return sbox_value

