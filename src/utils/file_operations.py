'''Utility functions for file operations.'''
from src.utils.logger_config import logger
from src.models.wallet import Wallet
import json
from web3 import Web3


# Read a file and return its contents as a list of lines.
def read_file(file_name: str) -> list:
    try:
        with open(f'./user_data/{file_name}.txt', 'r', encoding='UTF-8') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        logger.error('"{file_name}.txt" file or directory not found')
        raise FileNotFoundError
    

# Load wallet data from files and create Wallet objects.
def load_wallets_data() -> list[Wallet]:
    private_keys = read_file('wallets')
    proxies = read_file('proxies')
    recipients = read_file('recipients')

    # Validate equal file lengths.
    if not len(private_keys) == len(proxies) == len(recipients):
        logger.error('The number of private keys, proxies, and recipient addresses must be the same')
        raise ValueError

    # Create Wallet objects.
    wallets = []
    for i, private_key in enumerate(private_keys):
        try:
            # Validate recipient address
            Web3.to_checksum_address(recipients[i])
            
            wallet = Wallet(
                private_key=private_key,
                recipient_address=recipients[i],
                proxy=proxies[i]
            )
            wallets.append(wallet)
        except ValueError as e:
            logger.error(f'Invalid recipient address: {recipients[i]}. Error: {e}')
            # Skip this wallet
            continue
    return wallets


# Load a contract ABI from a JSON file.
def load_contract_abi(file_name: str) -> dict:
    try:
        with open(f'./global_data/{file_name}.json', 'r', encoding='UTF-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error('"{file_name}.json" contract abi file not found')
        raise FileNotFoundError
    except json.JSONDecodeError:
        logger.error('Invalid JSON format in ABI file: "{file_path}.json"')
        raise ValueError
