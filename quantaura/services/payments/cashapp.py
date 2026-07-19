# Cash App integration
CASHAPP_HANDLE = '$111Joshua1984'
def process_payment(amount):
    print(f'Cash App payment request for ${amount} to {CASHAPP_HANDLE}')
    return {'status': 'success'}
