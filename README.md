web3 API
==========

## Installation

Require Python 3.8+


To install the dependencies
```
pip install -r requirements.txt
```

## Run

```
python api/app.py
```

## Endpoints

Create Wallet
 
POST http://127.0.0.1:4000/create_wallet

Create NFT

POST http://127.0.0.1:4000/contract_function_call

Arguments
```
{
    "contract_address":"0xaB81fFeB4aF5f90C6c85fe572f51DEEe5B12C792",
    "args":[<usser wallet to recive the NFT>, <NFT id>],
    "tx_args":{
        "sender_address": <contract owner wallet>,
        "sender_private_key": <contract owner private key>
    }
}
```


  
