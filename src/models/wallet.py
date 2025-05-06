from src.utils.logger_config import logger
from eth_account import Account
from web3 import Web3
from typing import Optional

class Wallet:
    # Wallet class initiation.
    def __init__(self, private_key: str, recipient_address: str, proxy: Optional[str] = None):
        self.private_key = private_key
        self.recipient_address = self.to_checksum(recipient_address)
        self.proxy = proxy
        self.sender_address = self.address_extract(private_key)

    @staticmethod
    # Get the wallet address from the private key.
    def address_extract(private_key: str) -> str:
        try:
            return (Account.from_key(private_key)).address
        except Exception as e:
            logger.error(f'Invalid private key: {private_key}. Error: {e}"')
            raise ValueError
        
    @staticmethod
    # Get the checksum address.
    def to_checksum(address: str) -> str:
        try:
            return Web3.to_checksum_address(address)
        except Exception as e:
            logger.error(f'Invalid address: {address}. Error: {e}"')
            raise ValueError
            
    # Get hidden version of private key for logs.
    def get_hidden_key(self) -> str:
        """Return a hidden version of the private key for logging."""
        if not self.private_key:
            return "None"
        if self.private_key.startswith("0x"):
            visible_part = self.private_key[:6] + "..." + self.private_key[-4:]
        else:
            visible_part = self.private_key[:4] + "..." + self.private_key[-4:]
        return visible_part
