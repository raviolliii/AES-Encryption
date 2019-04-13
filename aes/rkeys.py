def uint(x):
	# casts x to unsigned int (1 byte)
	return x & 0xff

def chunkify(string, size):
	# breaks up string into chunks of size
	chunks = []
	for i in range(0, len(string), size):
		chunks.append(string[i:i + size])
	return chunks

def gen_rcons(rounds):
	# generates and returns round constants
	# the round constants don't depend on the 
	# key so these constants could have been 
	# hard coded, but I wanted to build it anyway
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

def generate_round_keys(key, rounds, sbox):
	# Generates round keys based on main key
	# basic variables used for looping, etc.
	key_size = len(key) * 8
	R = rounds + 1
	rcons = gen_rcons(rounds) # get round key constants
	N = key_size // 32
	# split key into 32 bit words and parse to int
	K = [int(k.encode("utf-8").hex(), 16) for k in chunkify(key, 4)] 
	W = [0] * (4 * R)

	# main loop to generate expanded round subkeys
	for i in range(4 * R):
		if i < N:
			W[i] = K[i]
		elif i >= N and i % N == 0:
			word_str = hex(W[i - 1])[2:].zfill(8) # turn int to 8 digit hex
			rot = word_str[2:] + word_str[:2] # rotate left 1 byte 
			hex_bytes = chunkify(rot, 2) # split into byte chunks
			subvals = [sbox(hexb) for hexb in hex_bytes] # sub out hex bytes with s-box
			sval = (subvals[0] << 24) \
				+ (subvals[1] << 16) \
				+ (subvals[2] << 8) \
				+ subvals[3] # concat hex bytes and parse to 32 bit int
			W[i] = W[i - N] ^ sval ^ rcons[(i // N) - 1]
		elif i >= N and N > 6 and i % N == 4:
			word_str = hex(W[i - 1])[2:].zfill(8) # turn int to 8 digit hex
			hex_bytes = chunkify(word_str, 2) # split into byte chunks
			subvals = [sbox(hexb) for hexb in hex_bytes] # sub out hex bytes with s-box
			sval = (subvals[0] << 24) \
				+ (subvals[1] << 16) \
				+ (subvals[2] << 8) \
				+ subvals[3] # concat hex bytes and parse to 32 bit int
			W[i] = W[i - N] ^ sval
		else:
			W[i] = W[i - N] ^ W[i - 1]

	# subkeys are all 128 bits, but each entry is 32 bits
	# so combine all entries by groups of 4 for later use
	return [tuple(W[i:i + 4]) for i in range(0, len(W), 4)]

def add_round_key(state, round_key):
	# adds each byte of the round key to the 
	# respective byte of the state
	key = []
	# round key is a tuple of 4, 32 bit ints
	for rk in round_key:
		hx = hex(rk)[2:].zfill(8) # turn int to hex
		# add each byte to the key list as an int
		key += [int(hx[i:i + 2], 16) for i in range(0, len(hx), 2)]
	for i in range(len(state)):
		# run through the state and add each byte to the
		# respective byte in the key
		key_state = [key[j] for j in range(i, len(key), 4)]
		state[i] = [sv ^ kv for sv, kv in zip(state[i], key_state)]
	return state
