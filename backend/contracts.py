# contracts.py - Backend integration for all Hedera/Ethereum contracts
from web3 import Web3
import os
from backend.hedera_integration_v2 import HederaClient

# Contract configurations - Update with actual deployed addresses and ABIs
CONTRACTS = {
    'PropertyNFT': {
        'abi': [
            {"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"symbol","type":"string"}],"stateMutability":"nonpayable","type":"constructor"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"approved","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"operator","type":"address"},{"indexed":False,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},
            {"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
            {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"_approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
            {"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"string","name":"tokenURI","type":"string"}],"name":"mint","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}
        ],
        'address': '0x0000000000000000000000000000000000000000',  # Replace with deployed address
        'hedera_id': os.getenv('HEDERA_PROPERTYNFT_CONTRACT_ID'),
    },
    'LeaseAgreement': {
        'abi': [
            {"inputs":[{"internalType":"address","name":"_propertyNFT","type":"address"},{"internalType":"address","name":"_rentEscrow","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
            {"anonymous":False,"inputs":[{"indexed":False,"internalType":"uint256","name":"leaseId","type":"uint256"},{"indexed":True,"internalType":"address","name":"tenant","type":"address"},{"indexed":True,"internalType":"uint256","name":"propertyId","type":"uint256"}],"name":"LeaseCreated","type":"event"},
            {"inputs":[],"name":"leaseCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"leases","outputs":[{"internalType":"uint256","name":"propertyId","type":"uint256"},{"internalType":"address","name":"tenant","type":"address"},{"internalType":"address","name":"landlord","type":"address"},{"internalType":"uint256","name":"monthlyRent","type":"uint256"},{"internalType":"uint256","name":"startDate","type":"uint256"},{"internalType":"uint256","name":"endDate","type":"uint256"},{"internalType":"bool","name":"isActive","type":"bool"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_propertyId","type":"uint256"},{"internalType":"address","name":"_tenant","type":"address"},{"internalType":"uint256","name":"_monthlyRent","type":"uint256"},{"internalType":"uint256","name":"_durationMonths","type":"uint256"}],"name":"createLease","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_leaseId","type":"uint256"}],"name":"terminateLease","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_leaseId","type":"uint256"}],"name":"getLeaseDetails","outputs":[{"internalType":"uint256","name":"propertyId","type":"uint256"},{"internalType":"address","name":"tenant","type":"address"},{"internalType":"address","name":"landlord","type":"address"},{"internalType":"uint256","name":"monthlyRent","type":"uint256"},{"internalType":"uint256","name":"startDate","type":"uint256"},{"internalType":"uint256","name":"endDate","type":"uint256"},{"internalType":"bool","name":"isActive","type":"bool"}],"stateMutability":"view","type":"function"}
        ],
        'address': '0x0000000000000000000000000000000000000000',  # Replace with deployed address
        'hedera_id': os.getenv('HEDERA_LEASEAGREEMENT_CONTRACT_ID'),
    },
    'RentEscrow': {
        'abi': [
            {"inputs":[{"internalType":"address","name":"_findToken","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"tenant","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"timestamp","type":"uint256"}],"name":"PaymentReceived","type":"event"},
            {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"escrowedFunds","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"address","name":"_tenant","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"depositRent","outputs":[],"stateMutability":"payable","type":"function"},
            {"inputs":[{"internalType":"address","name":"_landlord","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"releaseRent","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"address","name":"_tenant","type":"address"}],"name":"getEscrowedAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"address","name":"_tenant","type":"address"}],"name":"refundTenant","outputs":[],"stateMutability":"nonpayable","type":"function"}
        ],
        'address': '0x0000000000000000000000000000000000000000',  # Replace with deployed address
        'hedera_id': os.getenv('HEDERA_RENTESCROW_CONTRACT_ID'),
    },
    'SavingsVault': {
        'abi': [
            {"inputs":[{"internalType":"address","name":"_findToken","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Deposit","type":"event"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Withdrawal","type":"event"},
            {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balances","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"deposit","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"address","name":"_user","type":"address"}],"name":"getBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}
        ],
        'address': '0x0000000000000000000000000000000000000000',  # Replace with deployed address
        'hedera_id': os.getenv('HEDERA_SAVINGSVAULT_CONTRACT_ID'),
    },
    'Reputation': {
        'abi': [
            {"inputs":[],"stateMutability":"nonpayable","type":"constructor"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"uint256","name":"score","type":"uint256"}],"name":"ReputationUpdated","type":"event"},
            {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"reputations","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"uint256","name":"_score","type":"uint256"}],"name":"updateReputation","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"address","name":"_user","type":"address"}],"name":"getReputation","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}
        ],
        'address': '0x0000000000000000000000000000000000000000',  # Replace with deployed address
        'hedera_id': os.getenv('HEDERA_REPUTATION_CONTRACT_ID'),
    },
    'P2PCommunity': {
        'abi': [
            {"inputs":[],"stateMutability":"nonpayable","type":"constructor"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"string","name":"userType","type":"string"}],"name":"UserRegistered","type":"event"},
            {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"users","outputs":[{"internalType":"string","name":"userType","type":"string"},{"internalType":"uint256","name":"reputation","type":"uint256"},{"internalType":"bool","name":"isActive","type":"bool"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"string","name":"_userType","type":"string"}],"name":"registerUser","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"address","name":"_user","type":"address"}],"name":"getUserInfo","outputs":[{"internalType":"string","name":"userType","type":"string"},{"internalType":"uint256","name":"reputation","type":"uint256"},{"internalType":"bool","name":"isActive","type":"bool"}],"stateMutability":"view","type":"function"}
        ],
        'address': '0x0000000000000000000000000000000000000000',  # Replace with deployed address
        'hedera_id': os.getenv('HEDERA_P2PCOMMUNITY_CONTRACT_ID'),
    },
    'AgentEconomy': {
        'abi': [
            {"inputs":[{"internalType":"string","name":"agentType","type":"string"},{"internalType":"string[]","name":"capabilities","type":"string[]"},{"internalType":"address","name":"walletAddress","type":"address"}],"name":"registerAgent","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"agentId","type":"uint256"},{"internalType":"string","name":"serviceType","type":"string"},{"internalType":"string","name":"description","type":"string"},{"internalType":"uint256","name":"basePrice","type":"uint256"},{"internalType":"uint256","name":"variableFee","type":"uint256"},{"internalType":"uint256","name":"minOrderValue","type":"uint256"}],"name":"createServiceOffer","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"offerId","type":"uint256"},{"internalType":"uint256","name":"requestorAgentId","type":"uint256"},{"internalType":"uint256","name":"orderValue","type":"uint256"}],"name":"executeService","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"payable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"fromAgent","type":"uint256"},{"internalType":"uint256","name":"toAgent","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"string","name":"serviceType","type":"string"}],"name":"transferBetweenAgents","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"agentId","type":"uint256"}],"name":"getAgentBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"agentId","type":"uint256"}],"name":"getAgentCapabilities","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"string","name":"serviceType","type":"string"}],"name":"getServiceOffers","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},
            {"inputs":[],"name":"getAllAgents","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"agentId","type":"uint256"}],"name":"agents","outputs":[{"internalType":"uint256","name":"agentId","type":"uint256"},{"internalType":"address","name":"walletAddress","type":"address"},{"internalType":"string","name":"agentType","type":"string"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"uint256","name":"reputation","type":"uint256"},{"internalType":"uint256","name":"stakedAmount","type":"uint256"},{"internalType":"string[]","name":"capabilities","type":"string[]"},{"internalType":"bool","name":"isActive","type":"bool"},{"internalType":"uint256","name":"registeredAt","type":"uint256"},{"internalType":"uint256","name":"lastActivity","type":"uint256"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"offerId","type":"uint256"}],"name":"offers","outputs":[{"internalType":"uint256","name":"offerId","type":"uint256"},{"internalType":"uint256","name":"agentId","type":"uint256"},{"internalType":"string","name":"serviceType","type":"string"},{"internalType":"string","name":"description","type":"string"},{"internalType":"uint256","name":"basePrice","type":"uint256"},{"internalType":"uint256","name":"variableFee","type":"uint256"},{"internalType":"uint256","name":"minOrderValue","type":"uint256"},{"internalType":"bool","name":"isActive","type":"bool"},{"internalType":"uint256","name":"createdAt","type":"uint256"},{"internalType":"uint256","name":"totalTransactions","type":"uint256"},{"internalType":"uint256","name":"totalRevenue","type":"uint256"}],"stateMutability":"view","type":"function"}
        ],
        'address': '0x0000000000000000000000000000000000000000',  # Replace with deployed address
        'hedera_id': os.getenv('HEDERA_AGENT_ECONOMY_CONTRACT_ID'),
    },
    'MultiAgentNegotiation': {
        'abi': [
            {"inputs":[{"internalType":"uint256","name":"_agentEconomy","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"uint256","name":"negotiationId","type":"uint256"},{"indexed":True,"internalType":"uint256","name":"initiatorId","type":"uint256"}],"name":"NegotiationCreated","type":"event"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"uint256","name":"negotiationId","type":"uint256"},{"indexed":True,"internalType":"uint256","name":"agentId","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"bidAmount","type":"uint256"}],"name":"BidSubmitted","type":"event"},
            {"inputs":[],"name":"negotiationCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_initiatorId","type":"uint256"},{"internalType":"uint256[]","name":"_participantIds","type":"uint256[]"},{"internalType":"string","name":"_negotiationType","type":"string"},{"internalType":"bytes","name":"_initialParams","type":"bytes"}],"name":"createNegotiation","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_negotiationId","type":"uint256"},{"internalType":"uint256","name":"_bidAmount","type":"uint256"},{"internalType":"bytes","name":"_bidData","type":"bytes"}],"name":"submitBid","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_negotiationId","type":"uint256"},{"internalType":"uint256","name":"_stepIndex","type":"uint256"},{"internalType":"bytes","name":"_stepData","type":"bytes"}],"name":"executeWorkflowStep","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_negotiationId","type":"uint256"}],"name":"getNegotiationStatus","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_negotiationId","type":"uint256"}],"name":"getWinningBid","outputs":[{"internalType":"uint256","name":"agentId","type":"uint256"},{"internalType":"uint256","name":"bidAmount","type":"uint256"},{"internalType":"bytes","name":"bidData","type":"bytes"}],"stateMutability":"view","type":"function"}
        ],
        'address': '0x0000000000000000000000000000000000000000',  # Replace with deployed address
        'hedera_id': os.getenv('HEDERA_MULTI_AGENT_NEGOTIATION_CONTRACT_ID'),
    },
    'CrossChainService': {
        'abi': [
            {"inputs":[],"stateMutability":"nonpayable","type":"constructor"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"uint256","name":"serviceId","type":"uint256"},{"indexed":True,"internalType":"string","name":"chainName","type":"string"}],"name":"CrossChainServiceRegistered","type":"event"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"uint256","name":"requestId","type":"uint256"},{"indexed":True,"internalType":"string","name":"targetChain","type":"string"}],"name":"CrossChainRequestCreated","type":"event"},
            {"inputs":[],"name":"serviceCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"string","name":"_chainName","type":"string"},{"internalType":"string","name":"_serviceType","type":"string"},{"internalType":"address","name":"_bridgeContract","type":"address"},{"internalType":"bytes","name":"_config","type":"bytes"}],"name":"registerCrossChainService","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_serviceId","type":"uint256"},{"internalType":"bytes","name":"_requestData","type":"bytes"},{"internalType":"uint256","name":"_gasLimit","type":"uint256"}],"name":"createCrossChainRequest","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_requestId","type":"uint256"},{"internalType":"bytes","name":"_result","type":"bytes"}],"name":"executeCrossChainRequest","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_serviceId","type":"uint256"}],"name":"getServiceInfo","outputs":[{"internalType":"string","name":"chainName","type":"string"},{"internalType":"string","name":"serviceType","type":"string"},{"internalType":"address","name":"bridgeContract","type":"address"},{"internalType":"bool","name":"isActive","type":"bool"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_requestId","type":"uint256"}],"name":"getRequestStatus","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}
        ],
        'address': '0x0000000000000000000000000000000000000000',  # Replace with deployed address
        'hedera_id': os.getenv('HEDERA_CROSS_CHAIN_SERVICE_CONTRACT_ID'),
    },
    'AIOptimization': {
        'abi': [
            {"inputs":[{"internalType":"address","name":"_agentEconomy","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"uint256","name":"modelId","type":"uint256"},{"indexed":True,"internalType":"uint256","name":"agentId","type":"uint256"},{"indexed":False,"internalType":"string","name":"modelType","type":"string"}],"name":"ModelCreated","type":"event"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"uint256","name":"modelId","type":"uint256"},{"indexed":True,"internalType":"uint256","name":"experienceId","type":"uint256"}],"name":"ExperienceRecorded","type":"event"},
            {"inputs":[{"internalType":"uint256","name":"_agentId","type":"uint256"},{"internalType":"string","name":"_modelType","type":"string"},{"internalType":"bytes","name":"_initialParams","type":"bytes"}],"name":"createLearningModel","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_modelId","type":"uint256"},{"internalType":"bytes","name":"_state","type":"bytes"},{"internalType":"bytes","name":"_action","type":"bytes"},{"internalType":"int256","name":"_reward","type":"int256"},{"internalType":"bytes","name":"_nextState","type":"bytes"}],"name":"recordExperience","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_taskId","type":"uint256"}],"name":"executeOptimization","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_modelId","type":"uint256"},{"internalType":"bytes","name":"_state","type":"bytes"}],"name":"getModelPrediction","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_learningRate","type":"uint256"},{"internalType":"uint256","name":"_discountFactor","type":"uint256"},{"internalType":"uint256","name":"_explorationRate","type":"uint256"}],"name":"updateHyperparameters","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_modelId","type":"uint256"}],"name":"getLearningModel","outputs":[{"internalType":"uint256","name":"modelId","type":"uint256"},{"internalType":"uint256","name":"agentId","type":"uint256"},{"internalType":"string","name":"modelType","type":"string"},{"internalType":"bytes","name":"modelParams","type":"bytes"},{"internalType":"uint256","name":"version","type":"uint256"},{"internalType":"uint256","name":"accuracy","type":"uint256"},{"internalType":"uint256","name":"trainingDataPoints","type":"uint256"},{"internalType":"uint256","name":"lastUpdated","type":"uint256"},{"internalType":"bool","name":"isActive","type":"bool"}],"stateMutability":"view","type":"function"}
        ],
        'address': '0x0000000000000000000000000000000000000000',  # Replace with deployed address
        'hedera_id': os.getenv('HEDERA_AI_OPTIMIZATION_CONTRACT_ID'),
    },
    'AgentGovernance': {
        'abi': [
            {"inputs":[{"internalType":"address","name":"_agentEconomy","type":"address"},{"internalType":"address","name":"_governanceToken","type":"address"},{"components":[{"internalType":"uint256","name":"votingPeriod","type":"uint256"},{"internalType":"uint256","name":"proposalThreshold","type":"uint256"},{"internalType":"uint256","name":"quorumThreshold","type":"uint256"},{"internalType":"uint256","name":"timelockDelay","type":"uint256"},{"internalType":"uint256","name":"executionGracePeriod","type":"uint256"}],"internalType":"struct AgentGovernance.GovernanceConfig","name":"_config","type":"tuple"}],"stateMutability":"nonpayable","type":"constructor"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"uint256","name":"proposalId","type":"uint256"},{"indexed":True,"internalType":"address","name":"proposer","type":"address"},{"indexed":False,"internalType":"enum AgentGovernance.ProposalType","name":"proposalType","type":"uint8"}],"name":"ProposalCreated","type":"event"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"uint256","name":"proposalId","type":"uint256"},{"indexed":True,"internalType":"address","name":"voter","type":"address"},{"indexed":False,"internalType":"bool","name":"support","type":"bool"},{"indexed":False,"internalType":"uint256","name":"weight","type":"uint256"}],"name":"VoteCast","type":"event"},
            {"anonymous":False,"inputs":[{"indexed":True,"internalType":"uint256","name":"proposalId","type":"uint256"}],"name":"ProposalExecuted","type":"event"},
            {"inputs":[{"internalType":"enum AgentGovernance.ProposalType","name":"_proposalType","type":"uint8"},{"internalType":"string","name":"_title","type":"string"},{"internalType":"string","name":"_description","type":"string"},{"internalType":"bytes","name":"_parameters","type":"bytes"}],"name":"createProposal","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_proposalId","type":"uint256"},{"internalType":"bool","name":"_support","type":"bool"}],"name":"castVote","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_proposalId","type":"uint256"}],"name":"executeProposal","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_proposalId","type":"uint256"}],"name":"executeTimelockedProposal","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"components":[{"internalType":"uint256","name":"votingPeriod","type":"uint256"},{"internalType":"uint256","name":"proposalThreshold","type":"uint256"},{"internalType":"uint256","name":"quorumThreshold","type":"uint256"},{"internalType":"uint256","name":"timelockDelay","type":"uint256"},{"internalType":"uint256","name":"executionGracePeriod","type":"uint256"}],"internalType":"struct AgentGovernance.GovernanceConfig","name":"_newConfig","type":"tuple"}],"name":"updateConfig","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_proposalId","type":"uint256"}],"name":"getProposal","outputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"proposer","type":"address"},{"internalType":"enum AgentGovernance.ProposalType","name":"proposalType","type":"uint8"},{"internalType":"string","name":"title","type":"string"},{"internalType":"string","name":"description","type":"string"},{"internalType":"bytes","name":"parameters","type":"bytes"},{"internalType":"uint256","name":"startTime","type":"uint256"},{"internalType":"uint256","name":"endTime","type":"uint256"},{"internalType":"uint256","name":"forVotes","type":"uint256"},{"internalType":"uint256","name":"againstVotes","type":"uint256"},{"internalType":"uint256","name":"abstainVotes","type":"uint256"},{"internalType":"enum AgentGovernance.ProposalStatus","name":"status","type":"uint8"},{"internalType":"bool","name":"executed","type":"bool"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_proposalId","type":"uint256"},{"internalType":"address","name":"_voter","type":"address"}],"name":"getVote","outputs":[{"internalType":"bool","name":"hasVoted","type":"bool"},{"internalType":"bool","name":"support","type":"bool"},{"internalType":"uint256","name":"weight","type":"uint256"},{"internalType":"uint256","name":"timestamp","type":"uint256"}],"stateMutability":"view","type":"function"}
        ],
        'address': '0x0000000000000000000000000000000000000000',  # Replace with deployed address
        'hedera_id': os.getenv('HEDERA_AGENT_GOVERNANCE_CONTRACT_ID'),
    },
}

