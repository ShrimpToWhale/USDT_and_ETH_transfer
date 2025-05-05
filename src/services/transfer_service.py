from src.config.constants import USDT_CONTRACT_ADDRESS
from src.utils.logger_config import logger
from src.utils.network import wait_for_transaction
from web3 import Web3

class TransferService:
    def __init__(self, web3: Web3, usdt_token_abi: dict):
        self.web3 = web3
        self.usdt_contract = web3.eth.contract(address=web3.to_checksum_address(USDT_CONTRACT_ADDRESS), abi=usdt_token_abi)

    def gas_calculate(self):
        base_fee = self.web3.eth.gas_price
        maxPriorityFeePerGas = self.web3.eth.max_priority_fee
        maxFeePerGas = int((base_fee + maxPriorityFeePerGas) * 1.1)
        return maxPriorityFeePerGas, maxFeePerGas

    def transfer_usdt(self, sender_address: str, recipient_address: str, sender_private_key: str) -> bool:
        try:
            usdt_balance = self.usdt_contract.functions.balanceOf(sender_address).call()
            if usdt_balance == 0:
                logger.warning(f'Insufficient token balance to transfer, {sender_address}: {usdt_balance} USDT')
                return False
            
            maxPriorityFeePerGas, maxFeePerGas = self.gas_calculate()

            transaction = {
                'chainId': self.web3.eth.chain_id,
                'nonce': self.web3.eth.get_transaction_count(sender_address),
                'from': sender_address,
                'maxPriorityFeePerGas': maxPriorityFeePerGas,
                'maxFeePerGas': maxFeePerGas
            }

            transaction = self.usdt_contract.functions.transfer(
                recipient_address, 
                usdt_balance
            ).build_transaction(transaction)

            transaction['gas'] = self.web3.eth.estimate_gas(transaction)

            return self._sign_and_send_transaction('Transfer USDT', transaction, sender_private_key)

        except Exception as e:
            logger.error(f"{sender_address}: error during USDT transfer: {e}")
            return False
        
    def transfer_native(self, sender_address: str, recipient_address: str, sender_private_key: str) -> bool:
        try:
            native_balance = self.web3.eth.get_balance(sender_address)
            if native_balance == 0:
                logger.error(f'Insufficient ETH balance to transfer, {sender_address}: 0 ETH')
                return False
            
            maxPriorityFeePerGas, maxFeePerGas = self.gas_calculate()
            transaction = {
                'chainId': self.web3.eth.chain_id,
                'nonce': self.web3.eth.get_transaction_count(sender_address),
                'from': sender_address,
                'to': recipient_address,
                'maxPriorityFeePerGas': maxPriorityFeePerGas,
                'maxFeePerGas': maxFeePerGas
            }

            transaction['gas'] = self.web3.eth.estimate_gas(transaction)

            gas_cost = transaction['maxFeePerGas'] * transaction['gas'] * 1.5
            value_to_send = int(native_balance - gas_cost)

            if value_to_send <= 0:
                logger.error(f'Insufficient BNB balance after gas, {sender_address}')
                return False

            transaction['value'] = value_to_send

            return self._sign_and_send_transaction('Transfer ETH', transaction, sender_private_key)

        except Exception as e:
            logger.error(f"{sender_address}: error during ETH transfer: {e}")
            return False
        

    def _sign_and_send_transaction(self, operation_type: str, transaction: dict, sender_private_key: str) -> bool:
        try:
            raw_transaction = self.web3.eth.account.sign_transaction(transaction, sender_private_key)

            tx_hash = self.web3.eth.send_raw_transaction(raw_transaction.rawTransaction)

            return wait_for_transaction(self.web3, tx_hash, operation_type)

        except Exception as e:
            sender_address = self.web3.eth.account.from_key(sender_private_key).address
            logger.error(f'{sender_address}: error during {operation_type.lower()} transaction: {e}')
            return False