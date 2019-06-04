import json

import requests
from random import randint
import datetime


class Transfers:

    def __init__(self, id_no, transfer_description):
        self.id = id_no
        self.transfer_description = transfer_description


class TransferDescription:

    def __init__(self, status, origin_acct, target_acct, amount, description, ini_time, completed_time, failed_at):
        self.status = status
        self.origin_acct = origin_acct
        self.target_acct = target_acct
        self.amount = amount
        self.description = description
        self.ini_time = ini_time
        self.completed_time = completed_time
        self.failed_at = failed_at


class Users:

    def __init__(self, user_id, user_description):
        self.user_id = user_id
        self.user_description = user_description


class UserDescription:

    def __init__(self, firstname, lastname, accounts, transfers, likes):
        self.firstname = firstname
        self.lastname = lastname
        self.accounts = accounts
        self.transfers = transfers
        self.likes = likes


class Accounts:

    def __init__(self, id_no, account_description):
        self.id_no = id_no
        self.account_description = account_description


class AccountDescription:

    def __init__(self, user, account_number, balance):
        self.user = user
        self.account_number = account_number
        self.balance = balance


class Feed:

    def __init__(self, origin_user_name, target_user_name, amount, description):
        self.origin_user_name = origin_user_name
        self.target_user_name = target_user_name
        self.amount = amount
        self.description = description


class Trades:
    transactions = []
    users = []
    transfer_list = []
    accounts = []

    def get_transfers(self):
        json_data = requests.get("https://ellevest-rohan-tandon1.glitch.me/transfers").json()
        for transfer in json_data:
            transfer_description = TransferDescription(transfer["status"], transfer["originAccount"],
                                                       transfer["targetAccount"], transfer["amount"],
                                                       transfer["description"], transfer["initiatedAt"],
                                                       transfer["completedAt"], transfer["failedAt"])
            id_no = transfer["id"]
            transaction = Transfers(id_no, transfer_description)
            self.transactions.append(transaction)

    def get_users(self):
        json_data = requests.get("https://ellevest-rohan-tandon1.glitch.me/users").json()
        for users in json_data:
            id_no = users["id"]
            user_description = UserDescription(users["firstName"], users["lastName"], users["accounts"],
                                               users["transfers"], users["likes"])
            person = Users(id_no, user_description)
            self.users.append(person)

    def get_transfer_list(self):
        for transaction in self.transactions:
            amount = transaction.transfer_description.amount
            description = transaction.transfer_description.description
            origin_name = ""
            target_name = ""
            # likeNum = 0
            for user in self.users:
                accounts = user.user_description.accounts
                for acc in accounts:
                    if acc == transaction.transfer_description.origin_acct:
                        origin_name = user.user_description.firstname + user.user_description.lastname
                        # likes = user.user_description.likes
                        # for like in likes:
                        #     if like[0] == transaction.id:
                        #        likeNum = like[1]
                    if acc == transaction.transfer_description.target_acct:
                        target_name = user.user_description.firstname + user.user_description.lastname

            feed = Feed(origin_name, target_name, amount / 100, description)
            self.transfer_list.append(feed)

    def get_accounts(self):
        json_data = requests.get("https://ellevest-rohan-tandon1.glitch.me/accounts").json()
        for account in json_data:
            acct_description = AccountDescription(account["user"], account["accountNumber"], account["balance"])
            acct = Accounts(account["id"], acct_description)
            self.accounts.append(acct)

    def execute_transfer(self, origin_account_no, target_account_no, amount, description, initiated_at):
        origin_account = self.accounts[origin_account_no]
        target_account = self.accounts[target_account_no]
        original_user = self.users[origin_account_no]
        target_user = self.users[target_account_no]

        transfer_number = randint(0, 100)
        time = datetime.datetime.now().isoformat()

        if amount <= origin_account.account_description.balance:
            origin_account.account_description.balance -= amount
            target_account.account_description.balance += amount
            self.accounts[origin_account_no] = origin_account
            self.accounts[target_account_no] = target_account
            status = "complete"
            failed_at = "none"
            completed_time = time

        else:
            status = "failed"
            completed_time = "none"
            failed_at = time

        transfer_description = TransferDescription(status, origin_account_no, target_account_no, amount,
                                                   description, initiated_at, completed_time, failed_at)

        transfer = Transfers(transfer_number, transfer_description)
        self.transactions.append(transfer)
        current_transactions_origin_acct = original_user.user_description.transfers
        current_transactions_origin_acct.append(transfer_number)
        original_user.user_description.transfers = current_transactions_origin_acct

        current_transactions_target_acct = target_user.user_description.transfers
        current_transactions_target_acct.append(transfer_number)
        target_user.user_description.transfers = current_transactions_target_acct

        return transfer


def main():
    trades = Trades()
    trades.get_transfers()
    trades.get_users()
    trades.get_transfer_list()
    print("Social feed created is:")
    for t in trades.transfer_list:
        y = json.dumps(t.__dict__)
        print(y)
    trades.get_accounts()
    print("Trying to execute new transfer: ")
    new_transfer = {'origin_account': 3, 'target_account': 1, 'amount': 1230, 'description': "Thanks for the laughs",
                    'status': 'initiated'}
    initiated_at = datetime.datetime.now().isoformat()
    new_transfer['initiated_at'] = initiated_at
    print(json.dumps(new_transfer))
    transfer = trades.execute_transfer(3, 1, 1230, "Thanks for the laughs!", initiated_at)
    transfer_description = transfer.transfer_description
    if transfer_description.status == "complete":
        print("Transfer was success:")
        print(transfer_description.__dict__)


if __name__ == "__main__":
    main()
