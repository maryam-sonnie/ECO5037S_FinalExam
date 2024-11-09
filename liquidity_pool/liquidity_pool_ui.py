import streamlit as st
import liquidity_pool as lp_aux

# region data



#update session state:
def update_session_state(variable, new_value):
    st.session_state[variable] = new_value

# addint to session state:
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


algo_pool_balance = st.session_state.algo_pool_balance
uctzar_pool_balance = st.session_state.uctzar_pool_balance

allocated_liquidity_tokens = st.session_state.allocated_liquidity_tokens
total_liquidity_tokens = st.session_state.total_liquidity_tokens

algo_transaction_fees = st.session_state.algo_transaction_fees
uctzar_transaction_fees = st.session_state.uctzar_transaction_fees

ALGO_TO_UCTZAR_RATE = 2
UCTZAR_TO_ALGO_RATE = 0.5




# endregion

st.title("DEX")

st.text("Add Liquidity:")

user_name = st.text_input("Enter your name:")

algo_amount = st.number_input("Enter ALGO amount", min_value=1, step=1)
uctzar_amount = st.number_input("Enter UCTZAR amount", min_value=1, step=1)

if st.button("Add Liquidity"):
    st.write(f"Liquidity added: {algo_amount} ALGO and {uctzar_amount} UCTZAR")
    (allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens,
      algo_transaction_fees, uctzar_transaction_fees) = lp_aux.add_liquidity(user_name,
                                                                              algo_amount, uctzar_amount,
                                                                                algo_pool_balance, uctzar_pool_balance,
                                                                                  total_liquidity_tokens, 
                                                                                  allocated_liquidity_tokens, 
                                                                                  algo_transaction_fees,
                                                                                    uctzar_transaction_fees)
    
    st.session_state.algo_pool_balance = algo_pool_balance
    st.session_state.uctzar_pool_balance = uctzar_pool_balance
    st.session_state.total_liquidity_tokens = total_liquidity_tokens
    st.session_state.allocated_liquidity_tokens.update(allocated_liquidity_tokens)
    st.session_state.algo_transaction_fees = algo_transaction_fees
    st.session_state.uctzar_transaction_fees = uctzar_transaction_fees

    st.write(allocated_liquidity_tokens)

st.text("Trade:")

trade_option = st.selectbox("Choose trade", ["ALGO to UCTZAR", "UCTZAR to ALGO"])
trade_amount = st.number_input("Enter trade amount", min_value=0.0, step=0.01)

if st.button("Execute Trade"):
    st.write('button pressed')
    if trade_option == "ALGO to UCTZAR":
        st.write(f"Trading {trade_amount} ALGO for UCTZAR...")
        (trade_amount, allocated_liquidity_tokens, algo_pool_balance, 
         uctzar_pool_balance, total_liquidity_tokens, algo_transaction_fees,
           uctzar_transaction_fees) = lp_aux.trade_asset(user_name,
                                                        trade_amount, 0, algo_pool_balance, uctzar_pool_balance, 
                                                        total_liquidity_tokens, allocated_liquidity_tokens, algo_transaction_fees,
                                                          uctzar_transaction_fees)
    elif trade_option == "UCTZAR to ALGO":
        st.write(f"Trading {trade_amount} UCTZAR for ALGO...")
        (trade_amount, allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens, 
        algo_transaction_fees, uctzar_transaction_fees) = lp_aux.trade_asset(user_name, 0, trade_amount, 
                                                                          algo_pool_balance, uctzar_pool_balance,
                                                                            total_liquidity_tokens, allocated_liquidity_tokens, 
                                                                            algo_transaction_fees, uctzar_transaction_fees)
        
    st.write(trade_amount)
    st.session_state.algo_pool_balance = algo_pool_balance
    st.session_state.uctzar_pool_balance = uctzar_pool_balance
    st.session_state.total_liquidity_tokens = total_liquidity_tokens
    st.session_state.allocated_liquidity_tokens = allocated_liquidity_tokens
    st.session_state.algo_transaction_fees = algo_transaction_fees
    st.session_state.uctzar_transaction_fees = uctzar_transaction_fees
st.text("Withdraw Liquidity:")

lp_tokens_to_redeem = st.number_input("Enter LP tokens to redeem", min_value=1, step=1)
if st.button("Withdraw Liquidity"):
    st.write(f"Liquidity withdrawn: {lp_tokens_to_redeem} LP tokens")
    (allocated_liquidity_tokens, algo_pool_balance, uctzar_pool_balance, total_liquidity_tokens,
      algo_transaction_fees, uctzar_transaction_fees) = lp_aux.withdraw_liquidity(user_name, lp_tokens_to_redeem, algo_pool_balance, 
                                                                                  uctzar_pool_balance, total_liquidity_tokens,
                                                                                   allocated_liquidity_tokens,
                                                                                     algo_transaction_fees, uctzar_transaction_fees)
    
    st.session_state.algo_pool_balance = algo_pool_balance
    st.session_state.uctzar_pool_balance = uctzar_pool_balance
    st.session_state.total_liquidity_tokens = total_liquidity_tokens
    st.session_state.allocated_liquidity_tokens = allocated_liquidity_tokens
    st.session_state.algo_transaction_fees = algo_transaction_fees
    st.session_state.uctzar_transaction_fees = uctzar_transaction_fees

