import os
from dotenv import load_dotenv

load_dotenv()

# Network configuration
arb_rpc_url = os.getenv('ARB_RPC_URL', 'https://1rpc.io/arb')
arb_explorer_url = os.getenv('ARB_EXPLORER_URL', 'https://arbiscan.io/')

# Contract address
USDT_CONTRACT_ADDRESS = os.getenv('USDT_CONTRACT_ADDRESS', '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9')
