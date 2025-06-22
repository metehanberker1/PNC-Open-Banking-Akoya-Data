import requests
import pandas as pd


# Fetch Data from Akoya API
def fetch_akoya_data(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    accounts = requests.get("https://sandbox-products.ddp.akoya.com/accounts-info/v2/mikomo", headers=headers).json()
    transactions = requests.get(f"https://sandbox-products.ddp.akoya.com/transactions/v2/mikomo/{accounts['accounts'][4]['depositAccount']['accountId']}", headers=headers).json()
    income = 0
    expenses = 0
    subscription_keywords = ["Netflix", "Spotify", "Amazon Prime", "Hulu"]
    subscriptions = []

    for account in accounts['accounts']:
        account_type, account_details = next(iter(account.items()))  # Extract the account type and details
        print(f"Account ID: {account_details['accountId']} and Account Type: {account_details['accountType']}")
        print(account)
        transactions = requests.get(
            f"https://sandbox-products.ddp.akoya.com/transactions/v2/mikomo/{account_details['accountId']}?startTime=2020-03-30T04:00:00Z&endTime=2025-06-21T04:00:00Z",
            headers=headers).json()
        print(transactions['transactions'])
        """
        if len(transactions['transactions']) > 0:
            keys = list(transactions['transactions'][0].keys())
            print("Keys in the dictionary:", keys)
            # Extract the nested "investmentTransaction" data
            flattened_data = [item[keys[0]] for item in transactions['transactions']]

            df = pd.DataFrame(flattened_data)

            # Display the dataframe
            # print(df)
            # print(df.info())
            # Check if a specific column exists and get unique values
            column_name = 'transactionType'
            if column_name in df.columns:
                unique_values = df[column_name].unique().tolist()
                print(f"Unique values in '{column_name}' column:", unique_values)
            else:
                print(f"Column '{column_name}' does not exist in the DataFrame.")
        """
        if account_details['accountType'] in ["IRA", "401K", "BROKERAGE"]:
            for txn in transactions['transactions']:
                tx = txn.get("investmentTransaction")
                if tx.get("accountId") == account_details['accountId']:
                    transaction_type = tx.get("transactionType", "").upper()
                    if transaction_type == "SOLD":
                        income += tx.get("amount")
                    elif transaction_type == "PURCHASED":
                        print(tx)
                        expenses += tx.get("amount")

        elif account_details['accountType'] in ["CHECKING", "SAVINGS"]:
            for txn in transactions['transactions']:
                tx = txn.get("depositTransaction")
                print(tx.get("description"))
                if any(kw.lower() in tx.get("description").lower() for kw in subscription_keywords):
                    subscriptions.append(tx)
                if tx.get("accountId") == account_details['accountId']:
                    transaction_type = tx.get("transactionType", "").upper()
                    if transaction_type in ["DEPOSIT", "DIRECTDEPOSIT", "ATMDEPOSIT"]:
                        income += tx.get("amount")
                    elif transaction_type in ["POSDEBIT", "BILLPAYMENT", "TRANSFER", "ATMWITHDRAWAL", "WITHDRAWAL"]:
                        expenses += tx.get("amount")
                        if any(kw.lower() in tx.get("description").lower() for kw in subscription_keywords):
                                subscriptions.append(tx)

        elif account_details['accountType'] == "MORTGAGE":
            for txn in transactions['transactions']:
                tx = txn.get("loanTransaction")
                if tx.get("accountId") == account_details['accountId']:
                    transaction_type = tx.get("transactionType", "").upper()
                    if transaction_type == "PAYMENT":
                        expenses += tx.get("amount")

        elif account_details['accountType'] == "CREDITCARD":
            for txn in transactions['transactions']:
                tx = txn.get("locTransaction")
                print(tx.get("description"))
                if any(kw.lower() in tx.get("description").lower() for kw in subscription_keywords):
                    subscriptions.append(tx)
                if tx.get("accountId") == account_details['accountId']:
                    transaction_type = tx.get("transactionType", "").upper()
                    if transaction_type in ["FEE", "TRANSFER", "WITHDRAWAL"]:
                        expenses += tx.get("amount")
                    elif transaction_type == "DEPOSIT":
                        income += tx.get("amount")

    # return accounts['accounts']
    print(income, expenses, subscriptions)
    return income, expenses, subscriptions


if __name__ == '__main__':
    fetch_akoya_data('eyJhb....')

