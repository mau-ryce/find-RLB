// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./AgentEconomy.sol";

/**
 * @title AgentGovernance
 * @dev Decentralized governance system for the agent economy
 * Enables agents and stakeholders to propose and vote on system changes
 */
contract AgentGovernance is Ownable, ReentrancyGuard {
    AgentEconomy public agentEconomy;
    IERC20 public governanceToken;

    enum ProposalType {
        PARAMETER_UPDATE,
        CONTRACT_UPGRADE,
        AGENT_REGULATION,
        ECONOMIC_POLICY,
        SYSTEM_MAINTENANCE
    }

    enum ProposalStatus {
        PENDING,
        ACTIVE,
        SUCCEEDED,
        DEFEATED,
        EXECUTED,
        CANCELLED
    }

    struct Proposal {
        uint256 id;
        address proposer;
        ProposalType proposalType;
        string title;
        string description;
        bytes parameters;
        uint256 startTime;
        uint256 endTime;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        ProposalStatus status;
        mapping(address => Vote) votes;
        bool executed;
    }

    struct Vote {
        bool hasVoted;
        bool support;
        uint256 weight;
        uint256 timestamp;
    }

    struct GovernanceConfig {
        uint256 votingPeriod;        // Duration of voting period in seconds
        uint256 proposalThreshold;   // Minimum tokens needed to create proposal
        uint256 quorumThreshold;     // Minimum participation for valid proposal (basis points)
        uint256 timelockDelay;       // Delay before proposal execution
        uint256 executionGracePeriod; // Time window to execute after timelock
    }

    // State variables
    mapping(uint256 => Proposal) public proposals;
    mapping(address => uint256) public votingPower;
    mapping(address => uint256) public lastVoteTime;

    uint256 public proposalCount;
    GovernanceConfig public config;

    // Timelock for critical proposals
    mapping(uint256 => uint256) public timelockTimestamps;

    // Events
    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, ProposalType proposalType);
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 indexed proposalId);
    event ConfigUpdated(string parameter, uint256 oldValue, uint256 newValue);

    constructor(
        address _agentEconomy,
        address _governanceToken,
        GovernanceConfig memory _config
    ) {
        agentEconomy = AgentEconomy(_agentEconomy);
        governanceToken = IERC20(_governanceToken);
        config = _config;
    }

    /**
     * @dev Create a new governance proposal
     */
    function createProposal(
        ProposalType proposalType,
        string memory title,
        string memory description,
        bytes memory parameters
    ) external returns (uint256) {
        require(governanceToken.balanceOf(msg.sender) >= config.proposalThreshold, "Insufficient tokens to propose");

        proposalCount++;
        uint256 proposalId = proposalCount;

        Proposal storage proposal = proposals[proposalId];
        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.proposalType = proposalType;
        proposal.title = title;
        proposal.description = description;
        proposal.parameters = parameters;
        proposal.startTime = block.timestamp;
        proposal.endTime = block.timestamp + config.votingPeriod;
        proposal.status = ProposalStatus.ACTIVE;

        emit ProposalCreated(proposalId, msg.sender, proposalType);
        return proposalId;
    }

    /**
     * @dev Cast a vote on a proposal
     */
    function castVote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.status == ProposalStatus.ACTIVE, "Proposal not active");
        require(block.timestamp >= proposal.startTime && block.timestamp <= proposal.endTime, "Voting not open");
        require(!proposal.votes[msg.sender].hasVoted, "Already voted");

        uint256 weight = _getVotingWeight(msg.sender);

        if (support) {
            proposal.forVotes += weight;
        } else {
            proposal.againstVotes += weight;
        }

        proposal.votes[msg.sender] = Vote({
            hasVoted: true,
            support: support,
            weight: weight,
            timestamp: block.timestamp
        });

        lastVoteTime[msg.sender] = block.timestamp;

        emit VoteCast(proposalId, msg.sender, support, weight);
    }

    /**
     * @dev Execute a successful proposal
     */
    function executeProposal(uint256 proposalId) external nonReentrant {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.status == ProposalStatus.ACTIVE, "Proposal not active");
        require(block.timestamp > proposal.endTime, "Voting still open");

        // Check if proposal succeeded
        uint256 totalVotes = proposal.forVotes + proposal.againstVotes + proposal.abstainVotes;
        uint256 totalSupply = governanceToken.totalSupply();

        bool quorumReached = (totalVotes * 10000) / totalSupply >= config.quorumThreshold;
        bool majoritySupport = proposal.forVotes > proposal.againstVotes;

        if (quorumReached && majoritySupport) {
            proposal.status = ProposalStatus.SUCCEEDED;

            // Check if timelock is required
            if (_requiresTimelock(proposal.proposalType)) {
                timelockTimestamps[proposalId] = block.timestamp + config.timelockDelay;
            } else {
                _executeProposalLogic(proposal);
                proposal.executed = true;
                proposal.status = ProposalStatus.EXECUTED;
                emit ProposalExecuted(proposalId);
            }
        } else {
            proposal.status = ProposalStatus.DEFEATED;
        }
    }

    /**
     * @dev Execute a timelocked proposal
     */
    function executeTimelockedProposal(uint256 proposalId) external {
        require(timelockTimestamps[proposalId] > 0, "No timelock set");
        require(block.timestamp >= timelockTimestamps[proposalId], "Timelock not expired");
        require(block.timestamp <= timelockTimestamps[proposalId] + config.executionGracePeriod, "Execution window expired");

        Proposal storage proposal = proposals[proposalId];
        require(!proposal.executed, "Already executed");

        _executeProposalLogic(proposal);
        proposal.executed = true;
        proposal.status = ProposalStatus.EXECUTED;

        delete timelockTimestamps[proposalId];
        emit ProposalExecuted(proposalId);
    }

    /**
     * @dev Update governance configuration (only owner)
     */
    function updateConfig(GovernanceConfig memory newConfig) external onlyOwner {
        emit ConfigUpdated("votingPeriod", config.votingPeriod, newConfig.votingPeriod);
        emit ConfigUpdated("proposalThreshold", config.proposalThreshold, newConfig.proposalThreshold);
        emit ConfigUpdated("quorumThreshold", config.quorumThreshold, newConfig.quorumThreshold);
        emit ConfigUpdated("timelockDelay", config.timelockDelay, newConfig.timelockDelay);
        emit ConfigUpdated("executionGracePeriod", config.executionGracePeriod, newConfig.executionGracePeriod);

        config = newConfig;
    }

    /**
     * @dev Get voting weight for an address
     */
    function getVotingWeight(address voter) external view returns (uint256) {
        return _getVotingWeight(voter);
    }

    /**
     * @dev Get proposal details
     */
    function getProposal(uint256 proposalId) external view returns (
        uint256 id,
        address proposer,
        ProposalType proposalType,
        string memory title,
        string memory description,
        bytes memory parameters,
        uint256 startTime,
        uint256 endTime,
        uint256 forVotes,
        uint256 againstVotes,
        uint256 abstainVotes,
        ProposalStatus status,
        bool executed
    ) {
        Proposal storage proposal = proposals[proposalId];
        return (
            proposal.id,
            proposal.proposer,
            proposal.proposalType,
            proposal.title,
            proposal.description,
            proposal.parameters,
            proposal.startTime,
            proposal.endTime,
            proposal.forVotes,
            proposal.againstVotes,
            proposal.abstainVotes,
            proposal.status,
            proposal.executed
        );
    }

    /**
     * @dev Get vote details for a proposal and voter
     */
    function getVote(uint256 proposalId, address voter) external view returns (
        bool hasVoted,
        bool support,
        uint256 weight,
        uint256 timestamp
    ) {
        Vote storage vote = proposals[proposalId].votes[voter];
        return (vote.hasVoted, vote.support, vote.weight, vote.timestamp);
    }

    // Internal functions

    function _getVotingWeight(address voter) internal view returns (uint256) {
        // Voting weight based on governance token balance + agent reputation
        uint256 tokenBalance = governanceToken.balanceOf(voter);

        // Additional weight for registered agents
        try agentEconomy.getAgent(voter) returns (
            uint256 agentId,
            string memory name,
            string memory agentType,
            uint256 reputation,
            uint256 balance,
            bool isActive
        ) {
            if (isActive) {
                // Agents get 2x voting weight
                tokenBalance = tokenBalance * 2;
                // Additional weight based on reputation
                tokenBalance += reputation * 100; // 1 reputation point = 100 tokens
            }
        } catch {
            // Not an agent, use token balance only
        }

        return tokenBalance;
    }

    function _requiresTimelock(ProposalType proposalType) internal pure returns (bool) {
        return proposalType == ProposalType.CONTRACT_UPGRADE ||
               proposalType == ProposalType.ECONOMIC_POLICY ||
               proposalType == ProposalType.SYSTEM_MAINTENANCE;
    }

    function _executeProposalLogic(Proposal storage proposal) internal {
        if (proposal.proposalType == ProposalType.PARAMETER_UPDATE) {
            _executeParameterUpdate(proposal.parameters);
        } else if (proposal.proposalType == ProposalType.CONTRACT_UPGRADE) {
            _executeContractUpgrade(proposal.parameters);
        } else if (proposal.proposalType == ProposalType.AGENT_REGULATION) {
            _executeAgentRegulation(proposal.parameters);
        } else if (proposal.proposalType == ProposalType.ECONOMIC_POLICY) {
            _executeEconomicPolicy(proposal.parameters);
        } else if (proposal.proposalType == ProposalType.SYSTEM_MAINTENANCE) {
            _executeSystemMaintenance(proposal.parameters);
        }
    }

    function _executeParameterUpdate(bytes memory parameters) internal {
        // Decode and apply parameter updates
        (string memory paramName, uint256 newValue) = abi.decode(parameters, (string, uint256));

        if (keccak256(abi.encodePacked(paramName)) == keccak256(abi.encodePacked("agentFee"))) {
            // Update agent registration fee in AgentEconomy contract
            agentEconomy.updateAgentFee(newValue);
        } else if (keccak256(abi.encodePacked(paramName)) == keccak256(abi.encodePacked("serviceFee"))) {
            // Update service execution fee
            agentEconomy.updateServiceFee(newValue);
        }
        // Add more parameter updates as needed
    }

    function _executeContractUpgrade(bytes memory parameters) internal {
        // Contract upgrade logic would go here
        // This would typically involve updating contract addresses or calling upgrade functions
        (address newContract, bytes memory upgradeData) = abi.decode(parameters, (address, bytes));

        // Implementation would depend on the specific upgrade mechanism used
        // For example, using OpenZeppelin's upgradeable contracts
    }

    function _executeAgentRegulation(bytes memory parameters) internal {
        // Agent regulation changes
        (uint256 agentId, bool suspend, string memory reason) = abi.decode(parameters, (uint256, bool, string));

        if (suspend) {
            agentEconomy.suspendAgent(agentId, reason);
        } else {
            agentEconomy.reactivateAgent(agentId);
        }
    }

    function _executeEconomicPolicy(bytes memory parameters) internal {
        // Economic policy changes
        (string memory policyType, uint256 newValue) = abi.decode(parameters, (string, uint256));

        if (keccak256(abi.encodePacked(policyType)) == keccak256(abi.encodePacked("maxServicePrice"))) {
            agentEconomy.setMaxServicePrice(newValue);
        } else if (keccak256(abi.encodePacked(policyType)) == keccak256(abi.encodePacked("minAgentBalance"))) {
            agentEconomy.setMinAgentBalance(newValue);
        }
    }

    function _executeSystemMaintenance(bytes memory parameters) internal {
        // System maintenance operations
        (string memory operation, bytes memory operationData) = abi.decode(parameters, (string, bytes));

        if (keccak256(abi.encodePacked(operation)) == keccak256(abi.encodePacked("emergencyPause"))) {
            agentEconomy.emergencyPause();
        } else if (keccak256(abi.encodePacked(operation)) == keccak256(abi.encodePacked("emergencyUnpause"))) {
            agentEconomy.emergencyUnpause();
        }
    }
}