import pandas as pd
import streamlit as st

from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from typing import Dict, Any

import random as rd
import time
import asyncio

class Stokvel:



    def __init__(self):
        self.algod_address = "https://testnet-api.algonode.cloud"
        self.algod_token = ""
        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address)
        self.msig = transaction.Multisig(
            version=1,
            threshold=4,
            addresses=['QKW6MVTTBFRGOTTAA3NE7RVTBIWVEK7EYJRWUU44WWV5PT7MEMBBZB3WEM', 'UEVXYSSEHZ5ZUEEORSVHX7NU24QG7TPGHA6ZYXFXV3EUNDQZAT6DD4NCMM',
                        'AM3PBMGXISRAGOSENUYAT7LDXNC7Z2FXQXA76WRPH2OZ4DSC5SW2TCBHNI', 'IB7NX4JGZBREICBZERASTOB7D322QTQQ4KOXSZY5ZOLWHTCXVNME5J26X4',
                         'Z67A7UZPWDRVGX3U5RYXJCJ6KE2VNWKCYS6W6ZSMLQF54V7JYBOCAFUINQ']
        )

    

    def sign_up_detailscapture(self, datastore, address, mn):

        accounts = datastore["address"].tolist()

        if address not in accounts:
            st.error(f"This address {address} has not been approved to join this stokvel.", icon="🚫")
        
        else:
            datastore.loc[datastore["address"] == address, "mn"] = mn  # add their mn to the datastore - marking consent to recurring payments
            datastore.loc[datastore["address"] == address, "active"] = 1  # marking that the user is active

            print(datastore)

            st.success(f"""Your Algorand address {address} has been approved to join this stokvel.\n
                        You have concented to a monthly payment of 5 ALGO for the next 5 Months"\n
                        """, icon="✅")
    

    def check_all_members_active(self, datastore):
        return datastore["active"].eq(1).all()
    
    def contributions(self, datastore, transactions, month):

        print(datastore)

        for index, row in datastore.iterrows():

            address = row["address"]
            mn = row["mn"]

            address_pk = mnemonic.to_private_key(mn)

            sp = self.algod_client.suggested_params()
            stokvel_contribution = transaction.PaymentTxn(
                sender=address,
                sp=sp,
                receiver=self.msig.address(),
                amt=int(1*1_000_000) #CHANGE THIS!
            )

            stokvel_signed_txn = stokvel_contribution.sign(address_pk)
            sent_trans = self.algod_client.send_transactions([stokvel_signed_txn])

            print("Waiting for transaction to confirm...")
            print(f"Address {address} has made a contribution of 5 ALGO")

            result = transaction.wait_for_confirmation(self.algod_client, sent_trans, 4)
            print(f"Payment made from account {address} confirmed in round {result['confirmed-round']}")

            transactions.append({"icon": "🟥", "id": sent_trans, "address": address, "amount":5, "type": "CONTRIBUTION", "date": month})

            st.write(f"Month: {month}")
            st.success(f"Contribution from {address} made successfully", icon="✅")

            print(transactions)
            st.session_state.transactions = transactions
    

    def get_receiver(self, datastore):

        payout_candidates = []
        for index, row in datastore.iterrows():
            if row["paid_out_counter"] == 0:
                payout_candidates.append(row["address"])
        
        print(payout_candidates)

        chosen_receiver = rd.choice(payout_candidates)
        return chosen_receiver
    
    def create_msig_payment(self, stokvel_address, chosen_receiver):
        sp = self.algod_client.suggested_params()
        msig_payment = transaction.PaymentTxn(
            sender=stokvel_address,
            sp=sp,
            receiver=chosen_receiver,
            amt=int(3*1_000_000)#change this as well
        )
        msig_transaction = transaction.MultisigTransaction(msig_payment, self.msig)
        return msig_transaction
    
    
    def sign_multisig(self, mn, msig_transaction):
        address_pk = mnemonic.to_private_key(mn)
        msig_transaction.sign(address_pk)
    
    
    def payout_stokvel(self,signed_msig_transaction, chosen_receiver):
        try:
            payout_transaction = self.algod_client.send_transactions([signed_msig_transaction])
            transactions.append({"icon": "🟩", "id": payout_transaction, "address": chosen_receiver, "amount":15, "type": "PAYOUT"})
            st.session_state.transactions.update(transactions)
            
            st.success("Payment made successfully", icon="✅")
        
        except Exception as e:
            st.error(f"Payment failed: {e} - not enough signatures", icon="🚫")

    
    def run_stokvel(self, df, transactions, signature_counts):
        if stokvel_instance.check_all_members_active(df):
            st.success("All members have consented to recurring payments\n The contribution cycle with begin", icon="✅")
            
            for month in range(1, 6):
                    print(month)
                    stokvel_instance.contributions(df, transactions, month)

                    #at day t+1
                    #create payout

                    time.sleep(2)
                    receiver = self.get_receiver(df)
                    print(receiver)
                    multisig_transaction = self.create_msig_payment(self.msig.address(), receiver)
                    
                    while(signature_counts < 4):
                        signing_account = st.text_input("Enter your address:")
                        signing_mn = st.text_input("Enter your mnemonic:")
                        
                        if st.button("Sign"):
                            stokvel_instance.sign_multisig(signing_mn, multisig_transaction)
                            signature_counts += 1
                            st.session_state.signature_count = signature_counts
                    
                    else:
                        stokvel_instance.payout_stokvel(multisig_transaction, receiver)


        
        
        
        else:
            st.error("Some members have not consented to recurring payments", icon="🚫")



       

