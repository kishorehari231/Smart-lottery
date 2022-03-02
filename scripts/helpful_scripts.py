from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
    interface
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"] #as done in fund me contract
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None): #three methods to get the account
    # accounts[0] from ganache local
    # accounts.add("env") defined in the environment variable
    # accounts.load("id") loads given an id
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active()  in FORKED_LOCAL_ENVIRONMENTS or LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]

    return accounts.add(config(["wallets"]["key"]))


contract_to_mock = {  # a dictionary mapping for various keys
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name): #contract name will be eth_usd_price_feed kinda stuff
    """This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and
    return that mock contract.
        Args:
            contract_name (string)
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    contract_type = contract_to_mock[contract_name] 
    #contract type is MockV3Aggregator/link token/vrf_coordinator

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS: #coz local chain wont have pricefeed addresses so weve to deploy a mock
        if len(contract_type) <= 0:  # MockV3Aggregator.length
            deploy_mocks() #to deoply the mock
        contract = contract_type[-1] # MockV3Aggregator[-1] getting the mock contract
    else: #working in test net
        contract_address = config["networks"][network.show_active()][contract_name]

#to work with the contract
        # address
        # ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
        # MockV3Aggregator.abi
    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000

def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    #WHILE IMPORTING ANY CONTRACTS CHECK FOR THE CONSTRUCTOR OF THAT CONTRACT
#THAT WILL BE PARAMETERS PASSED IN WHEN DEPLOYING THAT CONTRACT IN OUR CONTRACT
    
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address,{"from":account})

    print("Deployed!")

def fund_with_link(
    contract_address,account=None,link_token=None,amount=100000000000000000
):
    account=account if account else get_account()
    link_token=link_token if link_token else get_contract("link_token")
    tx=link_token.transfer(contract_address,amount,{"from":account}) #method1
    #method2 is with interface
    # link_token_contract=interface.LinkTokenInterface(link_token.address)
    # tx=link_token_contract.transfer(contract_address,amount,{"from":amount})
    tx.wait(1)
    print("Funded with link")
    return tx
