from src.utils.logger_config import logger
from src.utils.file_operations import load_wallets_data, load_contract_abi
from src.utils.input_handler import get_user_config, shuffle_wallets_if_needed
from src.services.processor import Processor

def main():
    try:
        config = get_user_config()

        wallets = load_wallets_data()

        if config.shuffle_wallets:
            wallets = shuffle_wallets_if_needed(wallets, True)

        usdt_token_abi = load_contract_abi('ERC-20_ABI')

        processor = Processor(config, usdt_token_abi)
        processor.process_wallets(wallets)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")


if __name__ == '__main__':
    main() 