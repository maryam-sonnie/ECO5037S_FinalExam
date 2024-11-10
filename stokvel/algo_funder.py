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

    accounts = ['QKW6MVTTBFRGOTTAA3NE7RVTBIWVEK7EYJRWUU44WWV5PT7MEMBBZB3WEM', 'UEVXYSSEHZ5ZUEEORSVHX7NU24QG7TPGHA6ZYXFXV3EUNDQZAT6DD4NCMM',
      'AM3PBMGXISRAGOSENUYAT7LDXNC7Z2FXQXA76WRPH2OZ4DSC5SW2TCBHNI', 
     'IB7NX4JGZBREICBZERASTOB7D322QTQQ4KOXSZY5ZOLWHTCXVNME5J26X4', 'Z67A7UZPWDRVGX3U5RYXJCJ6KE2VNWKCYS6W6ZSMLQF54V7JYBOCAFUINQ']

    for acc in accounts:
        print("funding algos")
        algofund(acc, 30)


    