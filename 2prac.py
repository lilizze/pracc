

from decimal import Decimal

from web3 import Web3


w3 = Web3(Web3.HTTPProvider("https://ethereum-rpc.publicnode.com"))

ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"


ROUTER_ABI = [
    {
        "name": "getAmountsOut",
        "type": "function",
        "stateMutability": "view",
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "path", "type": "address[]"},
        ],
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
    },
    { 
        "name": "factory",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "address"}],
    },
]

FACTORY_ABI = [{
    "name": "getPair",
    "type": "function",
    "stateMutability": "view",
    "inputs": [
        {"name": "tokenA", "type": "address"},
        {"name": "tokenB", "type": "address"},
    ],
    "outputs": [{"name": "pair", "type": "address"}],
}]

PAIR_ABI = [
    {
        "name": "getReserves",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [
            {"name": "reserve0", "type": "uint112"},
            {"name": "reserve1", "type": "uint112"},
            {"name": "blockTimestampLast", "type": "uint32"},
        ],
    },
    {
        "name": "token0",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "address"}],
    },
]

router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)


def get_reserves(token_in, token_out):

    factory_address = router.functions.factory().call()
    factory = w3.eth.contract(address=factory_address, abi=FACTORY_ABI)

    pair_address = factory.functions.getPair(token_in, token_out).call()
    if int(pair_address, 16) == 0:
        raise ValueError("Пары для этих токенов не существует")

    pair = w3.eth.contract(address=pair_address, abi=PAIR_ABI)
    reserve0, reserve1, _ = pair.functions.getReserves().call()
    token0 = pair.functions.token0().call()

    if token0.lower() == token_in.lower():
        return reserve0, reserve1
    return reserve1, reserve0


def get_amount_out(amount_in, token_in, token_out, decimals_in, decimals_out):

    amount_in_raw = int(Decimal(str(amount_in)) * 10**decimals_in)

    amounts = router.functions.getAmountsOut(amount_in_raw, [token_in, token_out]).call()
    amount_out_raw = amounts[-1]

    reserve_in, reserve_out = get_reserves(token_in, token_out)
    spot_price = Decimal(reserve_out) / Decimal(reserve_in)
    ideal_out_raw = Decimal(amount_in_raw) * Decimal("0.997") * spot_price
    price_impact = (1 - Decimal(amount_out_raw) / ideal_out_raw) * 100
    return amount_out_raw / 10**decimals_out, price_impact


# ----------------------------------------------------------------------------
# Вызов
# ----------------------------------------------------------------------------

WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

result, impact = get_amount_out(645647, WETH, USDC, 18, 6)
print(f"754 WETH -> {result:.4f} USDC")
print(f"Price impact: {impact:.4f}%")
