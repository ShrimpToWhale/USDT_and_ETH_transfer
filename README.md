## ​Software for automatically USDT and ETH transfering.

🔔**Author's info**
- Author: [https://t.me/zero_0x_zero](https://t.me/zero_0x_zero)
- CHANNEL: [https://t.me/shrimp_to_whale](https://t.me/shrimp_to_whale)

✨**Features**
- 🟢 USDT transfer
- 🟢 Native(ETH) token transfer

🚀**Installation and launch**
1. git clone [https://github.com/ShrimpToWhale/StakeStone-CLaim-Transfer](https://github.com/ShrimpToWhale/USDT_and_ETH_transfer)
2. cd USDT_and_ETH_transfer
3. pip install -r requirements.txt
4. python main.py

📁**Files that need to be filled out**
- `wallets.txt` - private keys of your EVM accounts (with or without '0x')
- `recipients.txt` - addresses where USDT and ETH will be deposited
- `proxies.txt` - proxies in the login:password@host:port format
- `src/config/constants.py` - RPC endpoint, explorer URL, and the USDT contract address for the target chain.
  
❗ **The number of proxies, private keys, and deposit addresses must be the same.**

❗**If a proxy is not working, the software will automatically use the local IP to send requests.**

🛠️**Workflow and Configuration**

Upon launching the software, you’ll be prompted to set two types of delays(in seconds):
1. Delay between accounts – how long the script waits before switching to the next account
2. Delay between actions – pauses between USDT and ETH transfers

You’ll also be asked whether you want to shuffle the wallets before execution (each private key keeps its original address and proxy pairing).

**The software executes USDT and ETH transfers sequentially.
If a wallet does not have enough funds the subsequent operations will not be performed.**
