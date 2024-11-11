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

        """
        Confirms users as part of the stokvel - allowing for recurring payments and signing the msig
        """

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
        """Checks if all members have consented to recurring payments"""
        return datastore["active"].eq(1).all()
    
    def contributions(self, datastore, transactions, month):

        """
        Runs the contribution cycle - updates the datastore where needed
        """

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
                amt=int(5*1000000) #CHANGE THIS!
            )

            stokvel_signed_txn = stokvel_contribution.sign(address_pk)
            sent_trans = self.algod_client.send_transactions([stokvel_signed_txn])

            print("Waiting for transaction to confirm...")
            print(f"Address {address} has made a contribution of 5 ALGO")

            result = transaction.wait_for_confirmation(self.algod_client, sent_trans, 4)
            print(f"Payment made from account {address} confirmed in round {result['confirmed-round']}")

            transactions.append({"icon": "🟥", "id": sent_trans, "address": address, "amount":5, "type": "CONTRIBUTION", "date": month})

            print(transactions)
            st.session_state.transactions = transactions
    

    def get_receiver(self, datastore):

        """
        Randomly selects the payout receiver
        """

        payout_candidates = []
        for index, row in datastore.iterrows():
            if row["paid_out_counter"] == 0:
                payout_candidates.append(row["address"])
        
        print(payout_candidates)

        chosen_receiver = rd.choice(payout_candidates)
        return chosen_receiver
    
    def create_msig_payment(self, stokvel_address, chosen_receiver):

        """
        Creates the msig payment
        """
        sp = self.algod_client.suggested_params()
        msig_payment = transaction.PaymentTxn(
            sender=stokvel_address,
            sp=sp,
            receiver=chosen_receiver,
            amt=int(15*1000000)#change this as well
        )
        print("selfmsig", self.msig)
        msig_transaction = transaction.MultisigTransaction(msig_payment, self.msig)
        
        return msig_transaction
    
    def get_random_signer(self, datastore):

        """
        Gets four random signers from the stokvel members datastore
        """
        return rd.sample(datastore["address"].tolist(), 4)
    
    
    def sign_multisig(self, mn, msig_transaction):

        """
        Used to sign the multisig
        """

        address_pk = mnemonic.to_private_key(mn)
        msig_transaction.sign(address_pk)
    
    
    def payout_stokvel(self,signed_msig_transaction, chosen_receiver):

        """
        Allows for stokvel payout and updates datastores and transactiions as required
        """

        try:
            payout_transaction = self.algod_client.send_transactions(signed_msig_transaction)
            print(f"Payment made from account {self.msig.address()} to account {chosen_receiver} confirmed in round {payout_transaction['confirmed-round']}")
            transactions.append({"icon": "🟩", "id": payout_transaction, "address": chosen_receiver, "amount":15, "type": "PAYOUT"})
            st.session_state.transactions = (transactions)

            st.write("Completing payout...", icon = "⏳")
            time.sleep(2)
                    
        except Exception as e:
            # Error handling with specific information on failed signatures
            st.error(f"Payment failed: {e} - not enough valid signatures", icon="🚫")
            print("Error details:", e)

    
    def run_stokvel(self, df, transactions, signature_count, stokvel_address):
        if self.check_all_members_active(df):
            st.success("All members have consented to recurring payments\n The contribution cycle with begin", icon="✅")
            
            for month in range(1, 6):
                    
                    st.write(f"⏳Processing contributions from Month: {month}...")
                    

                    print(month)
                    #contributions on day t
                    self.contributions(df, transactions, month)
                    st.success(f"Month: {month}\nContributions from all participants made successfully", icon="✅")

                    #at day t+1
                    #create payout
                    time.sleep(2)
                    receiver = self.get_receiver(df)
                    print("THIS MONTHS RECIEVER:", receiver)

                    print('CREATING MSIG TRANS')

                    # create new multisig transaction
                    msig_transaction = self.create_msig_payment(stokvel_address, receiver)

                    print("created msig = ", msig_transaction)
                    
                    #ensuring that there are at least 4 signatures before the payouts happen
                    while(signature_count < 4):

                        print("SIGNATURE COUNT: ", signature_count)   
                        print("CHECKING SIGNATURES")

                        signers = self.get_random_signer(datastore=df) #random signer - simulates users logging in an signing the stokvel payout
                        
                        for signer in signers:
                            signing_mn = df.loc[df["address"] == signer, "mn"].iloc[0]
                            print(signing_mn)
                            print(signer)
                            try:
                               
                                self.sign_multisig(signing_mn, msig_transaction)

                                signature_count += 1
                                print("SIGNATURE COUNTS: ", signature_count)
                                st.write("Payout signed by: ", signer)
                                st.write("Total signatures: ", signature_count)

                                st.session_state.signature_count = signature_count
                            
                            except Exception as e:
                                print("Could not sign - ERROR ADDRESS:", signer )
                                print(e)
                    
                    if signature_count >= 4:
                        payout_transaction = self.algod_client.send_transaction(msig_transaction)
                        transactions.append({"icon": "🟩", "id": payout_transaction, "address": receiver, "amount":15, "type": "PAYOUT"})
                        st.session_state.transactions = (transactions)

                        st.write("Completing payout...", icon = "⏳")
                        time.sleep(2)                        
                        st.success("Threshold has been reached and payout has been made", icon="✅")
                        signature_count = 0
                        st.session_state.signature_count = signature_count
        else:
            st.error("Some members have not consented to recurring payments", icon="🚫")



       

if __name__ == "__main__":

    st.set_page_config(layout="wide")

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

    st.subheader(f"STOKVEL ADDRESS: {stokvel_instance.msig.address()}")

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
        # df['active'] = 1
        #df['active] = 0

        st.write(stokvel_instance.msig.address())

        st.session_state.datastore = df
        stokvel_instance.run_stokvel(df, transactions, signature_count, stokvel_instance.msig.address())

    
    elif action == "view transactions":

        st.header("View Stokvel Transactions:")

        if not transactions:
            st.error("No transactions have taken place yet", icon="🚫")
        
        else:
            st.table(transactions)

    
    elif action == "leave stokvel":
        st.header("Leave Stokvel:")

        address = st.text_input("Enter your Algorand address:")
        mn = st.text_input("Enter your Mnemonic Phrase:", type = "password")

        if st.button("Opt out of stokvel"):
            df.loc[df["address"] == address, "active"] = 0 # marking that the user is active
            st.session_state.datastore = df
            st.error("You have left the stokvel")
#sign up for stockvel

