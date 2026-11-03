import time
from web3 import Web3

url = "https://api.avax.network/ext/bc/C/rpc"
w3 = Web3(Web3.HTTPProvider(url))

uni = "0x9e5A52f57b3038F1B8EeE45F28b3C1967e22799C"

topic = "0x" + Web3.keccak(text="PairCreated(address,address,address,uint256)").hex()

def check(last_check, to_block):

    logs = w3.eth.get_logs({
        'fromBlock': last_check,
        'toBlock': to_block,
        'address': uni,
        'topics': [topic]
    })

    for log in logs:
        token0 = '0x' + log['topics'][1].hex()[-40:]
        token1 = '0x' + log['topics'][2].hex()[-40:]
        pair = '0x' + log['data'].hex()[2:][24:64]
        print(f"пул: {pair}")
        print(f"Token0: {token0}")
        print(f"Token1: {token1}")

last_check = w3.eth.block_number
while True:
    try: 
        latest = w3.eth.block_number
        if latest > last_check:         
            to_block = min(latest, last_check + 4)
            print(f"проверка блоков {last_check} - {to_block}")
            check(last_check, to_block)
            last_check = to_block + 1
        time.sleep(3)  

    except KeyboardInterrupt:
        break