if __name__ == "__main__":

    # Initialize session state variables if they don't exist
    st.session_state.datastore = st.session_state.get('datastore', pd.read_excel("./df_test.xlsx"))
    st.session_state.transactions = st.session_state.get('transactions', [])
    st.session_state.signature_count = st.session_state.get('signature_count', 0)
    st.session_state.stokvel_instance = st.session_state.get('stokvel_instance', Stokvel())
    st.session_state.msig_transaction = st.session_state.get('msig_transaction', None)
    st.session_state.chosen_receiver = st.session_state.get('chosen_receiver', None)

    # Assign session state variables to local variables for convenience
    df = st.session_state.datastore
    transactions = st.session_state.transactions
    signature_count = st.session_state.signature_count
    stokvel_instance = st.session_state.stokvel_instance
    msig_transaction = st.session_state.msig_transaction
    chosen_receiver = st.session_state.chosen_receiver   


    st.header("ALGORAND STOKVEL")
    st.subheader("Welcome to the Algogrand stokvel. \nPlease find the constitution below:")

    st.text(
        f"""

        CONSTITUTION\n

        1. Each member must consent to a recurring payment of 5 ALGO for the next 5 months on day t
        2. Each member must sign to the payment of 15 ALGO for the next 5 months on day day t to a random stokvel member
        3. Leaving can only be done after the last payout of 15 ALGO has been made

        """

    )



    actions = ["", "optin", "run stokvel", "view transactions",  "leave stokvel"]
    action = st.selectbox("Select an action", actions)


    if action == "optin":
        st.header("Approve recurring payment into STOKVEL:")

        address = st.text_input("Enter your Algorand address:")
        mn = st.text_input("Enter your Mnemonic Phrase:", type = "password")

        if st.button("Allow recurring payments"):
            stokvel_instance.sign_up_detailscapture(datastore=df, address=address, mn=mn)

    if action == "run stokvel":
        st.subheader('Select action: ')

        #Running the stokvel simulation
        #for testing:
        df['active'] = 1
        #df['active] = 0
        st.session_state.datastore = df
        stokvel_instance.run_stokvel(df, transactions, signature_count)

    
    elif action == "view transactions":

        st.header("View Stokvel Transactions:")

        if not transactions:
            st.error("No transactions have taken place yet", icon="🚫")
        
        else:
            st.table(transactions)


    
    elif action == "leave stokvel":
        st.header("Leave Stokvel:")
        pass

    elif action == "reset all":
        pass
#sign up for stockvel

