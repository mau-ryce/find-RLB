// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./AgentEconomy.sol";

/**
 * @title AIOptimization
 * @dev Reinforcement learning system for agent optimization
 * Enables agents to learn optimal strategies for pricing, negotiation, and decision-making
 */
contract AIOptimization is Ownable, ReentrancyGuard {
    AgentEconomy public agentEconomy;

    struct LearningModel {
        uint256 modelId;
        uint256 agentId;
        string modelType;          // "pricing", "negotiation", "matching", "resource-allocation"
        bytes modelParams;         // Serialized model parameters
        uint256 version;
        uint256 accuracy;          // Model performance metric (0-10000, basis points)
        uint256 trainingDataPoints;
        uint256 lastUpdated;
        bool isActive;
    }

    struct Experience {
        uint256 experienceId;
        uint256 agentId;
        uint256 modelId;
        bytes state;               // Environment state
        bytes action;              // Action taken
        int256 reward;             // Reward received
        bytes nextState;           // Next state
        uint256 timestamp;
    }

    struct OptimizationTask {
        uint256 taskId;
        uint256 agentId;
        string taskType;           // "price-optimization", "negotiation-strategy", "resource-bidding"
        bytes taskParams;
        uint256[] relevantModels;
        uint256 deadline;
        bool isCompleted;
        bytes result;
        uint256 createdAt;
    }

    // State variables
    mapping(uint256 => LearningModel) public learningModels;
    mapping(uint256 => Experience[]) public modelExperiences;
    mapping(uint256 => OptimizationTask) public optimizationTasks;

    uint256 public nextModelId = 1;
    uint256 public nextExperienceId = 1;
    uint256 public nextTaskId = 1;

    // RL hyperparameters (can be updated by governance)
    uint256 public learningRate = 100;     // Basis points (1% = 100)
    uint256 public discountFactor = 900;   // 90%
    uint256 public explorationRate = 100;  // 1%

    // Events
    event ModelCreated(uint256 indexed modelId, uint256 indexed agentId, string modelType);
    event ExperienceRecorded(uint256 indexed modelId, uint256 indexed experienceId);
    event ModelUpdated(uint256 indexed modelId, uint256 newAccuracy);
    event OptimizationTaskCreated(uint256 indexed taskId, uint256 indexed agentId);
    event OptimizationCompleted(uint256 indexed taskId, bytes result);

    constructor(address _agentEconomy) {
        agentEconomy = AgentEconomy(_agentEconomy);
    }

    /**
     * @dev Create a new learning model for an agent
     */
    function createLearningModel(
        uint256 agentId,
        string memory modelType,
        bytes memory initialParams
    ) external returns (uint256) {
        uint256 modelId = nextModelId++;

        learningModels[modelId] = LearningModel({
            modelId: modelId,
            agentId: agentId,
            modelType: modelType,
            modelParams: initialParams,
            version: 1,
            accuracy: 5000,        // Start at 50%
            trainingDataPoints: 0,
            lastUpdated: block.timestamp,
            isActive: true
        });

        emit ModelCreated(modelId, agentId, modelType);
        return modelId;
    }

    /**
     * @dev Record an experience for model training
     */
    function recordExperience(
        uint256 modelId,
        bytes memory state,
        bytes memory action,
        int256 reward,
        bytes memory nextState
    ) external returns (uint256) {
        LearningModel storage model = learningModels[modelId];
        require(model.isActive, "Model not active");

        uint256 experienceId = nextExperienceId++;

        Experience memory exp = Experience({
            experienceId: experienceId,
            agentId: model.agentId,
            modelId: modelId,
            state: state,
            action: action,
            reward: reward,
            nextState: nextState,
            timestamp: block.timestamp
        });

        modelExperiences[modelId].push(exp);
        model.trainingDataPoints++;

        emit ExperienceRecorded(modelId, experienceId);

        // Trigger model update if enough experiences collected
        if (modelExperiences[modelId].length >= 10) {
            _updateModel(modelId);
        }

        return experienceId;
    }

    /**
     * @dev Create an optimization task
     */
    function createOptimizationTask(
        uint256 agentId,
        string memory taskType,
        bytes memory taskParams,
        uint256[] memory relevantModels,
        uint256 durationHours
    ) external returns (uint256) {
        uint256 taskId = nextTaskId++;

        optimizationTasks[taskId] = OptimizationTask({
            taskId: taskId,
            agentId: agentId,
            taskType: taskType,
            taskParams: taskParams,
            relevantModels: relevantModels,
            deadline: block.timestamp + (durationHours * 1 hours),
            isCompleted: false,
            result: "",
            createdAt: block.timestamp
        });

        emit OptimizationTaskCreated(taskId, agentId);
        return taskId;
    }

    /**
     * @dev Execute optimization using available models
     */
    function executeOptimization(uint256 taskId) external {
        OptimizationTask storage task = optimizationTasks[taskId];
        require(!task.isCompleted, "Task already completed");
        require(block.timestamp <= task.deadline, "Task deadline passed");

        bytes memory result;

        if (keccak256(abi.encodePacked(task.taskType)) == keccak256(abi.encodePacked("price-optimization"))) {
            result = _optimizePricing(task);
        } else if (keccak256(abi.encodePacked(task.taskType)) == keccak256(abi.encodePacked("negotiation-strategy"))) {
            result = _optimizeNegotiation(task);
        } else if (keccak256(abi.encodePacked(task.taskType)) == keccak256(abi.encodePacked("resource-bidding"))) {
            result = _optimizeResourceBidding(task);
        }

        task.isCompleted = true;
        task.result = result;

        emit OptimizationCompleted(taskId, result);
    }

    /**
     * @dev Get model prediction for a given state
     */
    function getModelPrediction(uint256 modelId, bytes memory state) external view returns (bytes memory) {
        LearningModel storage model = learningModels[modelId];
        require(model.isActive, "Model not active");

        // Simple Q-learning prediction (simplified)
        return _predictAction(model, state);
    }

    /**
     * @dev Update RL hyperparameters (governance function)
     */
    function updateHyperparameters(
        uint256 _learningRate,
        uint256 _discountFactor,
        uint256 _explorationRate
    ) external onlyOwner {
        require(_learningRate <= 1000, "Learning rate too high");     // Max 10%
        require(_discountFactor <= 1000, "Discount factor too high"); // Max 100%
        require(_explorationRate <= 1000, "Exploration rate too high"); // Max 10%

        learningRate = _learningRate;
        discountFactor = _discountFactor;
        explorationRate = _explorationRate;
    }

    // Internal optimization functions

    function _optimizePricing(OptimizationTask memory task) internal view returns (bytes memory) {
        // Price optimization using reinforcement learning
        // Analyze historical pricing data and market conditions

        // Simplified: Use Q-learning to find optimal price point
        uint256 optimalPrice = _calculateOptimalPrice(task.relevantModels, task.taskParams);

        return abi.encode("optimal_price", optimalPrice);
    }

    function _optimizeNegotiation(OptimizationTask memory task) internal view returns (bytes memory) {
        // Negotiation strategy optimization
        // Learn from past negotiation outcomes

        NegotiationStrategy memory strategy = _calculateNegotiationStrategy(task.relevantModels, task.taskParams);

        return abi.encode("negotiation_strategy", strategy);
    }

    function _optimizeResourceBidding(OptimizationTask memory task) internal view returns (bytes memory) {
        // Resource bidding optimization
        // Optimize bids in multi-agent resource allocation

        uint256 optimalBid = _calculateOptimalBid(task.relevantModels, task.taskParams);

        return abi.encode("optimal_bid", optimalBid);
    }

    function _calculateOptimalPrice(uint256[] memory modelIds, bytes memory params) internal view returns (uint256) {
        // Simplified price optimization algorithm
        uint256 basePrice = abi.decode(params, (uint256));
        uint256 adjustment = 0;

        for (uint256 i = 0; i < modelIds.length; i++) {
            LearningModel storage model = learningModels[modelIds[i]];
            if (model.accuracy > 7000) { // Use high-accuracy models
                // Apply model-based adjustment
                adjustment += (model.accuracy - 5000) / 100; // Small adjustment based on accuracy
            }
        }

        return basePrice + adjustment;
    }

    function _calculateOptimalBid(uint256[] memory modelIds, bytes memory params) internal view returns (uint256) {
        // Simplified bid optimization
        (uint256 maxBudget, uint256 competitionLevel) = abi.decode(params, (uint256, uint256));

        // Conservative bidding strategy: bid at 70-90% of max budget based on competition
        uint256 bidPercentage = 7000 + (competitionLevel * 2000) / 10000; // 70% + up to 20% based on competition

        return (maxBudget * bidPercentage) / 10000;
    }

    function _predictAction(LearningModel memory model, bytes memory state) internal view returns (bytes memory) {
        // Simplified Q-learning action prediction
        // In practice, this would use the trained model parameters

        if (keccak256(abi.encodePacked(model.modelType)) == keccak256(abi.encodePacked("pricing"))) {
            // Price prediction
            uint256 predictedPrice = _decodeStatePrice(state) + 5; // Simple +5 adjustment
            return abi.encode("set_price", predictedPrice);
        } else if (keccak256(abi.encodePacked(model.modelType)) == keccak256(abi.encodePacked("negotiation"))) {
            // Negotiation action prediction
            return abi.encode("counter_offer", _decodeStatePrice(state) - 2);
        }

        return abi.encode("no_action");
    }

    function _updateModel(uint256 modelId) internal {
        LearningModel storage model = learningModels[modelId];
        Experience[] storage experiences = modelExperiences[modelId];

        // Simple Q-learning update (simplified)
        // In practice, this would update the model parameters based on experiences

        uint256 positiveExperiences = 0;
        for (uint256 i = 0; i < experiences.length; i++) {
            if (experiences[i].reward > 0) {
                positiveExperiences++;
            }
        }

        // Update accuracy based on positive experience ratio
        model.accuracy = (positiveExperiences * 10000) / experiences.length;
        model.version++;
        model.lastUpdated = block.timestamp;

        // Clear old experiences to save gas (keep last 50)
        if (experiences.length > 50) {
            // Remove oldest experiences
            for (uint256 i = 0; i < experiences.length - 50; i++) {
                experiences[i] = experiences[i + 50];
            }
            while (experiences.length > 50) {
                experiences.pop();
            }
        }

        emit ModelUpdated(modelId, model.accuracy);
    }

    function _decodeStatePrice(bytes memory state) internal pure returns (uint256) {
        // Helper to decode price from state
        return abi.decode(state, (uint256));
    }

    // View functions

    function getLearningModel(uint256 modelId) external view returns (
        uint256, uint256, string memory, bytes memory, uint256, uint256, uint256, uint256, bool
    ) {
        LearningModel storage model = learningModels[modelId];
        return (
            model.modelId,
            model.agentId,
            model.modelType,
            model.modelParams,
            model.version,
            model.accuracy,
            model.trainingDataPoints,
            model.lastUpdated,
            model.isActive
        );
    }

    function getModelExperiences(uint256 modelId) external view returns (Experience[] memory) {
        return modelExperiences[modelId];
    }

    function getOptimizationTask(uint256 taskId) external view returns (
        uint256, uint256, string memory, bytes memory, uint256[] memory, uint256, bool, bytes memory, uint256
    ) {
        OptimizationTask storage task = optimizationTasks[taskId];
        return (
            task.taskId,
            task.agentId,
            task.taskType,
            task.taskParams,
            task.relevantModels,
            task.deadline,
            task.isCompleted,
            task.result,
            task.createdAt
        );
    }

    // Struct for internal use
    struct NegotiationStrategy {
        uint256 initialOffer;
        uint256 minAcceptance;
        uint256 concessionRate;
        bool useAnchoring;
    }

    function _calculateNegotiationStrategy(uint256[] memory modelIds, bytes memory params)
        internal view returns (NegotiationStrategy memory) {

        // Simplified negotiation strategy calculation
        (uint256 targetPrice, uint256 marketRate) = abi.decode(params, (uint256, uint256));

        return NegotiationStrategy({
            initialOffer: targetPrice + (targetPrice * 110) / 100, // 10% above target
            minAcceptance: targetPrice - (targetPrice * 50) / 100, // 50% below target
            concessionRate: 50, // 5% concessions
            useAnchoring: marketRate > 80 // Use anchoring if market rate > 80%
        });
    }
}