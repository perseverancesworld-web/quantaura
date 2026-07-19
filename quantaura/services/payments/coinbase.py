# Coinbase integration with user ID
COINBASE_ID = '3c348248-3931-5135-a204-c139a35c9598'
def create_charge(amount, currency='USD'):
    print(f'Creating Coinbase charge for ${amount} {currency}')
    return {'id': 'cb-charge-123', 'status': 'pending'}
