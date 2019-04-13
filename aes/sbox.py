def uint(x):
	# casts x to unsigned int (1 byte)
	return x & 0xff

def rotleft(x, shift):
	# rotates bits left in a 1 byte int
	left = uint(x << shift)
	right = x >> (8 - shift)
	return left | right

def generate_sbox():
	# generates the Rijndael Substitution Box
	# the s-box can be hard coded in here,
	# but there is an algorithm to generate it,
	# and I didn't want to type out the whole box
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
		# returns the value in the s-box given
		# the input hex (most significant nibble
		# is the row, least significant is the 
		# column)
		val = int(input_hex, 16)
		ln = val & 0x0f
		hn = val >> 4
		return sbox[(hn * 16) + ln]

	return sbox_value

