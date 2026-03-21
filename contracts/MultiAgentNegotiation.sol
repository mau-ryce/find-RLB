// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./AgentEconomy.sol";

/**
 * @title MultiAgentNegotiation
 * @dev Advanced negotiation protocols for complex multi-agent workflows
 * Supports auctions, sequential bargaining, and collaborative decision-making
 */
contract MultiAgentNegotiation is Ownable, ReentrancyGuard {
    AgentEconomy public agentEconomy;

    enum NegotiationType { AUCTION, BARGAINING, COLLABORATIVE, COMPETITIVE }
    enum NegotiationStatus { ACTIVE, COMPLETED, CANCELLED, DISPUTED }
    enum BidType { OFFER, COUNTER_OFFER, ACCEPT, REJECT }

    struct Negotiation {
        uint256 negotiationId;
        uint256 initiatorAgent;
        NegotiationType negType;
        string workflowType;        // "lease-negotiation", "service-bundling", "resource-sharing"
        bytes workflowParams;       // Encoded workflow-specific parameters
        uint256[] participants;
        uint256[] requiredCapabilities;
        uint256 minParticipants;
        uint256 maxParticipants;
        uint256 deadline;
        NegotiationStatus status;
        uint256 createdAt;
        uint256 completedAt;
    }

    struct Bid {
        uint256 bidId;
        uint256 negotiationId;
        uint256 agentId;
        BidType bidType;
        bytes bidData;             // Encoded bid parameters
        uint256 stakeAmount;       // HBAR staked for commitment
        uint256 timestamp;
        bool isActive;
    }

    struct WorkflowStep {
        uint256 stepId;
        string stepType;           // "bid-collection", "counter-offers", "voting", "execution"
        bytes stepParams;
        uint256[] eligibleAgents;
        uint256 deadline;
        bool isCompleted;
        bytes stepResult;
    }

    // State variables
    mapping(uint256 => Negotiation) public negotiations;
    mapping(uint256 => Bid[]) public negotiationBids;
    mapping(uint256 => WorkflowStep[]) public negotiationWorkflow;
    mapping(uint256 => mapping(uint256 => bool)) public agentParticipation; // negotiationId => agentId => participated

    uint256 public nextNegotiationId = 1;
    uint256 public nextBidId = 1;
    uint256 public nextStepId = 1;

    // Events
    event NegotiationCreated(uint256 indexed negotiationId, uint256 indexed initiator, NegotiationType negType);
    event BidSubmitted(uint256 indexed negotiationId, uint256 indexed bidId, uint256 indexed agentId);
    event WorkflowStepCompleted(uint256 indexed negotiationId, uint256 indexed stepId);
    event NegotiationCompleted(uint256 indexed negotiationId, bytes result);
    event DisputeRaised(uint256 indexed negotiationId, uint256 indexed agentId, string reason);

    constructor(address _agentEconomy) {
        agentEconomy = AgentEconomy(_agentEconomy);
    }

    /**
     * @dev Create a new multi-agent negotiation
     */
    function createNegotiation(
        uint256 initiatorAgent,
        NegotiationType negType,
        string memory workflowType,
        bytes memory workflowParams,
        uint256[] memory requiredCapabilities,
        uint256 minParticipants,
        uint256 maxParticipants,
        uint256 durationHours
    ) external returns (uint256) {
        require(minParticipants >= 2, "Minimum 2 participants required");
        require(maxParticipants >= minParticipants, "Invalid participant limits");

        uint256 negotiationId = nextNegotiationId++;
        uint256 deadline = block.timestamp + (durationHours * 1 hours);

        negotiations[negotiationId] = Negotiation({
            negotiationId: negotiationId,
            initiatorAgent: initiatorAgent,
            negType: negType,
            workflowType: workflowType,
            workflowParams: workflowParams,
            participants: new uint256[](0),
            requiredCapabilities: requiredCapabilities,
            minParticipants: minParticipants,
            maxParticipants: maxParticipants,
            deadline: deadline,
            status: NegotiationStatus.ACTIVE,
            createdAt: block.timestamp,
            completedAt: 0
        });

        // Initialize workflow based on type
        _initializeWorkflow(negotiationId, negType, workflowType);

        emit NegotiationCreated(negotiationId, initiatorAgent, negType);
        return negotiationId;
    }

    /**
     * @dev Join a negotiation as a participant
     */
    function joinNegotiation(uint256 negotiationId, uint256 agentId) external {
        Negotiation storage neg = negotiations[negotiationId];
        require(neg.status == NegotiationStatus.ACTIVE, "Negotiation not active");
        require(block.timestamp < neg.deadline, "Negotiation deadline passed");
        require(neg.participants.length < neg.maxParticipants, "Maximum participants reached");
        require(!agentParticipation[negotiationId][agentId], "Agent already participating");

        // Check if agent has required capabilities
        bool hasCapabilities = _checkAgentCapabilities(agentId, neg.requiredCapabilities);
        require(hasCapabilities, "Agent lacks required capabilities");

        neg.participants.push(agentId);
        agentParticipation[negotiationId][agentId] = true;
    }

    /**
     * @dev Submit a bid in a negotiation
     */
    function submitBid(
        uint256 negotiationId,
        uint256 agentId,
        BidType bidType,
        bytes memory bidData,
        uint256 stakeAmount
    ) external payable returns (uint256) {
        Negotiation storage neg = negotiations[negotiationId];
        require(neg.status == NegotiationStatus.ACTIVE, "Negotiation not active");
        require(agentParticipation[negotiationId][agentId], "Agent not participating");
        require(msg.value >= stakeAmount, "Insufficient stake");

        uint256 bidId = nextBidId++;

        Bid memory newBid = Bid({
            bidId: bidId,
            negotiationId: negotiationId,
            agentId: agentId,
            bidType: bidType,
            bidData: bidData,
            stakeAmount: stakeAmount,
            timestamp: block.timestamp,
            isActive: true
        });

        negotiationBids[negotiationId].push(newBid);

        // Process bid based on workflow
        _processBidInWorkflow(negotiationId, newBid);

        emit BidSubmitted(negotiationId, bidId, agentId);
        return bidId;
    }

    /**
     * @dev Execute the next workflow step
     */
    function executeWorkflowStep(uint256 negotiationId) external {
        Negotiation storage neg = negotiations[negotiationId];
        require(neg.status == NegotiationStatus.ACTIVE, "Negotiation not active");

        WorkflowStep[] storage workflow = negotiationWorkflow[negotiationId];
        require(workflow.length > 0, "No workflow steps defined");

        // Find the current active step
        for (uint256 i = 0; i < workflow.length; i++) {
            if (!workflow[i].isCompleted) {
                _executeStep(negotiationId, i);
                break;
            }
        }
    }

    /**
     * @dev Complete a negotiation with results
     */
    function completeNegotiation(uint256 negotiationId, bytes memory result) external {
        Negotiation storage neg = negotiations[negotiationId];
        require(neg.status == NegotiationStatus.ACTIVE, "Negotiation not active");
        require(neg.participants.length >= neg.minParticipants, "Insufficient participants");

        neg.status = NegotiationStatus.COMPLETED;
        neg.completedAt = block.timestamp;

        // Distribute stakes and rewards based on result
        _distributeNegotiationRewards(negotiationId, result);

        emit NegotiationCompleted(negotiationId, result);
    }

    /**
     * @dev Raise a dispute in a negotiation
     */
    function raiseDispute(uint256 negotiationId, uint256 agentId, string memory reason) external {
        Negotiation storage neg = negotiations[negotiationId];
        require(neg.status == NegotiationStatus.ACTIVE, "Negotiation not active");
        require(agentParticipation[negotiationId][agentId], "Agent not participating");

        neg.status = NegotiationStatus.DISPUTED;

        emit DisputeRaised(negotiationId, agentId, reason);
    }

    // Internal functions

    function _initializeWorkflow(
        uint256 negotiationId,
        NegotiationType negType,
        string memory workflowType
    ) internal {
        WorkflowStep[] storage workflow = negotiationWorkflow[negotiationId];

        if (negType == NegotiationType.AUCTION) {
            // Auction workflow: bid collection -> winner selection -> execution
            workflow.push(WorkflowStep({
                stepId: nextStepId++,
                stepType: "bid-collection",
                stepParams: abi.encode("duration", 1 hours),
                eligibleAgents: negotiations[negotiationId].participants,
                deadline: block.timestamp + 1 hours,
                isCompleted: false,
                stepResult: ""
            }));

            workflow.push(WorkflowStep({
                stepId: nextStepId++,
                stepType: "winner-selection",
                stepParams: abi.encode("criteria", "lowest-price"),
                eligibleAgents: new uint256[](0), // System only
                deadline: block.timestamp + 2 hours,
                isCompleted: false,
                stepResult: ""
            }));
        } else if (negType == NegotiationType.BARGAINING) {
            // Bargaining workflow: initial offers -> counter-offers -> agreement
            workflow.push(WorkflowStep({
                stepId: nextStepId++,
                stepType: "initial-offers",
                stepParams: abi.encode("maxOffers", 3),
                eligibleAgents: negotiations[negotiationId].participants,
                deadline: block.timestamp + 30 minutes,
                isCompleted: false,
                stepResult: ""
            }));

            workflow.push(WorkflowStep({
                stepId: nextStepId++,
                stepType: "counter-offers",
                stepParams: abi.encode("rounds", 2),
                eligibleAgents: negotiations[negotiationId].participants,
                deadline: block.timestamp + 1 hours,
                isCompleted: false,
                stepResult: ""
            }));
        }
        // Add more workflow types as needed
    }

    function _processBidInWorkflow(uint256 negotiationId, Bid memory bid) internal {
        WorkflowStep[] storage workflow = negotiationWorkflow[negotiationId];

        // Find current active step and process bid accordingly
        for (uint256 i = 0; i < workflow.length; i++) {
            if (!workflow[i].isCompleted) {
                if (keccak256(abi.encodePacked(workflow[i].stepType)) == keccak256(abi.encodePacked("bid-collection"))) {
                    // Collect bids until deadline or max bids reached
                    Bid[] storage bids = negotiationBids[negotiationId];
                    if (bids.length >= 5 || block.timestamp >= workflow[i].deadline) {
                        workflow[i].isCompleted = true;
                        workflow[i].stepResult = abi.encode("bidsCollected", bids.length);
                        emit WorkflowStepCompleted(negotiationId, workflow[i].stepId);
                    }
                }
                break;
            }
        }
    }

    function _executeStep(uint256 negotiationId, uint256 stepIndex) internal {
        WorkflowStep storage step = negotiationWorkflow[negotiationId][stepIndex];

        if (keccak256(abi.encodePacked(step.stepType)) == keccak256(abi.encodePacked("winner-selection"))) {
            // Select winner based on criteria
            Bid[] storage bids = negotiationBids[negotiationId];
            uint256 winnerBidId = _selectWinner(bids);

            step.stepResult = abi.encode("winner", winnerBidId);
            step.isCompleted = true;

            emit WorkflowStepCompleted(negotiationId, step.stepId);
        }
        // Add more step execution logic as needed
    }

    function _selectWinner(Bid[] storage bids) internal view returns (uint256) {
        // Simple lowest price winner selection
        uint256 lowestPrice = type(uint256).max;
        uint256 winnerBidId = 0;

        for (uint256 i = 0; i < bids.length; i++) {
            if (bids[i].isActive) {
                // Decode price from bidData (simplified)
                uint256 price = abi.decode(bids[i].bidData, (uint256));
                if (price < lowestPrice) {
                    lowestPrice = price;
                    winnerBidId = bids[i].bidId;
                }
            }
        }

        return winnerBidId;
    }

    function _checkAgentCapabilities(uint256 agentId, uint256[] memory requiredCapabilities)
        internal view returns (bool) {
        // Check if agent has required capabilities (simplified)
        // In practice, this would query the AgentEconomy contract
        return true; // Placeholder
    }

    function _distributeNegotiationRewards(uint256 negotiationId, bytes memory result) internal {
        // Distribute stakes and rewards based on negotiation outcome
        Negotiation storage neg = negotiations[negotiationId];
        Bid[] storage bids = negotiationBids[negotiationId];

        // Return stakes to participants
        for (uint256 i = 0; i < bids.length; i++) {
            if (bids[i].isActive && bids[i].stakeAmount > 0) {
                // Transfer stake back to agent (simplified)
                payable(agentEconomy.agents(bids[i].agentId).walletAddress).transfer(bids[i].stakeAmount);
            }
        }
    }

    // View functions

    function getNegotiation(uint256 negotiationId) external view returns (
        uint256, uint256, NegotiationType, string memory, uint256[] memory,
        uint256, uint256, uint256, NegotiationStatus
    ) {
        Negotiation storage neg = negotiations[negotiationId];
        return (
            neg.negotiationId,
            neg.initiatorAgent,
            neg.negType,
            neg.workflowType,
            neg.participants,
            neg.minParticipants,
            neg.maxParticipants,
            neg.deadline,
            neg.status
        );
    }

    function getNegotiationBids(uint256 negotiationId) external view returns (Bid[] memory) {
        return negotiationBids[negotiationId];
    }

    function getWorkflowSteps(uint256 negotiationId) external view returns (WorkflowStep[] memory) {
        return negotiationWorkflow[negotiationId];
    }
}