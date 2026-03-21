// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title AgentEconomy
 * @dev Decentralized marketplace for AI agents to register, offer services, and transact autonomously
 * Enables transparent, autonomous economies leveraging Hedera's fast, low-cost microtransactions
 */
contract AgentEconomy is Ownable, ReentrancyGuard {
    // Agent structure
    struct Agent {
        uint256 agentId;
        address walletAddress;
        string agentType;        // "matching", "moving", "guardian", "landlord", "tenant", "p2p-community", "savings"
        uint256 balance;         // HBAR balance in tinybars (1 HBAR = 10^8 tinybars)
        uint256 reputation;      // 0-100 score
        uint256 stakedAmount;    // HBAR staked for reputation
        string[] capabilities;   // ["move-apartments", "negotiate-leases", "analyze-market"]
        bool isActive;
        uint256 registeredAt;
        uint256 lastActivity;
    }

    // Service offer structure
    struct ServiceOffer {
        uint256 offerId;
        uint256 agentId;
        string serviceType;      // "moving-service", "lease-negotiation", "market-analysis"
        string description;
        uint256 basePrice;       // Base price in tinybars
        uint256 variableFee;     // Variable fee as percentage (basis points, 100 = 1%)
        uint256 minOrderValue;   // Minimum order value in tinybars
        bool isActive;
        uint256 createdAt;
        uint256 totalTransactions;
        uint256 totalRevenue;
    }

    // Transaction record
    struct AgentTransaction {
        uint256 txId;
        uint256 fromAgent;
        uint256 toAgent;
        uint256 amount;          // Amount in tinybars
        string serviceType;
        uint256 timestamp;
        TransactionStatus status;
    }

    enum TransactionStatus { PENDING, COMPLETED, DISPUTED, CANCELLED }

    // State variables
    mapping(uint256 => Agent) public agents;
    mapping(uint256 => ServiceOffer) public offers;
    mapping(uint256 => AgentTransaction) public transactions;
    mapping(address => uint256) public addressToAgentId;
    mapping(string => uint256[]) public serviceTypeToOffers; // Service discovery

    uint256 public nextAgentId = 1;
    uint256 public nextOfferId = 1;
    uint256 public nextTxId = 1;
    uint256 public totalAgents;
    uint256 public totalOffers;
    uint256 public totalTransactions;

    // Events
    event AgentRegistered(uint256 indexed agentId, string agentType, address wallet);
    event ServiceOfferCreated(uint256 indexed offerId, uint256 indexed agentId, string serviceType);
    event ServiceOfferUpdated(uint256 indexed offerId, uint256 newBasePrice);
    event TransferBetweenAgents(uint256 indexed fromAgent, uint256 indexed toAgent, uint256 amount, string serviceType);
    event ServiceExecuted(uint256 indexed offerId, uint256 indexed requestorAgentId, uint256 indexed providerAgentId, uint256 amount);
    event ReputationUpdated(uint256 indexed agentId, uint256 newReputation);
    event AgentStaked(uint256 indexed agentId, uint256 amount);
    event AgentUnstaked(uint256 indexed agentId, uint256 amount);

    // Modifiers
    modifier onlyAgent(uint256 agentId) {
        require(agents[agentId].walletAddress == msg.sender, "Only agent owner can call");
        require(agents[agentId].isActive, "Agent is not active");
        _;
    }

    modifier validAgent(uint256 agentId) {
        require(agentId > 0 && agentId < nextAgentId, "Invalid agent ID");
        require(agents[agentId].isActive, "Agent is not active");
        _;
    }

    modifier validOffer(uint256 offerId) {
        require(offerId > 0 && offerId < nextOfferId, "Invalid offer ID");
        require(offers[offerId].isActive, "Offer is not active");
        _;
    }

    /**
     * @dev Register a new AI agent in the economy
     * @param agentType Type of agent (matching, moving, guardian, etc.)
     * @param capabilities Array of service capabilities
     * @param walletAddress Agent's Hedera wallet address
     */
    function registerAgent(
        string memory agentType,
        string[] memory capabilities,
        address walletAddress
    ) external returns (uint256) {
        require(walletAddress != address(0), "Invalid wallet address");
        require(addressToAgentId[walletAddress] == 0, "Wallet already registered");

        uint256 agentId = nextAgentId++;
        agents[agentId] = Agent({
            agentId: agentId,
            walletAddress: walletAddress,
            agentType: agentType,
            balance: 0,
            reputation: 50,      // Start at neutral reputation
            stakedAmount: 0,
            capabilities: capabilities,
            isActive: true,
            registeredAt: block.timestamp,
            lastActivity: block.timestamp
        });

        addressToAgentId[walletAddress] = agentId;
        totalAgents++;

        emit AgentRegistered(agentId, agentType, walletAddress);
        return agentId;
    }

    /**
     * @dev Create a service offer that other agents can purchase
     * @param agentId ID of the offering agent
     * @param serviceType Type of service offered
     * @param description Human-readable description
     * @param basePrice Base price in tinybars
     * @param variableFee Variable fee in basis points (100 = 1%)
     * @param minOrderValue Minimum order value in tinybars
     */
    function createServiceOffer(
        uint256 agentId,
        string memory serviceType,
        string memory description,
        uint256 basePrice,
        uint256 variableFee,
        uint256 minOrderValue
    ) external onlyAgent(agentId) returns (uint256) {
        require(bytes(serviceType).length > 0, "Service type required");
        require(basePrice > 0, "Base price must be > 0");
        require(variableFee <= 10000, "Variable fee cannot exceed 100%");

        uint256 offerId = nextOfferId++;
        offers[offerId] = ServiceOffer({
            offerId: offerId,
            agentId: agentId,
            serviceType: serviceType,
            description: description,
            basePrice: basePrice,
            variableFee: variableFee,
            minOrderValue: minOrderValue,
            isActive: true,
            createdAt: block.timestamp,
            totalTransactions: 0,
            totalRevenue: 0
        });

        // Add to service discovery mapping
        serviceTypeToOffers[serviceType].push(offerId);
        totalOffers++;

        emit ServiceOfferCreated(offerId, agentId, serviceType);
        return offerId;
    }

    /**
     * @dev Update an existing service offer
     * @param offerId ID of the offer to update
     * @param newBasePrice New base price
     * @param newVariableFee New variable fee
     */
    function updateServiceOffer(
        uint256 offerId,
        uint256 newBasePrice,
        uint256 newVariableFee
    ) external validOffer(offerId) {
        ServiceOffer storage offer = offers[offerId];
        require(offer.agentId == addressToAgentId[msg.sender], "Not offer owner");

        offer.basePrice = newBasePrice;
        offer.variableFee = newVariableFee;

        emit ServiceOfferUpdated(offerId, newBasePrice);
    }

    /**
     * @dev Execute a service by purchasing it from another agent
     * @param offerId ID of the service offer
     * @param requestorAgentId ID of the requesting agent
     * @param orderValue Value of the order for variable fee calculation
     */
    function executeService(
        uint256 offerId,
        uint256 requestorAgentId,
        uint256 orderValue
    ) external payable validOffer(offerId) validAgent(requestorAgentId) nonReentrant returns (bool) {
        ServiceOffer storage offer = offers[offerId];
        require(orderValue >= offer.minOrderValue, "Order value below minimum");

        // Calculate total price: base + (orderValue * variableFee / 10000)
        uint256 variableAmount = (orderValue * offer.variableFee) / 10000;
        uint256 totalPrice = offer.basePrice + variableAmount;

        // Check requesting agent has sufficient balance
        require(agents[requestorAgentId].balance >= totalPrice, "Insufficient balance");

        // Transfer funds
        agents[requestorAgentId].balance -= totalPrice;
        agents[offer.agentId].balance += totalPrice;

        // Update offer statistics
        offer.totalTransactions++;
        offer.totalRevenue += totalPrice;

        // Update activity timestamps
        agents[requestorAgentId].lastActivity = block.timestamp;
        agents[offer.agentId].lastActivity = block.timestamp;

        // Update reputation (simple algorithm: successful transaction increases reputation)
        _updateReputation(offer.agentId, 1); // Small positive boost

        emit ServiceExecuted(offerId, requestorAgentId, offer.agentId, totalPrice);
        return true;
    }

    /**
     * @dev Direct transfer between agents
     * @param fromAgentId Sending agent ID
     * @param toAgentId Receiving agent ID
     * @param amount Amount in tinybars
     * @param serviceType Description of service/payment reason
     */
    function transferBetweenAgents(
        uint256 fromAgentId,
        uint256 toAgentId,
        uint256 amount,
        string memory serviceType
    ) external onlyAgent(fromAgentId) validAgent(toAgentId) nonReentrant {
        require(amount > 0, "Amount must be > 0");
        require(agents[fromAgentId].balance >= amount, "Insufficient balance");

        // Execute transfer
        agents[fromAgentId].balance -= amount;
        agents[toAgentId].balance += amount;

        // Record transaction
        uint256 txId = nextTxId++;
        transactions[txId] = AgentTransaction({
            txId: txId,
            fromAgent: fromAgentId,
            toAgent: toAgentId,
            amount: amount,
            serviceType: serviceType,
            timestamp: block.timestamp,
            status: TransactionStatus.COMPLETED
        });

        totalTransactions++;

        // Update activity
        agents[fromAgentId].lastActivity = block.timestamp;
        agents[toAgentId].lastActivity = block.timestamp;

        emit TransferBetweenAgents(fromAgentId, toAgentId, amount, serviceType);
    }

    /**
     * @dev Deposit HBAR to agent balance (called by agent owners)
     * @param agentId ID of the agent to deposit to
     */
    function depositToAgent(uint256 agentId) external payable validAgent(agentId) {
        require(msg.value > 0, "Deposit amount must be > 0");
        agents[agentId].balance += msg.value;
    }

    /**
     * @dev Withdraw HBAR from agent balance
     * @param agentId ID of the agent withdrawing
     * @param amount Amount to withdraw in tinybars
     */
    function withdrawFromAgent(uint256 agentId, uint256 amount) external onlyAgent(agentId) nonReentrant {
        require(amount > 0, "Withdraw amount must be > 0");
        require(agents[agentId].balance >= amount, "Insufficient balance");

        agents[agentId].balance -= amount;

        // Transfer HBAR back to agent owner
        payable(agents[agentId].walletAddress).transfer(amount);
    }

    /**
     * @dev Stake HBAR to boost reputation
     * @param agentId ID of the staking agent
     * @param amount Amount to stake
     */
    function stakeForReputation(uint256 agentId, uint256 amount) external onlyAgent(agentId) {
        require(amount > 0, "Stake amount must be > 0");
        require(agents[agentId].balance >= amount, "Insufficient balance");

        agents[agentId].balance -= amount;
        agents[agentId].stakedAmount += amount;

        // Boost reputation based on stake amount
        uint256 reputationBoost = (amount / 10**8) / 10; // 1 HBAR staked = 0.1 reputation boost
        _updateReputation(agentId, int256(reputationBoost));

        emit AgentStaked(agentId, amount);
    }

    /**
     * @dev Unstake HBAR (with penalty if reputation drops)
     * @param agentId ID of the unstaking agent
     * @param amount Amount to unstake
     */
    function unstakeReputation(uint256 agentId, uint256 amount) external onlyAgent(agentId) {
        require(amount > 0, "Unstake amount must be > 0");
        require(agents[agentId].stakedAmount >= amount, "Insufficient staked amount");

        agents[agentId].stakedAmount -= amount;
        agents[agentId].balance += amount;

        // Small reputation penalty for unstaking
        _updateReputation(agentId, -2);

        emit AgentUnstaked(agentId, amount);
    }

    /**
     * @dev Get agent balance
     * @param agentId Agent ID
     */
    function getAgentBalance(uint256 agentId) external view validAgent(agentId) returns (uint256) {
        return agents[agentId].balance;
    }

    /**
     * @dev Get agent capabilities
     * @param agentId Agent ID
     */
    function getAgentCapabilities(uint256 agentId) external view validAgent(agentId) returns (string[] memory) {
        return agents[agentId].capabilities;
    }

    /**
     * @dev Discover service offers by type
     * @param serviceType Type of service to search for
     */
    function getServiceOffers(string memory serviceType) external view returns (uint256[] memory) {
        return serviceTypeToOffers[serviceType];
    }

    /**
     * @dev Get all active agents (for discovery)
     */
    function getAllAgents() external view returns (uint256[] memory) {
        uint256[] memory activeAgents = new uint256[](totalAgents);
        uint256 count = 0;
        for (uint256 i = 1; i < nextAgentId; i++) {
            if (agents[i].isActive) {
                activeAgents[count] = i;
                count++;
            }
        }
        return activeAgents;
    }

    /**
     * @dev Internal function to update agent reputation
     * @param agentId Agent ID
     * @param delta Change in reputation (-100 to +100)
     */
    function _updateReputation(uint256 agentId, int256 delta) internal {
        uint256 currentRep = agents[agentId].reputation;
        uint256 newRep;

        if (delta > 0) {
            newRep = currentRep + uint256(delta);
            if (newRep > 100) newRep = 100;
        } else {
            if (uint256(-delta) >= currentRep) {
                newRep = 0;
            } else {
                newRep = currentRep - uint256(-delta);
            }
        }

        agents[agentId].reputation = newRep;
        emit ReputationUpdated(agentId, newRep);
    }

    /**
     * @dev Emergency pause for agent
     * @param agentId Agent to pause
     */
    function pauseAgent(uint256 agentId) external onlyOwner validAgent(agentId) {
        agents[agentId].isActive = false;
    }

    /**
     * @dev Reactivate paused agent
     * @param agentId Agent to reactivate
     */
    function reactivateAgent(uint256 agentId) external onlyOwner {
        require(agentId > 0 && agentId < nextAgentId, "Invalid agent ID");
        agents[agentId].isActive = true;
    }
}