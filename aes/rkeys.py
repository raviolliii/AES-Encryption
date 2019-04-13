def uint(x):
	return x & 0xff

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

def generate_round_keys(key, sbox):
	R = 11
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

def add_round_key(state, round_key):
	key = []
	for rk in round_key:
		hx = hex(rk)[2:].zfill(8)
		key += [int(hx[i:i + 2], 16) for i in range(0, len(hx), 2)]
	for i in range(len(state)):
		key_state = [key[j] for j in range(i, len(key), 4)]
		state[i] = [sv ^ kv for sv, kv in zip(state[i], key_state)]
	return state

