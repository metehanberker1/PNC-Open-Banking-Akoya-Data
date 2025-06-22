import requests

base_url = "https://sandbox.api.yodlee.com/ysl"
client_id = "7ySPE...."
client_secret = "oISaaw...."
username = "sbMem...."


# Authentication
def get_yodlee_access_token():
    # Endpoint for authentication
    auth_url = f"{base_url}/auth/token"

    # Request headers
    headers = {
        "Api-Version": "1.1", "loginName": "sbMem....",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Request payload
    payload = f"clientId={client_id}&secret={client_secret}"
    # Sending POST request to get the authentication token
    response = requests.post(auth_url, headers=headers, data=payload)

    # Raise an exception for HTTP errors
    response.raise_for_status()

    # Parse JSON response
    token_data = response.json()
    print("Authentication Successful!")
    print("Token:", token_data.get("token"))
    return response.json().get("token")


# Fetch transactions
def fetch_transactions_yodlee(token):
    tran_url = f"{base_url}/transactions"
    accts_url = f"{base_url}/accounts"
    headers = {
        "Api-Version": "1.1", "loginName": "sbMem....",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {token.get('accessToken')}"
    }
    response_accounts = requests.get(accts_url, headers=headers)
    response_accounts.raise_for_status()
    print(response_accounts.json())
    for account in response_accounts.json().get('account'):
        print(account)
        response_acct_details = requests.get(f'{accts_url}?accountId={account.get("providerAccountId")}', headers=headers)
        response_acct_details.raise_for_status()
        print(response_acct_details.json())
        response_transactions = requests.get(f'{tran_url}?accountId={account.get("providerAccountId")}', headers=headers)
        response_transactions.raise_for_status()
        print(response_transactions.json())
    # return response.json()["transaction"]
    return None


# Analyze spending
def analyze_spending_yodlee(transactions):
    spending_categories = {}
    for txn in transactions:
        category = txn.get("category", "Other")
        amount = txn.get("amount", {}).get("amount", 0)
        spending_categories[category] = spending_categories.get(category, 0) + amount
    return spending_categories


# Generate advice
def generate_financial_advice(spending_analysis):
    advice = []
    for category, total in spending_analysis.items():
        if total > 500:  # Example threshold
            advice.append(f"Reduce your spending in {category}, which is ${total:.2f}.")
    return advice


# Main function
def financial_wellness_solution_yodlee():
    token = get_yodlee_access_token()
    transactions = fetch_transactions_yodlee(token)
    spending_analysis = analyze_spending_yodlee(transactions)
    advice = generate_financial_advice(spending_analysis)
    return advice


# Example usage
if __name__ == "__main__":

    advice = financial_wellness_solution_yodlee()
    print("Financial Wellness Advice:")
    for item in advice:
        print(f"- {item}")
