from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from typing import Dict, Any

algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)

ASSET_ID = 728746029
FUNDED_ACCOUNT = "CTFLZ34ABG5G7O6ZBCNCHJZP2JPQBY6SD6TU3NINBSPLWBPKZBNLQZ5TMY"
FUNDED_ACCOUNT_PK =  "UbcuSgcYZm+/t3WsMuvxHWFiwdiJB2H3oXlrij14fUUUyrzvgAm6b7vZCJojpy/SXwDj0h+nTbUNDJ67BerIWg=="
FUNDED_ACCOUNT_MN = "tuition river pink lesson slow swift sadness interest few proud wedding balcony shadow core excite always umbrella march rubber pluck kitchen fun cloud able actor"

ALGO_TO_UCTZAR_RATE = 2
UCTZAR_TO_ALGO_RATE = 0.5

def uctzar_fund(receiver, amount):
    sp_uctzar = algod_client.suggested_params()
    uctzar_fund_trans = transaction.AssetTransferTxn(
        sender=FUNDED_ACCOUNT,
        sp=sp_uctzar,
        receiver=receiver,
        amt=int(amount*100),
        index=ASSET_ID,
        note="uctzar_fund"
    )

    signed_trans = uctzar_fund_trans.sign(FUNDED_ACCOUNT_PK)
    trans_id = algod_client.send_transaction(signed_trans)

    results = transaction.wait_for_confirmation(algod_client, trans_id, 4)
    print(f"Result confirmed in round: {results['confirmed-round']}")


def algofund(receiver, amount):
    sp_algos = algod_client.suggested_params()
    algo_fund_trans = transaction.PaymentTxn(
        sender=FUNDED_ACCOUNT,
        sp=sp_algos,
        receiver=receiver,
        amt=int(amount*1000000),
        note="algo_fund"
    )

    signed_trans = algo_fund_trans.sign(FUNDED_ACCOUNT_PK)
    trans_id = algod_client.send_transaction(signed_trans)

    results = transaction.wait_for_confirmation(algod_client, trans_id, 4)
    print(f"Result confirmed in round: {results['confirmed-round']}")


if __name__ == "__main__":
#    accounts = ["RAXI4AKY7ZLXKTTETIPK4NWEN5K5THZCPAVRYLUF2WNXEBDCXZEPFXKJEM","3L7ZAJZJA5UNPATYXVX5RNEO6GKHINZQFWIL3IMQVDFBFANIKTBXOMG3NE", "TLYBGTDLZJT4IQKCXOIKTQN54U2PA4PTPO5G2KZMIBBAHAEGTYGK467AXY"]
    accounts = ["3L7ZAJZJA5UNPATYXVX5RNEO6GKHINZQFWIL3IMQVDFBFANIKTBXOMG3NE"]

    for acc in accounts:
        print("funding algos")
        algofund(acc, 5)

        print("funding uctzar")
        uctzar_fund(acc, 10)

    