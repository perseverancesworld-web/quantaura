# FastAPI playground stub
from fastapi import FastAPI
app = FastAPI(title='Quantaura Playground')
@app.get('/demo')
def demo():
    return {'status': 'Quantaura VM ready with Coinbase/Cash App'}
