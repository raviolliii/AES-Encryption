from functools import reduce

def uint(x):
	return x & 0xff

def mult(a, b):
	p = 0
	for i in range(8):
		p ^= a if b & 0b1 else 0
		high = a >> 7
		a = (a << 1) ^ (0x1b if high else 0)
		b >>= 1
	return uint(p)

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

def mix_cols(state):
	for c in range(len(state[0])):
		col = [state[r][c] for r in range(len(state))]
		mixed_col = compute_mix_col(col)
		for r in range(len(state)):
			state[r][c] = mixed_col[r]
	return state

