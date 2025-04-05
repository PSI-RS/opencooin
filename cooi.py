
import hashlib
import json
from time import time
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.nodes = set()  # For future network implementation

    def create_genesis_block(self):
        return Block(0, time(), [], '0')

    def add_node(self, address):
        self.nodes.add(address)

    def add_transaction(self, sender, recipient, amount):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'timestamp': time()
        }
        self.pending_transactions.append(transaction)
        return self.last_block.index + 1

    def proof_of_work(self, last_block):
        nonce = 0
        while self.valid_proof(last_block, self.pending_transactions, nonce) is False:
            nonce += 1
        return nonce

    @staticmethod
    def valid_proof(last_block, transactions, nonce):
        guess = f'{last_block.hash}{transactions}{nonce}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"  # Simple difficulty

    def mine_pending_transactions(self, mining_address):
        last_block = self.last_block
        nonce = self.proof_of_work(last_block)
        self.add_transaction("reward", mining_address, 1) # Simple mining reward
        block = Block(len(self.chain), time(), self.pending_transactions, last_block.hash, nonce)
        self.pending_transactions = []
        self.chain.append(block)
        return block

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != self.hash(current_block):
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

            # Optionally re-verify proof of work (more complex with pending transactions)
            # This basic example doesn't re-verify PoW for simplicity

        return True

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

# --- GUI Section ---

def create_token_gui(coochain):
    window = Tk()
    window.title("OpenCooIn Token Entry")

    name_label = Label(window, text="Token Name:")
    name_label.grid(row=0, column=0, padx=5, pady=5)
    name_entry = Entry(window)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    wallet_label = Label(window, text="Wallet Address:")
    wallet_label.grid(row=1, column=0, padx=5, pady=5)
    wallet_entry = Entry(window)
    wallet_entry.grid(row=1, column=1, padx=5, pady=5)

    def enter_token():
        token_name = name_entry.get().strip()
        wallet_address = wallet_entry.get().strip()

        if not token_name or not wallet_address:
            messagebox.showerror("Error", "Please enter both Token Name and Wallet Address.")
            return

        # In a real application, you would likely:
        # 1. Check if the token name is valid (e.g., against a registry).
        # 2. Associate the token name with the wallet address in some persistent storage
        #    (not directly in the blockchain transactions for this purpose).
        # 3. Potentially trigger a "claim" transaction on the blockchain if that's part of your design.

        # For this simplified example, we'll just show a message.
        messagebox.showinfo("Success", f"Token '{token_name}' entered for wallet '{wallet_address}'.\n(Note: This doesn't directly mint or claim tokens on the blockchain in this example.)")

        name_entry.delete(0, 'end')
        wallet_entry.delete(0, 'end')

    enter_button = Button(window, text="Enter Token", command=enter_token)
    enter_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

    window.mainloop()

if __name__ == '__main__':
    coochain = Blockchain()
    print("OpenCooIn Blockchain Initialized.")

    # You can interact with the blockchain here for testing
    # Example:
     coochain.add_transaction("sender_address", "recipient_address", 5)
    mined_block = coochain.mine_pending_transactions("miner_address")
     print("Mined Block:", mined_block.hash)
    print("Is chain valid?", coochain.is_chain_valid())

    # Launch the GUI
    create_token_gui(coochain)
