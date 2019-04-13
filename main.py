from functools import reduce
from pprint import pprint

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

def shift_rows(state):
	o_state = [0] * 4
	for shift, row in enumerate(state):
		o_state[shift] = row[shift:] + row[:shift]
	return o_state

def mix_cols(state):
	for c in range(len(state[0])):
		col = [state[r][c] for r in range(len(state))]
		mixed_col = compute_mix_col(col)
		for r in range(len(state)):
			state[r][c] = mixed_col[r]
	return state

def compute_mix_col(col):
	mx = [[2, 3, 1, 1],
	[1, 2, 3, 1],
	[1, 1, 2, 3],
	[3, 1, 1, 2]]
	o_col = [0] * 4
	for i, row in enumerate(mx):
		values = [mult(a, b) for a, b in zip(row, col)]
		o_col[i] = reduce(lambda a, b: a ^ b, values)
	return o_col

def mult(a, b):
	p = 0
	for i in range(8):
		p ^= a if b & 0b1 else 0
		high = a >> 7
		a = (a << 1) ^ (0x1b if high else 0)
		b >>= 1
	return uint(p)

def gen_rcons(rounds):
	rcons = []
	for i in range(rounds):
		value = 0
		if i + 1 > 1:
			if rcons[i - 1] >= 0x80:
				value = uint((2 * rcons[i - 1]) ^ 0x11b)
			else:
				value = uint(2 * rcons[i - 1])
		else:
			value = 1
		rcons.append(value)
	return list(map(lambda x: x << 24, rcons))

def generate_round_keys(key):
	R = 11
	sbox = generate_sbox()
	rcons = gen_rcons(R - 1)
	N = 4
	key_split = [key[i:i + 4] for i in range(0, len(key), 4)]
	K = [int(k.encode("utf-8").hex(), 16) for k in key_split]
	W = [0] * (4 * R)
	for i in range(4 * R):
		if i < N:
			W[i] = K[i]
		elif i >= N and i % N == 0:
			word_str = hex(W[i - 1])[2:].zfill(8)
			rot = word_str[2:] + word_str[:2]
			hex_bytes = [rot[j:j + 2] for j in range(0, len(rot), 2)]
			subvals = [sbox(hex_bytes[b]) for b in range(len(hex_bytes))]
			sval = (subvals[0] << 24) + (subvals[1] << 16) + (subvals[2] << 8) + subvals[3]
			W[i] = W[i - N] ^ sval ^ rcons[(i // N) - 1]
		elif i >= N and N > 6 and i % N == 4:
			word_str = hex(W[i - 1])[2:].zfill(8)
			hex_bytes = [word_str[j:j + 2] for j in range(0, len(word_str), 2)]
			subvals = [sbox(hex_bytes[b]) for b in range(len(hex_bytes))]
			sval = (subvals[0] << 24) + (subvals[1] << 16) + (subvals[2] << 8) + subvals[3]
			W[i] = W[i - N] ^ sval
		else:
			W[i] = W[i - N] ^ W[i - 1]
	return [tuple(W[i:i + 4]) for i in range(0, len(W), 4)]

def init_state(message):
	state = [0] * 4
	for i in range(len(state)):
		state[i] = [uint(ord(message[j])) for j in range(i, len(message), 4)]
	return state

def print_state(state):
	for row in state:
		for f in row:
			print(hex(f)[2:].zfill(2), end=" ")
		print()

def join_state(state):
	res = ""
	for c in range(len(state[0])):
		col = [state[r][c] for r in range(len(state))]
		vals = list(map(lambda x: hex(x)[2:].zfill(2), col))
		res += "".join(vals)
	return res

def add_round_key(state, round_key):
	key = []
	for rk in round_key:
		hx = hex(rk)[2:].zfill(8)
		key += [int(hx[i:i + 2], 16) for i in range(0, len(hx), 2)]
	for i in range(len(state)):
		key_state = [key[j] for j in range(i, len(key), 4)]
		state[i] = [sv ^ kv for sv, kv in zip(state[i], key_state)]
	return state

def sub_bytes(state, sbox):
	for r in range(len(state)):
		row = state[r]
		for c in range(len(row)):
			val = state[r][c]
			state[r][c] = sbox(hex(val))
	return state

def aes(key, message):
	round_keys = generate_round_keys(key)
	rounds = 10
	sbox = generate_sbox()
	# initialization
	state = init_state(message)
	state = add_round_key(state, round_keys[0])
	# rounds
	for i in range(1, 10):
		state = sub_bytes(state, sbox)
		state = shift_rows(state)
		state = mix_cols(state)
		state = add_round_key(state, round_keys[i])
	# final round
	state = sub_bytes(state, sbox)
	state = shift_rows(state)
	state = add_round_key(state, round_keys[-1])
	return join_state(state)


# ========================================================

key = "Thats my Kung Fu"
message = "Two One Nine Two"
enc = aes(key, message)
print("Message: \t %s" % message)
print("Encrypted: \t %s" % enc)

