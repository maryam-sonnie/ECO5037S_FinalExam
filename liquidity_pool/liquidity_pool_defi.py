from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from typing import Dict, Any

# Liquidity Pool Details

# Private key: UbcuSgcYZm+/t3WsMuvxHWFiwdiJB2H3oXlrij14fUUUyrzvgAm6b7vZCJojpy/SXwDj0h+nTbUNDJ67BerIWg== 
# Algo address: CTFLZ34ABG5G7O6ZBCNCHJZP2JPQBY6SD6TU3NINBSPLWBPKZBNLQZ5TMY
# Mnemonic phrase: tuition river pink lesson slow swift sadness interest few proud wedding balcony shadow core excite always umbrella march rubber pluck kitchen fun cloud able actor


algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)

ASSET_ID = 728746029
LIQUIDITY_POOL = "CTFLZ34ABG5G7O6ZBCNCHJZP2JPQBY6SD6TU3NINBSPLWBPKZBNLQZ5TMY"
LIQUIDITY_POOL_PK =  "UbcuSgcYZm+/t3WsMuvxHWFiwdiJB2H3oXlrij14fUUUyrzvgAm6b7vZCJojpy/SXwDj0h+nTbUNDJ67BerIWg==" 

ALGO_TO_UCTZAR_RATE = 2
UCTZAR_TO_ALGO_RATE = 0.5


def asa_opt_in(address_mn):

    """
    Allow accounts to opt into using the asset
    """

    address_pk = mnemonic.to_private_key(address_mn)
    suggested = algod_client.suggested_params()
    optin_transaction = transaction.AssetOptInTxn(
        sender=account.address_from_private_key(address_pk),
        sp=suggested,
        index=ASSET_ID
    )

    signed_optin_transaction = optin_transaction.sign(address_pk)
    trans_id = algod_client.send_transaction(signed_optin_transaction)

    results = transaction.wait_for_confirmation(algod_client, trans_id, 4)
    print(f"Result confirmed in round: {results['confirmed-round']}")


def add_liquidity(lp_account, lp_mn, algo_amount, uctzar_amount, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, allocated_liquidity_tokens, algo_transaction_fees, uctzar_transaction_fees):
    
    if uctzar_amount != algo_amount*2:
        print("RATIO ERROR: uctzar_amount must be 2x algo_amount")    
    else:
        #calculate tokens to assign based on existing tokens in pool
        if total_liquidity_tokens == 0:
            issued_tokens = algo_amount
        else:
            issued_tokens = (algo_amount*total_liquidity_tokens)//total_liquidity_tokens
        
        #update balances and create Algorand BC transactions
        
        #transaction to transfer algos
        sp_algos = algod_client.suggested_params()
        algo_add_liquidity_trans = transaction.PaymentTxn(
            sender=lp_account,
            sp=sp_algos,
            receiver=LIQUIDITY_POOL,
            amt=algo_amount
        )

        #transaction to transfer uctzar
        sp_uctzar = algod_client.suggested_params()
        uctzar_add_liquidity_trans = transaction.AssetTransferTxn(
            sender=lp_account,
            sp=sp_uctzar,
            receiver=LIQUIDITY_POOL,
            amt=uctzar_amount,
            index=ASSET_ID,
            note="LP"
        )

        #atomic transaction
        atomic_group_trans_id = transaction.assign_group_id([algo_add_liquidity_trans, uctzar_add_liquidity_trans])
        algo_trans_signed = algo_add_liquidity_trans.sign(private_key=mnemonic.to_private_key(lp_mn))

        uctzar_trans_signed = uctzar_add_liquidity_trans.sign(private_key=mnemonic.to_private_key(lp_mn))
        
        signed_group = [algo_trans_signed, uctzar_trans_signed]
        group_send_id = algod_client.send_transactions(signed_group)

        result: Dict[str, Any] = transaction.wait_for_confirmation(algod_client, group_send_id, 4)
        print(f"txID: {group_send_id} confirmed in round: {result.get('confirmed-round', 0)}")

        #results - iff successful, update the global variables

        if result:
            algo_pool_balance += algo_amount
            uctzar_pool_balance += uctzar_amount
            total_liquidity_tokens += issued_tokens

            #update the lproviders token balance (allocate stake)
            if lp_account not in allocated_liquidity_tokens:
                allocated_liquidity_tokens[lp_account] = issued_tokens
            else:
                allocated_liquidity_tokens[lp_account] += issued_tokens
        
        else:
            print("Add Liquidity Transaction failed")
    
    # st.write(f"allocated_liquidity_tokens: {allocated_liquidity_tokens}")
    # st.write(f"algo_pool_balance: ", algo_pool_balance)
    # st.write(f"uctzar_pool_balance: ", uctzar_pool_balance)
    # st.write(f"total liq tokens {total_liquidity_tokens}")
    # st.write(f"algo fees: {algo_transaction_fees}")
    # st.write(f"uctzar transaction fees: {uctzar_transaction_fees}")
    
    return allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, algo_transaction_fees, uctzar_transaction_fees

