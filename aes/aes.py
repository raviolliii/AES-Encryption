from aes import sbox as sb
from aes import mixcols as mc
from aes import rkeys as rk

# rename functions for easier use
generate_sbox = sb.generate_sbox
mix_cols = mc.mix_cols
generate_round_keys = rk.generate_round_keys
add_round_key = rk.add_round_key

def uint(x):
	# casts x to unsigned int (1 byte)
	return x & 0xff

def shift_rows(state):
	# shifts rows of the aes state
	# each row gets shifted to the left 
	# (row index) times (eg. row 0 is 
	# shifted 0 times)
	o_state = [0] * 4
	for shift, row in enumerate(state):
		o_state[shift] = row[shift:] + row[:shift]
	return o_state

def init_state(message):
	# initializes the state with given
	# message, in column major order as
	# per the algorithm
	state = [0] * 4
	for i in range(len(state)):
		state[i] = [uint(ord(message[j])) for j in range(i, len(message), 4)]
	return state

def print_state(state):
	# Debugging purposes
	# Prints out state 
	for row in state:
		for f in row:
			print(hex(f)[2:].zfill(2), end=" ")
		print()

def join_state(state):
	# gets hex digits of each byte in the
	# state and concats them, to build the 
	# state bytestring
	res = ""
	for c in range(len(state[0])):
		col = [state[r][c] for r in range(len(state))]
		vals = list(map(lambda x: hex(x)[2:].zfill(2), col))
		res += "".join(vals)
	return res

def sub_bytes(state, sbox):
	# uses the Rijndael S-box to sub out
	# bytes in the state 
	for r in range(len(state)):
		row = state[r]
		for c in range(len(row)):
			val = state[r][c]
			state[r][c] = sbox(hex(val))
	return state

def clean(key, message):
	# returns 0 if the key or message
	# is invalid
	key_length = len(key) * 8
	if key_length not in [128, 192, 256]:
		return 0
	if len(message) != 16:
		return 0
	return 1

def encrypt(key, message):
	if not clean(key, message):
		return -1

	# basic variables needed for loop limits, etc.
	key_size = len(key) * 8
	rounds = {
		128: 10,
		192: 12,
		256: 14
	}[key_size] # number of rounds depends on the key size
	sbox = generate_sbox() # get s-box
	round_keys = generate_round_keys(key, rounds, sbox) # get the round keys

	# initial step
	state = init_state(message)
	state = add_round_key(state, round_keys[0])

	# main rounds
	for i in range(1, rounds):
		state = sub_bytes(state, sbox) # sub state bytes using the s-box
		state = shift_rows(state) # shift the rows of the state
		state = mix_cols(state) # mix columns of the state
		state = add_round_key(state, round_keys[i]) # add the round key to the state

	# final round
	state = sub_bytes(state, sbox)
	state = shift_rows(state)
	state = add_round_key(state, round_keys[-1])

	return join_state(state)
