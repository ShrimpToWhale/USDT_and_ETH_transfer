from src.config.constants import USDT_CONTRACT_ADDRESS
from src.utils.logger_config import logger
from src.utils.network import wait_for_transaction
from web3 import Web3
from typing import Dict, Any, Optional

class TransferService:
    # TransferService class initiation
    def __init__(self, web3: Web3, usdt_token_abi: dict):
        self.web3 = web3
        self.usdt_contract = web3.eth.contract(address=web3.to_checksum_address(USDT_CONTRACT_ADDRESS), abi=usdt_token_abi)
        
    # Gas calculation for EIP-1559.
    def gas_calculate(self) -> tuple[int, int]:
        base_fee = self.web3.eth.gas_price
        maxPriorityFeePerGas = self.web3.eth.max_priority_fee
        maxFeePerGas = int((base_fee + maxPriorityFeePerGas) * 1.1)
        return maxPriorityFeePerGas, maxFeePerGas

    # Transfer USDT tokens to recipient address.
    def transfer_usdt(self, sender_address: str, recipient_address: str, sender_private_key: str) -> bool:
        try:
            # Check if recipient is not the same as sender
            if sender_address.lower() == recipient_address.lower():
                logger.warning(f'Recipient address is the same as sender address: {sender_address}')
                return False
                
            # Check token balance.
            usdt_balance = self.usdt_contract.functions.balanceOf(sender_address).call()
            if usdt_balance == 0:
                logger.warning(f'Insufficient token balance to transfer, {sender_address}: {usdt_balance} USDT')
                return False
            
            # Get token decimals for better display
            try:
                decimals = self.usdt_contract.functions.decimals().call()
                human_balance = usdt_balance / (10 ** decimals)
                logger.info(f'USDT balance to transfer: {human_balance} USDT')
                
                # Add minimum transfer threshold to avoid dust transfers
                min_transfer_amount = 10 ** (decimals - 3)  # 0.001 USDT
                if usdt_balance < min_transfer_amount:
                    logger.warning(f'USDT balance too low for transfer: {human_balance}')
                    return False
            except Exception as e:
                logger.warning(f'Could not get token decimals: {e}. Continuing with raw balance')
            
            maxPriorityFeePerGas, maxFeePerGas = self.gas_calculate()

            # Build default transaction.
            transaction = {
                'chainId': self.web3.eth.chain_id,
                'nonce': self.web3.eth.get_transaction_count(sender_address),
                'from': sender_address,
                'maxPriorityFeePerGas': maxPriorityFeePerGas,
                'maxFeePerGas': maxFeePerGas
            }

            # Create token transfer transaction.
            transaction = self.usdt_contract.functions.transfer(
                recipient_address, 
                usdt_balance
            ).build_transaction(transaction)

            # Estimate gas parameter addition.
            transaction['gas'] = self.web3.eth.estimate_gas(transaction)

            # Sign and send transaction.
            return self._sign_and_send_transaction('Transfer USDT', transaction, sender_private_key)

        except Exception as e:
            logger.error(f"{sender_address}: error during USDT transfer: {e}")
            return False

    # Transfer native ETH to recipient address.
    def transfer_native(self, sender_address: str, recipient_address: str, sender_private_key: str) -> bool:
        try:
            # Check if recipient is not the same as sender
            if sender_address.lower() == recipient_address.lower():
                logger.warning(f'Recipient address is the same as sender address: {sender_address}')
                return False
                
            # Get native balance.
            native_balance = self.web3.eth.get_balance(sender_address)
            if native_balance == 0:
                logger.error(f'Insufficient ETH balance to transfer, {sender_address}: 0 ETH')
                return False
            
            # Add minimum transfer threshold
            min_eth_transfer = self.web3.to_wei(0.001, 'ether')  # 0.001 ETH
            if native_balance < min_eth_transfer:
                logger.warning(f'ETH balance too low for transfer: {self.web3.from_wei(native_balance, "ether")} ETH')
                return False
                
            maxPriorityFeePerGas, maxFeePerGas = self.gas_calculate()
            
            # Build default transaction.
            transaction = {
                'chainId': self.web3.eth.chain_id,
                'nonce': self.web3.eth.get_transaction_count(sender_address),
                'from': sender_address,
                'to': recipient_address,
                'maxPriorityFeePerGas': maxPriorityFeePerGas,
                'maxFeePerGas': maxFeePerGas
            }

            # Estimate gas parameter addition.
            transaction['gas'] = self.web3.eth.estimate_gas(transaction)

             # Calculate value to send (total balance - gas cost with safety margin).
            gas_cost = transaction['maxFeePerGas'] * transaction['gas'] * 1.5
            value_to_send = int(native_balance - gas_cost)

            if value_to_send <= 0:
                logger.error(f'Insufficient ETH balance after gas, {sender_address}')
                return False

            # Display the amount being transferred
            eth_to_send = self.web3.from_wei(value_to_send, 'ether')
            logger.info(f'Transferring {eth_to_send} ETH to {recipient_address}')

            # Value parameter addition.
            transaction['value'] = value_to_send

            # Sign and send transaction.
            return self._sign_and_send_transaction('Transfer ETH', transaction, sender_private_key)

        except Exception as e:
            logger.error(f"{sender_address}: error during ETH transfer: {e}")
            return False
        

    # Sign and send a transaction.
    def _sign_and_send_transaction(self, operation_type: str, transaction: dict, sender_private_key: str) -> bool:
        try:
            # Sign transaction.
            raw_transaction = self.web3.eth.account.sign_transaction(transaction, sender_private_key)

            # Send transaction.
            tx_hash = self.web3.eth.send_raw_transaction(raw_transaction.rawTransaction)

            # Wait for confirmation.
            return wait_for_transaction(self.web3, tx_hash, operation_type)

        except Exception as e:
            sender_address = self.web3.eth.account.from_key(sender_private_key).address
            logger.error(f'{sender_address}: error during {operation_type.lower()} transaction: {e}')
            return False
