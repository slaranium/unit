from web3 import Web3
from eth_account import Account
import time
from colorama import init, Fore
import random as rand

init(autoreset=True)

def read_config(filename='data.txt'):
    config = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key.strip()] = value.strip().strip("'")
    return config

config = read_config()

private_key = config['private_key']
rpc_url = config['rpc_url']
chain_id = int(config['chain_id'])
Ticker = config['Ticker']
transaction_send = int(config['transaction_send'])
balance_send = float(config['balance_send'])
random = int(config['random'])
gasLimit = int(config['gasLimit'])
gasGwei = float(config['gasGwei'])

def connect_to_rpc():
    while True:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if w3.is_connected():
                print(Fore.GREEN + "Connected RPC")
                return w3
            else:
                print(Fore.YELLOW + "Failled ..Try Again")
                time.sleep(5)
        except Exception as e:
            print(Fore.RED + f"Failled: {e}")
            print(Fore.YELLOW + "Try Again")
            time.sleep(5)

w3 = connect_to_rpc()

def send_tokens(private_key, to_address, amount, nonce, gas_price, gas_limit):
    tx = {
        'nonce': nonce,
        'to': to_address,
        'value': w3.to_wei(amount, 'ether'),
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': chain_id
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash

def get_color(index):
    colors = [Fore.BLUE, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.CYAN]
    return colors[index % len(colors)]

def main():
    global gasGwei
    sender_address = Account.from_key(private_key).address
    if not w3.is_connected():
        print(Fore.RED + "RPC Failed")
        return
    balance_wei = w3.eth.get_balance(sender_address)
    balance_unit0 = w3.from_wei(balance_wei, 'ether')
    print(Fore.CYAN + f"Address: {sender_address}")
    print(Fore.CYAN + f"Balance: {balance_unit0:.6f} {Ticker}\n")
    gas_price = w3.to_wei(gasGwei, 'gwei')
    amount = balance_send * random
    nonce = w3.eth.get_transaction_count(sender_address)
    
    for index in range(transaction_send):
        retry_count = 0
        while retry_count < 3:
            try:
                new_account = Account.create()
                to_address = new_account.address
                current_balance = w3.from_wei(w3.eth.get_balance(sender_address), 'ether')
                tx_hash = send_tokens(private_key, to_address, amount, nonce, gas_price, gasLimit)
                color = get_color(index)
                print(color + f'✅ [{index+1}/{transaction_send}] [{current_balance:.6f}] {to_address[-5:]} >>> {tx_hash.hex()}')
                nonce += 1
                gas_price = w3.eth.gas_price
                time.sleep(rand.uniform(0.5, 1.5))
                break
            except Exception as e:
                error_message = str(e)
                if 'replacement transaction underpriced' in error_message.lower():
                    print(Fore.RED + f'❌ [{index+1}/{transaction_send}] Underpriced')
                    gas_price = int(gas_price * 1.2)
                elif 'nonce too low' in error_message.lower():
                    print(Fore.RED + f'❌ [{index+1}/{transaction_send}] Nonce too low')
                    nonce = w3.eth.get_transaction_count(sender_address)
                elif 'known transaction' in error_message.lower():
                    print(Fore.RED + f'❌ [{index+1}/{transaction_send}] Known transaction')
                    nonce += 1
                else:
                    print(Fore.RED + f'❌ [{index+1}/{transaction_send}] {error_message.split(":")[-1].strip()}')
                retry_count += 1
                time.sleep(1)
        
        if retry_count == 3:
            print(Fore.RED + f'❌ [{index+1}/{transaction_send}] Failed')

if __name__ == '__main__':
    main()
