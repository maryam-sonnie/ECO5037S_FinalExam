from pyteal import *
import streamlit as st

# region data

# algo_pool_balance = 0
# uctzar_pool_balance = 0

# allocated_liquidity_tokens = {}
# total_liquidity_tokens = 0

# all_transaction_fees = 0

ALGO_TO_UCTZAR_RATE = 2
UCTZAR_TO_ALGO_RATE = 0.5

# endregion

# region Transactions
def opt_in():
    pass
def add_liquidity(lp_user, algo_amount, uctzar_amount, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, allocated_liquidity_tokens, algo_transaction_fees, uctzar_transaction_fees):
    
    if uctzar_amount != algo_amount*2:
        print("RATIO ERROR: uctzar_amount must be 2x algo_amount")    
    else:
        #calculate tokens to assign based on existing tokens in pool
        if total_liquidity_tokens == 0:
            issued_tokens = algo_amount
        else:
            issued_tokens = (algo_amount*total_liquidity_tokens)//total_liquidity_tokens
        
        #update balances
        algo_pool_balance += algo_amount
        uctzar_pool_balance += uctzar_amount
        total_liquidity_tokens += issued_tokens

        #update the lproviders token balance

        if lp_user not in allocated_liquidity_tokens:
            allocated_liquidity_tokens[lp_user] = issued_tokens
        else:
            allocated_liquidity_tokens[lp_user] += issued_tokens
    
    st.write(f"allocated_liquidity_tokens: {allocated_liquidity_tokens}")
    st.write(f"algo_pool_balance: ", algo_pool_balance)
    st.write(f"uctzar_pool_balance: ", uctzar_pool_balance)
    st.write(f"total liq tokens {total_liquidity_tokens}")
    st.write(f"algo fees: {algo_transaction_fees}")
    st.write(f"uctzar transaction fees: {uctzar_transaction_fees}")
    
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

        st.write(f"provider share {provider_share}")

        algo_incentive = provider_share*algo_transaction_fees
        uctzar_incentive = provider_share*uctzar_transaction_fees

        st.write("Incentives")
        st.write(algo_incentive)
        st.write(uctzar_incentive)

        #calculate withdrawal amounts
        algo_amount_withdrawed = lp_tokens_to_redeem*1#(lp_tokens_to_redeem*algo_pool_balance)//total_liquidity_tokens
        uctzar_amount_withdrawed = lp_tokens_to_redeem*2#((lp_tokens_to_redeem*uctzar_pool_balance)//total_liquidity_tokens) #the ratio is 1A:2U

        st.write(f"withdrawed amounts: uctzar {uctzar_amount_withdrawed} algos {algo_amount_withdrawed}")

        #update pool balances

        algo_pool_balance -= (algo_amount_withdrawed+algo_incentive)
        uctzar_pool_balance -= (uctzar_amount_withdrawed+uctzar_incentive)

        #update the accumulated transaction fees
        algo_transaction_fees -= algo_incentive
        uctzar_transaction_fees -= uctzar_incentive

        #update poool tokens
        total_liquidity_tokens -= lp_tokens_to_redeem

        #clear tokens allocated to user
        allocated_liquidity_tokens[lp_user] -= lp_tokens_to_redeem

        st.write(f"allocated_liquidity_tokens: {allocated_liquidity_tokens}")
        st.write(f"algo_pool_balance: ", algo_pool_balance)
        st.write(f"uctzar_pool_balance: ", uctzar_pool_balance)
        st.write(f"total liq tokens {total_liquidity_tokens}")
        st.write(f"algo trans fees: {algo_transaction_fees}")
        st.write(f"uctzar transaction fees: {uctzar_transaction_fees}")

    return allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, algo_transaction_fees, uctzar_transaction_fees



def trade_asset(trader, algo_amount, uctzar_amount, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, allocated_liquidity_tokens, algo_trans_fees, uctzar_trans_fees):
    if algo_amount != 0:

        #manage trans fees
        transaction_fee = algo_amount*0.03
        algo_trans_fees += transaction_fee

        st.write(f"transaction fee: {transaction_fee} and total algo fees {algo_trans_fees}")

        #update balances - assuming a trade ALGO -> UCTZAR
        algo_pool_balance += algo_amount

        #calculate the traders resulting amount
        uct_total_amount = (algo_amount - transaction_fee) * ALGO_TO_UCTZAR_RATE
        uctzar_pool_balance -= uct_total_amount


        print(f"traded amounts: uctzar {uct_total_amount} algos {algo_amount}")
        print(f"allocated_liquidity_tokens: {allocated_liquidity_tokens}")
        print(f"algo_pool_balance: ", algo_pool_balance)
        print(f"uctzar_pool_balance: ", uctzar_pool_balance)
        print(f"total liq tokens {total_liquidity_tokens}")
        print(f"algo trans fee: {algo_trans_fees}")


        return uct_total_amount, allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, algo_trans_fees, uctzar_trans_fees


    elif uctzar_amount != 0:
        
        #manage fees
        transaction_fee = uctzar_amount*0.03
        uctzar_trans_fees += transaction_fee

        st.write(f"transaction fee: {transaction_fee} and total uctzar fees {uctzar_trans_fees}")


        #update balances - assuming that it's a trade UCTZAR -> ALGO
        uctzar_pool_balance += uctzar_amount

        #calculate the traders resulting amount
        algo_total_amount = (uctzar_amount - transaction_fee) * UCTZAR_TO_ALGO_RATE
        algo_pool_balance -= algo_total_amount


        print(f"traded amounts: uctzar {algo_total_amount} algos {uctzar_amount}")
        print(f"allocated_liquidity_tokens: {allocated_liquidity_tokens}")
        print(f"algo_pool_balance: ", algo_pool_balance)
        print(f"uctzar_pool_balance: ", uctzar_pool_balance)
        print(f"total liq tokens {total_liquidity_tokens}")
        print(f"uct zar trans fees: {uctzar_trans_fees}")

        return algo_total_amount, allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, algo_trans_fees, uctzar_trans_fees


    else:
       raise ValueError("ERROR: algo_amount or uctzar_amount must be greater than 0")

# endregion

# region Accessors



# endregion

