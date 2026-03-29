SAVE_FILE = r"C:\Program Files (x86)\Steam\userdata\REPLACE_WITH_YOUR_STEAM_USER_ID\531510\remote\JSBSave_SaveData"

ENC = {'0':'p','1':'q','2':'r','3':'s','4':'t','5':'u','6':'v','7':'w','8':'x','9':'y'}
DEC = {v:k for k,v in ENC.items()}

def xor(data):
    return bytes([b ^ 193 for b in data])

#read file
with open(SAVE_FILE, "rb") as f:
    raw = bytearray(f.read())

#backup
with open(SAVE_FILE + ".bak", "wb") as f:
    f.write(raw)
print("Backup saved.")

#decrypt
dec = bytearray(xor(raw))

#find bp field
PATTERN = bytes([0x62,0x02, 0x70,0x03,
                 0x62,0x03, 0x7a,0x03])

idx = dec.find(PATTERN)
if idx == -1:
    print("ERROR: Could not find bp field!")
    exit(1)

value_start = idx + len(PATTERN)

#find end
value_end = value_start
while (
    value_end + 1 < len(dec)
    and chr(dec[value_end]) in DEC
    and dec[value_end + 1] == 0x03
):
    value_end += 2

#read current val
current_encoded = ''.join(
    chr(dec[value_start + i]) for i in range(0, value_end - value_start, 2)
)

current_value = int(''.join(DEC[c] for c in current_encoded))
print(f"Current beat points: {current_value}")

#preserve orig digit length 
original_digits = len(current_encoded)
print(f"Detected digit capacity: {original_digits}")

#input new val
new_bp = int(input("Enter new beat points value: "))

if len(str(new_bp)) > original_digits:
    print(f"ERROR: Value too large! Max is {int('9'*original_digits)}")
    exit(1)

#pad to exact orig length
padded = str(new_bp).zfill(original_digits)

#encode
new_encoded = bytearray()
for d in padded:
    new_encoded.append(ord(ENC[d]))
    new_encoded.append(0x03)

#sanity check
if len(new_encoded) != (value_end - value_start):
    print("ERROR: Length mismatch! Aborting to prevent corruption.")
    exit(1)

#replace
dec[value_start:value_end] = new_encoded

#reencrypt
new_raw = xor(dec)

#write
with open(SAVE_FILE, "wb") as f:
    f.write(new_raw)

print(f"Done! Beat points set to {new_bp}.")