def withdraw_liquidity(lp_user, lp_tokens_to_redeem, algo_pool_balance, uctzar_pool_balance, 
                       total_liquidity_tokens, allocated_liquidity_tokens, algo_transaction_fees, uctzar_transaction_fees):
    if lp_user not in allocated_liquidity_tokens:
        print("ERROR: Your account does not have any liquidity tokens allocated")
    
    if lp_tokens_to_redeem > allocated_liquidity_tokens[lp_user]:
        print("ERROR: You do not have enough liquidity tokens to redeem")
    
    else:
        #calculate share of fees profits 
        # assuming that the provider has entered a valid amount (their account exists and they have enough tokens to redeem)
        provider_share = lp_tokens_to_redeem/total_liquidity_tokens

        # st.write(f"provider share {provider_share}")

        algo_incentive = provider_share*algo_transaction_fees
        uctzar_incentive = provider_share*uctzar_transaction_fees

        # st.write("Incentives")
        # st.write(algo_incentive)
        # st.write(uctzar_incentive)

        #calculate withdrawal amounts
        algo_amount_withdrawn = (lp_tokens_to_redeem*algo_pool_balance)//total_liquidity_tokens
        uctzar_amount_withdrawn = ((lp_tokens_to_redeem*uctzar_pool_balance)//total_liquidity_tokens) #the ratio is 1A:2U

        total_algos = algo_amount_withdrawn + algo_incentive
        total_uctzar = uctzar_amount_withdrawn + uctzar_incentive

        # st.write(f"withdrawed amounts: uctzar {uctzar_amount_withdrawed} algos {algo_amount_withdrawed}")

        #Withdraw from LIQUIDITY POOL

        #transaction to transfer algos
        sp_algos = algod_client.suggested_params()
        algo_withdraw_liquidity_trans = transaction.PaymentTxn(
            sender=LIQUIDITY_POOL,
            sp=sp_algos,
            receiver=lp_user,
            amt=total_algos,
            note="LP_WITHDRAW"
        )

        #transaction to transfer uctzar
        sp_uctzar = algod_client.suggested_params()
        uctzar_withdraw_liquidity_trans = transaction.AssetTransferTxn(
            sender=LIQUIDITY_POOL,
            sp=sp_uctzar,
            receiver=lp_user,
            amt=total_uctzar,
            index=ASSET_ID,
            note="LP_WITHDRAW"
        )

        #atomic transaction
        atomic_group_trans_id = transaction.assign_group_id([algo_withdraw_liquidity_trans, uctzar_withdraw_liquidity_trans])
        
        algo_trans_signed = algo_withdraw_liquidity_trans.sign(LIQUIDITY_POOL_PK)
        uctzar_trans_signed = uctzar_withdraw_liquidity_trans.sign(LIQUIDITY_POOL_PK)
        
        signed_group = [algo_trans_signed, uctzar_trans_signed]
        group_send_id = algod_client.send_transactions(signed_group)

        result: Dict[str, Any] = transaction.wait_for_confirmation(algod_client, group_send_id, 4)
        print(f"txID: {group_send_id} confirmed in round: {result.get('confirmed-round', 0)}")

        #results - iff successful, update the global variables
        if result:
        #update balances
            algo_pool_balance -= (algo_amount_withdrawn+algo_incentive)
            uctzar_pool_balance -= (uctzar_amount_withdrawn+uctzar_incentive)

            #update the accumulated transaction fees
            algo_transaction_fees -= algo_incentive
            uctzar_transaction_fees -= uctzar_incentive

            #update poool tokens
            total_liquidity_tokens -= lp_tokens_to_redeem

            #clear tokens allocated to user
            allocated_liquidity_tokens[lp_user] -= lp_tokens_to_redeem
        
        else:
            print("Withdraw Liquidity Transaction failed")

        # st.write(f"allocated_liquidity_tokens: {allocated_liquidity_tokens}")
        # st.write(f"algo_pool_balance: ", algo_pool_balance)
        # st.write(f"uctzar_pool_balance: ", uctzar_pool_balance)
        # st.write(f"total liq tokens {total_liquidity_tokens}")
        # st.write(f"algo trans fees: {algo_transaction_fees}")
        # st.write(f"uctzar transaction fees: {uctzar_transaction_fees}")

    return allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, algo_transaction_fees, uctzar_transaction_fees
 

def trade_asset(trader_account, trader_mn, algo_amount, uctzar_amount, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, allocated_liquidity_tokens, algo_trans_fees, uctzar_trans_fees):

    #ensure that the trade does not deplete the liquidity pool of ALGOS
    if algo_amount != 0 and algo_amount < algo_pool_balance*0.60:

        #manage trans fees
        transaction_fee = algo_amount*0.05
        algo_trans_fees += transaction_fee

        # st.write(f"transaction fee: {transaction_fee} and total algo fees {algo_trans_fees}")

        #update balances - assuming a trade ALGO -> UCTZAR

        #calculate the traders resulting amount
        uct_total_amount = (algo_amount - transaction_fee) * ALGO_TO_UCTZAR_RATE

        #transaction to trade in algos
        sp_algos = algod_client.suggested_params()
        algo_trade_in_trans = transaction.PaymentTxn(
            sender=trader_account,
            sp=sp_algos,
            receiver=LIQUIDITY_POOL,
            amt=algo_amount,
            note="ALGO_TRADEIN"
        )

        #transaction to transfer uctzar
        sp_uctzar = algod_client.suggested_params()
        uctzar_receive_trans = transaction.AssetTransferTxn(
            sender=LIQUIDITY_POOL,
            sp=sp_uctzar,
            receiver=trader_account,
            amt=uct_total_amount,
            index=ASSET_ID,
            note="LP_WITHDRAW"
        )

        #atomic transaction
        atomic_group_trans_id = transaction.assign_group_id([algo_trade_in_trans, uctzar_receive_trans])
        
        algo_trans_signed = algo_trade_in_trans.sign(trader_mn)
        uctzar_trans_signed = uctzar_receive_trans.sign(LIQUIDITY_POOL_PK)
        
        signed_group = [algo_trans_signed, uctzar_trans_signed]
        group_send_id = algod_client.send_transactions(signed_group)

        result: Dict[str, Any] = transaction.wait_for_confirmation(algod_client, group_send_id, 4)
        print(f"txID: {group_send_id} confirmed in round: {result.get('confirmed-round', 0)}")

        if result:
            algo_pool_balance += algo_amount
            uctzar_pool_balance -= uct_total_amount
        else:
            print("ALGO TRADE IN UNSUCCESSFUL")


        print(f"traded amounts: uctzar {uct_total_amount} algos {algo_amount}")
        print(f"allocated_liquidity_tokens: {allocated_liquidity_tokens}")
        print(f"algo_pool_balance: ", algo_pool_balance)
        print(f"uctzar_pool_balance: ", uctzar_pool_balance)
        print(f"total liq tokens {total_liquidity_tokens}")
        print(f"algo trans fee: {algo_trans_fees}")


        return uct_total_amount, allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, algo_trans_fees, uctzar_trans_fees


    #ensure that the trade does not take all of the UCTZAR asset
    elif uctzar_amount != 0 and uct_total_amount < uctzar_pool_balance*0.60:
        
        #manage fees
        transaction_fee = uctzar_amount*0.05
        uctzar_trans_fees += transaction_fee

        # st.write(f"transaction fee: {transaction_fee} and total uctzar fees {uctzar_trans_fees}")

        #calculate the traders resulting amount
        algo_total_amount = (uctzar_amount - transaction_fee) * UCTZAR_TO_ALGO_RATE

        #transaction to trade in uctzar
        sp_uctzar = algod_client.suggested_params()
        uctzar_tradein_trans = transaction.AssetTransferTxn(
            sender=trader_account,
            sp=sp_uctzar,
            receiver=LIQUIDITY_POOL,
            amt=uctzar_amount,
            index=ASSET_ID,
            note="LP_WITHDRAW"
        )

        #transaction to receive algos
        sp_algos = algod_client.suggested_params()
        algo_receive_trans = transaction.PaymentTxn(
            sender=LIQUIDITY_POOL,
            sp=sp_algos,
            receiver=trader_account,
            amt=algo_total_amount,
            note="ALGO_TRADEIN"
        )

        #atomic transaction
        atomic_group_trans_id = transaction.assign_group_id([algo_trade_in_trans, uctzar_receive_trans])
        
        algo_trans_signed = uctzar_tradein_trans.sign(trader_mn)
        uctzar_trans_signed = algo_receive_trans.sign(LIQUIDITY_POOL_PK)
        
        signed_group = [algo_trans_signed, uctzar_trans_signed]
        group_send_id = algod_client.send_transactions(signed_group)

        result: Dict[str, Any] = transaction.wait_for_confirmation(algod_client, group_send_id, 4)
        print(f"txID: {group_send_id} confirmed in round: {result.get('confirmed-round', 0)}")

        if result:
            #update balances - assuming that it's a trade UCTZAR -> ALGO
            uctzar_pool_balance += uctzar_amount
            algo_pool_balance -= algo_total_amount
        else:
            print("UCTZAR TRADE IN UNSUCCESSFUL")


        print(f"traded amounts: uctzar {algo_total_amount} algos {uctzar_amount}")
        print(f"allocated_liquidity_tokens: {allocated_liquidity_tokens}")
        print(f"algo_pool_balance: ", algo_pool_balance)
        print(f"uctzar_pool_balance: ", uctzar_pool_balance)
        print(f"total liq tokens {total_liquidity_tokens}")
        print(f"uct zar trans fees: {uctzar_trans_fees}")

        return algo_total_amount, allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, algo_trans_fees, uctzar_trans_fees

    else:
       raise ValueError("ERROR: algo_amount or uctzar_amount must be greater than 0")
