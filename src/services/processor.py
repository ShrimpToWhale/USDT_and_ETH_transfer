import sys
import re

from src.utils.logger_config import logger
from src.models.wallet import Wallet
from src.utils.network import create_web3_instance, check_proxy
from src.utils.input_handler import UserConfig, sleep_between_actions, sleep_between_accounts
from src.services.transfer_service import TransferService
from src.config.constants import arb_rpc_url, USDT_CONTRACT_ADDRESS


class Processor:
    # Processor class initiation
    def __init__(self, config: UserConfig, usdt_token_abi: dict):
        self.config = config
        self.usdt_token_abi = usdt_token_abi

    def check_wallet_balances(self, wallet: Wallet) -> tuple[float, float]:
        """Check wallet balances for USDT and ETH."""
        try:
            proxy_url = check_proxy(wallet.proxy)
            web3 = create_web3_instance(arb_rpc_url, proxy_url)
            
            # Check USDT balance
            usdt_contract = web3.eth.contract(
                address=web3.to_checksum_address(USDT_CONTRACT_ADDRESS), 
                abi=self.usdt_token_abi
            )
            usdt_balance = usdt_contract.functions.balanceOf(wallet.sender_address).call()
            usdt_decimals = usdt_contract.functions.decimals().call()
            usdt_balance_human = usdt_balance / (10 ** usdt_decimals)
            
            # Check ETH balance
            eth_balance = web3.eth.get_balance(wallet.sender_address)
            eth_balance_human = web3.from_wei(eth_balance, 'ether')
            
            logger.info(f'Wallet {wallet.sender_address} balances: {usdt_balance_human} USDT, {eth_balance_human} ETH')
            return usdt_balance_human, eth_balance_human
        except Exception as e:
            logger.error(f'Error checking balances for {wallet.sender_address}: {str(e)}')
            return 0, 0

    def process_wallet(self, wallet: Wallet) -> None:
        # Process a single wallet through the full workflow.
        try:
            # Private key format validation.
            if not re.match(r'^(0x)?[a-fA-F0-9]{64}$', wallet.private_key):
                logger.error(f'Invalid private key format: {wallet.get_hidden_key()}')
                return

            logger.info(f'Start work with {wallet.sender_address}')

            # Check balances before proceeding
            usdt_balance, eth_balance = self.check_wallet_balances(wallet)
            if usdt_balance == 0 and eth_balance == 0:
                logger.warning(f'Wallet {wallet.sender_address} has no funds. Skipping.')
                return

            proxy_url = check_proxy(wallet.proxy)
            # Web3 instance initiation
            web3 = create_web3_instance(arb_rpc_url, proxy_url)
            
            # Get USDT transfer status.
            transfer_service = TransferService(web3, self.usdt_token_abi)
            
            # Add check to prevent sending to same address
            if wallet.sender_address.lower() == wallet.recipient_address.lower():
                logger.warning(f'Recipient address is the same as sender address: {wallet.sender_address}. Skipping USDT transfer.')
            else:
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

        try:
            for i, wallet in enumerate(wallets):
                print(f"Processing wallet {i+1}/{len(wallets)}. Press Ctrl+C to abort...")
                self.process_wallet(wallet)

                if i < len(wallets) - 1:
                    sleep_between_accounts(self.config.min_account_delay, self.config.max_account_delay)
        except KeyboardInterrupt:
            logger.warning("Process interrupted by user")
            return

        logger.info(f'{"=" * 100}')
        logger.info(f'Finished processing all {len(wallets)} wallets')
        logger.info(f'{"=" * 100}\n')
