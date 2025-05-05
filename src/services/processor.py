import sys
import re

from src.utils.logger_config import logger
from src.models.wallet import Wallet
from src.utils.network import create_web3_instance, check_proxy
from src.utils.input_handler import UserConfig, sleep_between_actions, sleep_between_accounts
from src.services.transfer_service import TransferService
from src.config.constants import arb_rpc_url


class Processor:
    # Processor class initiation
    def __init__(self, config: UserConfig, usdt_token_abi: dict):
        self.config = config
        self.usdt_token_abi = usdt_token_abi

    def process_wallet(self, wallet: Wallet) -> None:
        # Process a single wallet through the full workflow.
        try:
            # Private key format validation.
            if not re.match(r'^(0x)?[a-fA-F0-9]{64}$', wallet.private_key):
                logger.error(f'Invalid private key format: {wallet.get_hidden_key()}')
                return

            logger.info(f'Start work with {wallet.sender_address}')

            proxy_url = check_proxy(wallet.proxy)
            # Web3 instance initiation
            web3 = create_web3_instance(arb_rpc_url, proxy_url)
            
            # Get USDT transfer status.
            transfer_service = TransferService(web3, self.usdt_token_abi)
            
            transfered = transfer_service.transfer_usdt(wallet.sender_address, wallet.recipient_address, wallet.private_key)

            if transfered:
                # Delay between actions.
                sleep_between_actions(self.config.min_action_delay, self.config.max_action_delay)
                transfer_service.transfer_native(wallet.sender_address, wallet.recipient_address, wallet.private_key)
                
        except Exception as e:
            logger.error(f'Error processing wallet {wallet.sender_address}: {str(e)}')
        finally:
            logger.info(f'Finish work with {wallet.sender_address}')

    def process_wallets(self, wallets: list[Wallet]) -> None:
        # Process all wallets.
        logger.info(f'{"=" * 100}')
        logger.info(f'Found {len(wallets)} wallets to process')
        logger.info('=' * 100)

        for i, wallet in enumerate(wallets):
            self.process_wallet(wallet)

            if i < len(wallets) - 1:
                sleep_between_accounts(self.config.min_account_delay, self.config.max_account_delay)

        logger.info(f'{"=" * 100}')
        logger.info(f'Finished processing all {len(wallets)} wallets')
        logger.info(f'{"=" * 100}\n')
