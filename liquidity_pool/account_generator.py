from algosdk import account, encoding, mnemonic

#generate account
private_key, address = account.generate_account()
mnemonic_phrase = mnemonic.from_private_key(private_key)

# Print details to terminal
print(f"Private key: {private_key} \nAlgo address: {address}\nMnemonic phrase: {mnemonic_phrase}" )

#Check address validity
if encoding.is_valid_address(address):
    print("The address is valid!")
else:
    print("The address is invalid.")