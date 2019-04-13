from aes import sbox as sb
from aes import mixcols as mc
from aes import rkeys as rk

generate_sbox = sb.generate_sbox
mix_cols = mc.mix_cols
generate_round_keys = rk.generate_round_keys
add_round_key = rk.add_round_key

def uint(x):
	return x & 0xff

def shift_rows(state):
	o_state = [0] * 4
	for shift, row in enumerate(state):
		o_state[shift] = row[shift:] + row[:shift]
	return o_state

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

def sub_bytes(state, sbox):
	for r in range(len(state)):
		row = state[r]
		for c in range(len(row)):
			val = state[r][c]
			state[r][c] = sbox(hex(val))
	return state

def aes(key, message):
	sbox = generate_sbox()
	round_keys = generate_round_keys(key, sbox)
	rounds = 10
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

