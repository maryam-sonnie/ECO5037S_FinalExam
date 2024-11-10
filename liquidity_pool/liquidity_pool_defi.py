from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from typing import Dict, Any
import streamlit as st

class LiquidityPool:
    # Liquidity Pool Details


    # Private key: Q0KJ2kyV/vUf5825EgT9qsEVlBXAiVmeoYL3kIUsTEWa8BNMa8pnxEFCu5Cpwb3lNPBx83u6bSssQEIDgIaeDA== 
    # Algo address: TLYBGTDLZJT4IQKCXOIKTQN54U2PA4PTPO5G2KZMIBBAHAEGTYGK467AXY
    # Mnemonic phrase: embody celery hood feel wood word decline social fire aware leader boy clog govern absent mean sleep major scout author arctic arctic clerk able disorder



    def __init__(self):
        self.algod_address = "https://testnet-api.algonode.cloud"
        self.algod_token = ""
        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address)

        self.ASSET_ID = 728746029
        self.LIQUIDITY_POOL = "TLYBGTDLZJT4IQKCXOIKTQN54U2PA4PTPO5G2KZMIBBAHAEGTYGK467AXY"
        self.LIQUIDITY_POOL_PK =  "Q0KJ2kyV/vUf5825EgT9qsEVlBXAiVmeoYL3kIUsTEWa8BNMa8pnxEFCu5Cpwb3lNPBx83u6bSssQEIDgIaeDA==" 
        self.LIQUIDITY_POOL_MN = "embody celery hood feel wood word decline social fire aware leader boy clog govern absent mean sleep major scout author arctic arctic clerk able disorder"

        self.ALGO_TO_UCTZAR_RATE = 2
        self.UCTZAR_TO_ALGO_RATE = 0.5


    def asa_opt_in(self, address_mn):

        """
        Allow accounts to opt into using the asset
        """

        address_pk = mnemonic.to_private_key(address_mn)
        suggested = self.algod_client.suggested_params()
        optin_transaction = transaction.AssetOptInTxn(
            sender=account.address_from_private_key(address_pk),
            sp=suggested,
            index=self.ASSET_ID
        )

        signed_optin_transaction = optin_transaction.sign(address_pk)
        trans_id = self.algod_client.send_transaction(signed_optin_transaction)

        results = transaction.wait_for_confirmation(self.algod_client, trans_id, 4)
        print(f"Result confirmed in round: {results['confirmed-round']}")


    def add_liquidity(self, lp_account, lp_mn, algo_amount, uctzar_amount, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, allocated_liquidity_tokens, algo_transaction_fees, uctzar_transaction_fees):
        
        print("inside add liq function")

        if uctzar_amount != algo_amount*2:
            print("RATIO ERROR: uctzar_amount must be 2x algo_amount")    
        else:
            #calculate tokens to assign based on existing tokens in pool
            if total_liquidity_tokens == 0:
                issued_tokens = algo_amount
            else:
                issued_tokens = (algo_amount*total_liquidity_tokens)//total_liquidity_tokens #issued_tokens = (algo_amount * total_liquidity_tokens) // algo_pool_balance
            
            #update balances and create Algorand BC transactions
            print(issued_tokens)
            
            try:
                #transaction to transfer algos

                print("Sender:", lp_account)
                print("Receiver:", self.LIQUIDITY_POOL)
                print("Amount:", algo_amount)

                try:
                    sp_algos = self.algod_client.suggested_params()
                    algo_add_liquidity_trans = transaction.PaymentTxn(
                        sender=lp_account,
                        sp=sp_algos,
                        receiver= self.LIQUIDITY_POOL,
                        amt=int(algo_amount*1000000) #this is important
                    )
                except Exception as e:
                    print(e)
                    print('coulndt create first transaction')

                print(algo_add_liquidity_trans)
                print("created algo transaction")


                #transaction to transfer uctzar
                sp_uctzar = self.algod_client.suggested_params()
                uctzar_add_liquidity_trans = transaction.AssetTransferTxn(
                    sender=lp_account,
                    sp=sp_uctzar,
                    receiver=self.LIQUIDITY_POOL,
                    amt=int(round(uctzar_amount*100, 0)),
                    index=self.ASSET_ID,
                    note="LP"
                )

                print("created uctzar transaction")
                print(uctzar_add_liquidity_trans)

                #atomic transaction
                atomic_group_trans_id = transaction.assign_group_id([algo_add_liquidity_trans, uctzar_add_liquidity_trans])
                algo_trans_signed = algo_add_liquidity_trans.sign(private_key=mnemonic.to_private_key(lp_mn))

                uctzar_trans_signed = uctzar_add_liquidity_trans.sign(private_key=mnemonic.to_private_key(lp_mn))
                
                signed_group = [algo_trans_signed, uctzar_trans_signed]
                group_send_id = self.algod_client.send_transactions(signed_group)

                print("sent group transaction")

                result: Dict[str, Any] = transaction.wait_for_confirmation(self.algod_client, group_send_id, 4)
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
            except Exception as e:
                print(e)
                raise Exception
        
        st.write(f"allocated_liquidity_tokens: {allocated_liquidity_tokens}")
        st.write(f"algo_pool_balance: ", algo_pool_balance)
        st.write(f"uctzar_pool_balance: ", uctzar_pool_balance)
        st.write(f"total liq tokens {total_liquidity_tokens}")
        st.write(f"algo fees: {algo_transaction_fees}")
        st.write(f"uctzar transaction fees: {uctzar_transaction_fees}")
        
        return allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, algo_transaction_fees, uctzar_transaction_fees

    def withdraw_liquidity(self, lp_user, lp_tokens_to_redeem, algo_pool_balance, uctzar_pool_balance, 
                        total_liquidity_tokens, allocated_liquidity_tokens, algo_transaction_fees, uctzar_transaction_fees):
        

        if lp_user not in allocated_liquidity_tokens:
            st.error("ERROR: Your account does not have any liquidity tokens allocated", icon="🚫")
        
        if lp_tokens_to_redeem > allocated_liquidity_tokens[lp_user]:
            st.error("ERROR: You do not have enough liquidity tokens (stake) to redeem this amount", icon="🚫")
        
        else:
            #calculate share of fees profits 
            # assuming that the provider has entered a valid amount (their account exists and they have enough tokens to redeem)
            provider_share = lp_tokens_to_redeem/total_liquidity_tokens

            print('test-1')

            # st.write(f"provider share {provider_share}")

            algo_incentive = provider_share*algo_transaction_fees
            uctzar_incentive = provider_share*uctzar_transaction_fees

            print('test0')

            # st.write("Incentives")
            # st.write(algo_incentive)
            # st.write(uctzar_incentive)

            #calculate withdrawal amounts
            algo_amount_withdrawn = (lp_tokens_to_redeem*algo_pool_balance)//total_liquidity_tokens
            uctzar_amount_withdrawn = ((lp_tokens_to_redeem*uctzar_pool_balance)//total_liquidity_tokens) #the ratio is 1A:2U

            print('test0.5')

            total_algos = algo_amount_withdrawn + algo_incentive
            total_uctzar = uctzar_amount_withdrawn + uctzar_incentive

            print((round(total_algos*1000000), 0))
            print((round(total_uctzar*100), 0))


            # st.write(f"withdrawed amounts: uctzar {uctzar_amount_withdrawed} algos {algo_amount_withdrawed}")

            #Withdraw from LIQUIDITY POOL

            #transaction to transfer algos
            sp_algos = self.algod_client.suggested_params()
            algo_withdraw_liquidity_trans = transaction.PaymentTxn(
                sender=self.LIQUIDITY_POOL,
                sp=sp_algos,
                receiver=lp_user,
                amt=int(round(total_algos*1000000, 0)),
                note="LP_WITHDRAW"
            )

            print('test1')

            #transaction to transfer uctzar
            sp_uctzar = self.algod_client.suggested_params()
            uctzar_withdraw_liquidity_trans = transaction.AssetTransferTxn(
                sender=self.LIQUIDITY_POOL,
                sp=sp_uctzar,
                receiver=lp_user,
                amt=int(round(total_uctzar*100, 0)),
                index=self.ASSET_ID,
                note="LP_WITHDRAW"
            )

            print('test2')

            #atomic transaction
            atomic_group_trans_id = transaction.assign_group_id([algo_withdraw_liquidity_trans, uctzar_withdraw_liquidity_trans])
            
            algo_trans_signed = algo_withdraw_liquidity_trans.sign(self.LIQUIDITY_POOL_PK)
            uctzar_trans_signed = uctzar_withdraw_liquidity_trans.sign(self.LIQUIDITY_POOL_PK)
            
            signed_group = [algo_trans_signed, uctzar_trans_signed]
            group_send_id = self.algod_client.send_transactions(signed_group)

            result: Dict[str, Any] = transaction.wait_for_confirmation(self.algod_client, group_send_id, 4)
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

            st.write(f"Total withdrawn liquidity: {total_algos} ALGO and {total_uctzar} UCTZAR")
            st.write(f"allocated_liquidity_tokens: {allocated_liquidity_tokens}")
            st.write(f"algo_pool_balance: ", algo_pool_balance)
            st.write(f"uctzar_pool_balance: ", uctzar_pool_balance)
            st.write(f"total liq tokens {total_liquidity_tokens}")
            st.write(f"algo trans fees: {algo_transaction_fees}")
            st.write(f"uctzar transaction fees: {uctzar_transaction_fees}")

        return allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, algo_transaction_fees, uctzar_transaction_fees, total_algos, total_uctzar, algo_incentive, uctzar_incentive
    

    def trade_asset(self, trader_account, trader_mn, algo_amount, uctzar_amount, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, allocated_liquidity_tokens, algo_trans_fees, uctzar_trans_fees):

        #ensure that the trade does not deplete the liquidity pool of ALGOS
        if algo_amount != 0:

            #manage trans fees
            transaction_fee = algo_amount*0.05
            algo_trans_fees += transaction_fee

            # st.write(f"transaction fee: {transaction_fee} and total algo fees {algo_trans_fees}")

            #update balances - assuming a trade ALGO -> UCTZAR

            #calculate the traders resulting amount
            uct_total_amount = (algo_amount - transaction_fee) * self.ALGO_TO_UCTZAR_RATE

            print('test1')

            #transaction to trade in algos
            sp_algos = self.algod_client.suggested_params()
            algo_trade_in_trans = transaction.PaymentTxn(
                sender=trader_account,
                sp=sp_algos,
                receiver=self.LIQUIDITY_POOL,
                amt=int(algo_amount*1000000),
                note="ALGO_TRADEIN"
            )
            print('test2')

            #transaction to transfer uctzar
            sp_uctzar = self.algod_client.suggested_params()
            uctzar_receive_trans = transaction.AssetTransferTxn(
                sender=self.LIQUIDITY_POOL,
                sp=sp_uctzar,
                receiver=trader_account,
                amt=int(round(uct_total_amount*100, 0)),
                index=self.ASSET_ID,
                note="UCTZAR_RECEIVE"
            )

            print('test3')


            #atomic transaction
            atomic_group_trans_id = transaction.assign_group_id([algo_trade_in_trans, uctzar_receive_trans])

            print('test3.5')
            
            algo_trans_signed = algo_trade_in_trans.sign(mnemonic.to_private_key(trader_mn))
            print('test3.5.1')
            uctzar_trans_signed = uctzar_receive_trans.sign(self.LIQUIDITY_POOL_PK)
            print('test3.5.2')

            print('test4')

            
            signed_group = [algo_trans_signed, uctzar_trans_signed]
            group_send_id = self.algod_client.send_transactions(signed_group)

            print('test5')


            result: Dict[str, Any] = transaction.wait_for_confirmation(self.algod_client, group_send_id, 4)
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
        elif uctzar_amount != 0:
            
            #manage fees
            transaction_fee = uctzar_amount*0.05
            uctzar_trans_fees += transaction_fee

            # st.write(f"transaction fee: {transaction_fee} and total uctzar fees {uctzar_trans_fees}")

            #calculate the traders resulting amount
            algo_total_amount = (uctzar_amount - transaction_fee) * self.UCTZAR_TO_ALGO_RATE

            #transaction to trade in uctzar
            sp_uctzar = self.algod_client.suggested_params()
            uctzar_tradein_trans = transaction.AssetTransferTxn(
                sender=trader_account,
                sp=sp_uctzar,
                receiver=self.LIQUIDITY_POOL,
                amt=int(round(uctzar_amount*100,0)),
                index=self.ASSET_ID,
                note="UCTZAR_TRADEIN"
            )

            #transaction to receive algos
            sp_algos = self.algod_client.suggested_params()
            algo_receive_trans = transaction.PaymentTxn(
                sender=self.LIQUIDITY_POOL,
                sp=sp_algos,
                receiver=trader_account,
                amt=int(algo_total_amount*1000000),
                note="ALGO_RECEIVE"
            )

            #atomic transaction
            atomic_group_trans_id = transaction.assign_group_id([uctzar_tradein_trans, algo_receive_trans])
            
            algo_trans_signed = uctzar_tradein_trans.sign(mnemonic.to_private_key(trader_mn))
            uctzar_trans_signed = algo_receive_trans.sign(self.LIQUIDITY_POOL_PK)
            
            signed_group = [algo_trans_signed, uctzar_trans_signed]
            group_send_id = self.algod_client.send_transactions(signed_group)

            result: Dict[str, Any] = transaction.wait_for_confirmation(self.algod_client, group_send_id, 4)
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



#======================= STREAMLIT UI ===========================#

# region DATA stores and session state set up
if 'algo_pool_balance' not in st.session_state:
    st.session_state.algo_pool_balance = 0
if 'uctzar_pool_balance' not in st.session_state:
    st.session_state.uctzar_pool_balance = 0
if 'allocated_liquidity_tokens' not in st.session_state:
    st.session_state.allocated_liquidity_tokens = {}
if 'total_liquidity_tokens' not in st.session_state:
    st.session_state.total_liquidity_tokens = 0
if 'algo_transaction_fees' not in st.session_state:
    st.session_state.algo_transaction_fees = 0
if 'uctzar_transaction_fees' not in st.session_state:
    st.session_state.uctzar_transaction_fees = 0
if 'selected_action' not in st.session_state:
    st.session_state.selected_action = ""


algo_pool_balance = st.session_state.algo_pool_balance
uctzar_pool_balance = st.session_state.uctzar_pool_balance

allocated_liquidity_tokens = st.session_state.allocated_liquidity_tokens
total_liquidity_tokens = st.session_state.total_liquidity_tokens

algo_transaction_fees = st.session_state.algo_transaction_fees
uctzar_transaction_fees = st.session_state.uctzar_transaction_fees

LiquidityPoolInstance = LiquidityPool()

ALGO_TO_UCTZAR_RATE = LiquidityPoolInstance.ALGO_TO_UCTZAR_RATE
UCTZAR_TO_ALGO_RATE = LiquidityPoolInstance.UCTZAR_TO_ALGO_RATE

# endregion

# region Page Actions Set Up

st.title("Liquidity Pool and DEX Simulation")

st.header("Current Liquidity Pool State:")

st.write(f"Algo Pool Balance: {algo_pool_balance}")
st.write(f"Uctzar Pool Balance: {uctzar_pool_balance}")

st.header("Select Action:")
selected_action = st.selectbox(label= 'Select Action:', options=["", "UCTZAR Opt-in", "Trade Liquidity", "Deposit Liquidity", "Withdraw Liquidity"])

# region OPT IN LOGIC
if selected_action == "UCTZAR Opt-in":
    st.session_state.selected_action = "UCTZAR Opt-in"
    st.header("UCTZAR Opt-in")

    st.write("In this section, you can opt-in to UCTZAR. This will allow you to start using the asset.")

    st.write("Enter your Algorand Account:")
    st.text_input("Account Address:")

    st.write("Enter your account mnemonic and click 'Opt-in' to opt-in to UCTZAR.")
    account_mn = st.text_input("Account mnuemoic:", type="password")

    optin_confirm = st.button("Opt-in")

    if optin_confirm:
        try:
            LiquidityPoolInstance.asa_opt_in(address_mn=account_mn)
            st.success("You have successfully opted in :). You can start receiving and trading UCTZAR.")
        except Exception as e:
            st.error("Error: We could not process your opt in. \nPlease check if you have already opted in or if you have entered a valid mnemonic." )
            print(e)
# endregion

# region ADD LIQ LOGIC
elif selected_action == "Deposit Liquidity":
    st.header("Deposit Liquidity")

    st.write("""In this section, you can provide liquidity. 
             You need to provide a ALGO/UCTZAR trading pair.
             \nFor each ALGO you provide you need to provide 2 UCTZAR assets.""")
    
    algo_amount = st.number_input("Enter ALGO amount")
    uctzar_amount = st.number_input("Enter UCTZAR amount")

    if not (algo_amount * 2 == uctzar_amount):
        st.error("Please enter asset in a 1:2 ratio")
    else:
        st.write("Enter your Algorand Account:")
        lp_account = st.text_input("Account Address:")

        st.write("Enter your account mnemonic")
        account_mn = st.text_input("Account mnuemoic:", type="password")

        deposit_liquidity = st.button("Confirm Liquidity Deposit")
        if deposit_liquidity:
            st.write(f"Liquidity added: {algo_amount} ALGO and {uctzar_amount} UCTZAR")
            try:
                (allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens,
                algo_transaction_fees, uctzar_transaction_fees) = LiquidityPoolInstance.add_liquidity(
                                                                                        lp_account=lp_account,
                                                                                        lp_mn=account_mn,
                                                                                        algo_amount=algo_amount,
                                                                                        uctzar_amount=uctzar_amount,
                                                                                        algo_pool_balance=algo_pool_balance,
                                                                                        uctzar_pool_balance=uctzar_pool_balance,
                                                                                        total_liquidity_tokens=total_liquidity_tokens,
                                                                                        allocated_liquidity_tokens=allocated_liquidity_tokens,
                                                                                        algo_transaction_fees=algo_transaction_fees,
                                                                                        uctzar_transaction_fees=uctzar_transaction_fees
                                                                                    )
                

                st.session_state.algo_pool_balance = algo_pool_balance
                st.session_state.uctzar_pool_balance = uctzar_pool_balance
                st.session_state.total_liquidity_tokens = total_liquidity_tokens
                st.session_state.allocated_liquidity_tokens.update(allocated_liquidity_tokens)
                st.session_state.algo_transaction_fees = algo_transaction_fees
                st.session_state.uctzar_transaction_fees = uctzar_transaction_fees

                st.success(
                    f"""Liquidity added: {algo_amount} ALGO and {uctzar_amount} UCTZAR\n",
                    Your Liquidity Pool stake: {(allocated_liquidity_tokens[lp_account]/total_liquidity_tokens)*100}%\n
                    Your Liquidity Tokens issued: {allocated_liquidity_tokens[lp_account]}\n
                    (correspoinding to the number of ALGO you provided):
                    """,

                    icon="✅",
                )
            
            except Exception as e:
                st.error("""Error: We could not process your liquidity addition. 
                         \nPlease check if your mnemonic is valid or that you have sufficient funds""",
                          icon="🚫")
                print(e)
# endregion

# region TRADE LOGIC
elif selected_action == "Trade Liquidity":
    st.header("Trade Liquidity")

    st.write("""In this section, you can trade ASSETS.""")
    st.write("""Please note: A 5% Transaction fee is added onto each transaction by this platform.""")

    st.write("Enter your Algorand Account:")
    lp_account = st.text_input("Account Address:")

    st.write("Enter your account mnemonic")
    account_mn = st.text_input("Account mnuemoic:", type="password")


    st.write("ASSET TRADE DETAILS:")

    trade_option = st.selectbox("Choose asset trade:", ["ALGO to UCTZAR", "UCTZAR to ALGO"])
    trade_amount = st.number_input("Enter trade amount")

    if st.button("Execute Trade"):
        try:
            if trade_option == "ALGO to UCTZAR":
                st.write(f"Trading {trade_amount} ALGO for UCTZAR...")
                (trade_amount, allocated_liquidity_tokens, algo_pool_balance, 
                uctzar_pool_balance, total_liquidity_tokens, algo_transaction_fees,
                uctzar_transaction_fees) = LiquidityPoolInstance.trade_asset(lp_account, account_mn,
                                                                trade_amount, 0, algo_pool_balance, uctzar_pool_balance, 
                                                                total_liquidity_tokens, allocated_liquidity_tokens, algo_transaction_fees,
                                                                uctzar_transaction_fees)
                
            elif trade_option == "UCTZAR to ALGO":
                st.write(f"Trading {trade_amount} UCTZAR for ALGO...")
                (trade_amount, allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, 
                algo_transaction_fees, uctzar_transaction_fees) = LiquidityPoolInstance.trade_asset(lp_account, account_mn, 0, trade_amount, 
                                                                                algo_pool_balance, uctzar_pool_balance,
                                                                                    total_liquidity_tokens, allocated_liquidity_tokens, 
                                                                                    algo_transaction_fees, uctzar_transaction_fees)
        

            st.success(
                f"""Your {trade_option} Trade was successful\n
                    Amount Deposited into your account: {trade_amount} {trade_option.split(" ")[2]}                    
                """,
                icon="✅",
            )

            #update global pool balances:

            st.session_state.algo_pool_balance = algo_pool_balance
            st.session_state.uctzar_pool_balance = uctzar_pool_balance
            st.session_state.total_liquidity_tokens = total_liquidity_tokens
            st.session_state.allocated_liquidity_tokens = allocated_liquidity_tokens
            st.session_state.algo_transaction_fees = algo_transaction_fees
            st.session_state.uctzar_transaction_fees = uctzar_transaction_fees

        except Exception as e:
            st.error("""Error: We could not process your trade. 
                         \nPlease check if your mnemonic is valid or that you have sufficient funds""",
                      icon="🚫")
            print(e)
            
# endregion

# region WITHDRAW LOGIC  
elif selected_action == "Withdraw Liquidity":
    st.header("Withdraw Liquidity")

    st.write("Enter your Algorand Account:")
    lp_account = st.text_input("Account Address:")

    st.write("Enter your account mnemonic")
    account_mn = st.text_input("Account mnuemoic:", type="password")

    try:

        st.success(f"""Your Liquidity Pool stake: {(allocated_liquidity_tokens[lp_account]/total_liquidity_tokens)*100}% \n
                    Your total Liquidity Tokens: {allocated_liquidity_tokens[lp_account]}
                    """)


        lp_tokens_to_redeem = st.number_input("Enter LP tokens to redeem:")
        
        if st.button("Withdraw Liquidity"):
            try:
                st.write(f"""Your Liquidity Pool stake: {allocated_liquidity_tokens[lp_account]/total_liquidity_tokens}"""),




                (allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens,
                algo_transaction_fees, uctzar_transaction_fees, total_algos, total_uctzar, algo_incentive, uctzar_incentive) = LiquidityPoolInstance.withdraw_liquidity(
                    lp_account, lp_tokens_to_redeem, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, allocated_liquidity_tokens, algo_transaction_fees, uctzar_transaction_fees)
                
                st.session_state.algo_pool_balance = algo_pool_balance
                st.session_state.uctzar_pool_balance = uctzar_pool_balance
                st.session_state.total_liquidity_tokens = total_liquidity_tokens
                st.session_state.allocated_liquidity_tokens = allocated_liquidity_tokens
                st.session_state.algo_transaction_fees = algo_transaction_fees
                st.session_state.uctzar_transaction_fees = uctzar_transaction_fees

                st.success(
                    f"""Liquidity withdrawn: {total_algos} ALGO and {total_algos} UCTZAR\n",
                    Your profits from transaction fees: {algo_incentive} ALGO and {uctzar_incentive} UCTZAR\n
                    Your Liquidity Pool stake: {(allocated_liquidity_tokens[lp_account]/total_liquidity_tokens)*100}%\n
                    Your Liquidity Tokens issued: {allocated_liquidity_tokens[lp_account]}\n
                    (correspoinding to the number of ALGO you provided):
                    """,

                    icon="✅",
                )

            except Exception as e:
                    st.error("""Error: We could not process your liquidity withdrawal. 
                            \nPlease check if your mnemonic is valid or that you have sufficient funds""",
                            icon="🚫")
                    print(e)
    
    except Exception as e:
        st.error(f"Account {lp_account} does not exist as a Liquidity Provider", icon="🚫")            


# endregion



# endregion





