from algosdk import account, encoding, mnemonic, transaction


def generate_user_accounts():
    for i in range(0,5):
        #generate accounts
        private_key, address = account.generate_account()
        mnemonic_phrase = mnemonic.from_private_key(private_key)

        # Print details to terminal
        print(f"Private key: {private_key} \nAlgo address: {address}\nMnemonic phrase: {mnemonic_phrase}" )

        #Check address validity
        if encoding.is_valid_address(address):
            print("The address is valid!")
        else:
            print("The address is invalid.")

def generate_stokvel_account(threshold: int, signing_accounts: list):
    version = 1

    msig_stokvel_account = transaction.Multisig(
        version=version,
        threshold=threshold,
        addresses=signing_accounts
    )

    return msig_stokvel_account.address()


if __name__ == "__main__":
    accounts = {
    "account_1": {
        "private_key": "3hIxq5CXSjGuyDl+hZdD+imrR/EivudcfVz1W7c2m1KCreZWcwliZ05gBtpPxrMKLVIr5MJjalOctavXz+wjAg==",
        "algo_address": "QKW6MVTTBFRGOTTAA3NE7RVTBIWVEK7EYJRWUU44WWV5PT7MEMBBZB3WEM",
        "mnemonic_phrase": "forward session few jungle news middle earth degree quit fun canyon panic film faint bleak sail ostrich voice purchase satisfy huge soap network able resemble"
    },
    "account_2": {
        "private_key": "25fqTbgXnGGbQy2Xa7aRxHgTGy7Sytmwwdu4MVrAKfahK3xKRD57mhCOjKp7/bTXIG/N5jg9nFy3rslGjhkE/A==",
        "algo_address": "UEVXYSSEHZ5ZUEEORSVHX7NU24QG7TPGHA6ZYXFXV3EUNDQZAT6DD4NCMM",
        "mnemonic_phrase": "window prevent cheap knee deal such broom coil indicate super emotion middle cheap man multiply skull brass almost hospital breeze refuse hybrid rally abstract dragon"
    },
    "account_3": {
        "private_key": "Vo2Hla6Vxs7nPVVuwQnXg1Dfqn0Ypirlk82TlRMOOz4DNvCw10SiAzpEbTAJ/WO7Rfzot4XB/1ovPp2eDkLsrQ==",
        "algo_address": "AM3PBMGXISRAGOSENUYAT7LDXNC7Z2FXQXA76WRPH2OZ4DSC5SW2TCBHNI",
        "mnemonic_phrase": "print bullet enlist foot minor victory upset festival column check twist amused salt height sentence plastic pipe exhibit traffic float cheese seminar vault ability stomach"
    },
    "account_4": {
        "private_key": "krGcFTi3S4o3qSC+1x5ay4b3kgclSfpAtUWMAJF774pAftvxJshiRAg5JEEpuD8e9ahOEOKdeWcdy5djzFerWA==",
        "algo_address": "IB7NX4JGZBREICBZERASTOB7D322QTQQ4KOXSZY5ZOLWHTCXVNME5J26X4",
        "mnemonic_phrase": "crane index approve inform number tip endless camera water kitten public hole upper tool choice empty butter steak carpet angle capital ten first above slogan"
    },
    "account_5": {
        "private_key": "QF1nqBYrLrZo63PnwjrQrj45T2bVsl81jaLdDl9aX9rPvg/TL7DjU1907HF0iT5RNVbZQsS9b2ZMXAveV+nAXA==",
        "algo_address": "Z67A7UZPWDRVGX3U5RYXJCJ6KE2VNWKCYS6W6ZSMLQF54V7JYBOCAFUINQ",
        "mnemonic_phrase": "pool output feature ramp fox collect forget initial friend twelve gym turtle include need private ready program crumble spend universe safe story spray absorb bone"
        }
    }

    addresses = []
    for acc, details in accounts.items():
        address = details["algo_address"]
        addresses.append(address)
    
    print(addresses)

    stokvel_address = generate_stokvel_account(4, addresses)
    print(stokvel_address)