# initialize web3 provider (HTTP or WS) from environment variables
w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URL', 'http://localhost:8545')))

# hedra client for on-chain functionality
hedera = HederaClient(
    account_id=os.getenv('HEDERA_ACCOUNT_ID'),
    private_key=os.getenv('HEDERA_PRIVATE_KEY'),
    network=os.getenv('HEDERA_NETWORK', 'testnet'),
)

# optional: check web3 connection (only when called)
# if w3 and not w3.is_connected():
#     # logging could be added here
#     pass


def get_contract(name):
    """Return a web3 contract or raise if unsupported."""
    info = CONTRACTS.get(name)
    if info is None:
        raise ValueError(f"contract '{name}' is not configured")
    if w3 and w3.isConnected():
        return w3.eth.contract(address=info['address'], abi=info['abi'])
    else:
        raise RuntimeError("Web3 provider not available")


def call_hedera_contract(name: str, function: str, params: list = None, gas: int = 100000) -> dict:
    """Invoke a function on an on-chain Hedera contract by name.

    This helper converts a named contract into its deployed ID, then calls
    ``hedera.call_contract``.  The caller is responsible for providing
    correct parameter formatting according to the ABI.
    """
    info = CONTRACTS.get(name)
    if not info or not info.get('hedera_id'):
        raise ValueError(f"Hedera contract '{name}' not configured or has no id")
    return hedera.call_contract(info['hedera_id'], function, params or [], gas)

# Example usage for PropertyNFT
# contract = get_contract('PropertyNFT')
# tx = contract.functions.registerProperty(...).buildTransaction({...})
# hedera.call_contract(CONTRACTS['PropertyNFT']['hedera_id'], 'registerProperty', [...])

# Example usage for PropertyNFT
# contract = get_contract('PropertyNFT')
# tx = contract.functions.registerProperty(...).buildTransaction({...})
