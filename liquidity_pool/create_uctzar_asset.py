from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from typing import Dict, Any


algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)

total_supply = 100000000000
asset_name = "UCTZAR"
asset_unit = "UCTZAR"

def issue_asa(address, private_key):
#Transaction set up - creating ASA
    sp = algod_client.suggested_params()
    asa_creation_txn = transaction.AssetConfigTxn(
        sender=address,
        sp=sp,
        default_frozen=False,
        unit_name=asset_unit,
        asset_name=asset_name,
        manager=address,
        reserve=address,
        freeze=address,
        clawback=address,
        total=total_supply,
        decimals=2,
    )


    #signing the transaction
    signed_txn = asa_creation_txn.sign(private_key)

    #send transaction
    txid = algod_client.send_transaction(signed_txn)
    print(f"Sent asset create transaction with txid: {txid}")

    results = transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"Result confirmed in round: {results['confirmed-round']}")

    #retrieve asset
    created_asset = results["asset-index"]
    print(f"Asset ID created: {created_asset}")

    #Asset information
    asset_info = algod_client.asset_info(created_asset)
    asset_params: Dict[str, Any] = asset_info["params"]
    print(f"Asset Name: {asset_params['name']}")
    print(f"Asset params: {list(asset_params.keys())}")

def destroy_asa(asa_id, manager_account, manager_account_privatekey):
    params = algod_client.suggested_params()

    delete_txn = transaction.AssetConfigTxn(
        sender=manager_account,
        sp=params,
        index=asa_id,
        strict_empty_address_check=False
    )

    signed_delete_txn = delete_txn.sign(manager_account_privatekey)

    txid = algod_client.send_transaction(signed_delete_txn)
    print(f"Asset deletion transaction sent with ID: {txid}")

    from algosdk.v2client import wait_for_confirmation
    wait_for_confirmation(algod_client, txid)
    print("ASA successfully deleted!")


if __name__ == "__main__":

    #details for simulation account

    # Private key: UbcuSgcYZm+/t3WsMuvxHWFiwdiJB2H3oXlrij14fUUUyrzvgAm6b7vZCJojpy/SXwDj0h+nTbUNDJ67BerIWg== 
    # Algo address: CTFLZ34ABG5G7O6ZBCNCHJZP2JPQBY6SD6TU3NINBSPLWBPKZBNLQZ5TMY
    # Mnemonic phrase: tuition river pink lesson slow swift sadness interest few proud wedding balcony shadow core excite always umbrella march rubber pluck kitchen fun cloud able actor

    mnemonic_main_address = "tuition river pink lesson slow swift sadness interest few proud wedding balcony shadow core excite always umbrella march rubber pluck kitchen fun cloud able actor"
    private_key = mnemonic.to_private_key(mnemonic_main_address)
    address = account.address_from_private_key(private_key)
    print(f"Address: {address}")

    issue_asa(address, private_key)
    
    
    # destroy_asa(1, address, private_key)