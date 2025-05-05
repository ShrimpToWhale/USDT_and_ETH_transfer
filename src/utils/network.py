'''Network-related utility functions.'''
import requests
from web3 import Web3
from web3.exceptions import TimeExhausted
from src.config.constants import arb_explorer_url
from src.utils.logger_config import logger


# Proxy availability check.
def check_proxy(proxy: str) -> str | None:
    if not proxy:
        return None

    try:
        response = requests.get(
            'https://httpbin.org/ip', 
            proxies={
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }, 
            timeout=10
        )

        if response.status_code != 200:
            logger.warning(f'Proxy {proxy} returned status: {response.status_code}, continue without it')
            return None
        else:
            return f'http://{proxy}'
    except Exception as e:
        logger.warning(f'Proxy {proxy} connection failed, continue without it')
        return None


# Create a Web3 instance with optional proxy.
def create_web3_instance(rpc_url: str, proxy: str | None = None) -> Web3:
    if proxy:
        web3 = Web3(Web3.HTTPProvider(
            rpc_url,
            request_kwargs={
                'proxies': {
                    'http': proxy,
                    'https': proxy
                }
            }
        ))
    else:
        web3 = Web3(Web3.HTTPProvider(rpc_url))

    # Check connection.
    if not web3.is_connected():
        raise ConnectionError("Failed to connect to the blockchain RPC endpoint")
    return web3


# Wait for transaction confirmation.
def wait_for_transaction(web3: Web3, tx_hash, operation_type: str) -> bool:
    try:
        logger.info(f'{operation_type} transaction sent, it will take up to 2 minutes to confirm it')
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120, poll_latency=10)

        if receipt['status'] == 1:
            logger.success(f'Successful {operation_type.lower()} transaction: {arb_explorer_url}tx/{tx_hash.hex()}')
            return True
        else:
            logger.error(f'{operation_type} transaction failed: {arb_explorer_url}tx/{tx_hash.hex()}')
            return False

    except TimeExhausted:
        logger.error(f'{operation_type} transaction was not confirmed within 120 seconds')
        return False
    except Exception as e:
        logger.error(f'Unexpected error while waiting for confirmation of {operation_type.lower()} transaction: {e}')
        return False 
