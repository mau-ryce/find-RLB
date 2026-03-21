// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./AgentEconomy.sol";

/**
 * @title CrossChainService
 * @dev Cross-chain interoperability for agent services
 * Enables agents to access services on other blockchains (Ethereum, Polygon, etc.)
 */
contract CrossChainService is Ownable, ReentrancyGuard {
    AgentEconomy public agentEconomy;

    enum ChainType { HEDERA, ETHEREUM, POLYGON, BSC, ARBITRUM, OPTIMISM }
    enum BridgeType { NATIVE, THIRD_PARTY, CUSTOM }

    struct CrossChainService {
        uint256 serviceId;
        string serviceName;
        ChainType chainType;
        address contractAddress;    // Address on target chain
        BridgeType bridgeType;
        address bridgeContract;     // Bridge contract address
        uint256 chainId;           // Target chain ID
        bool isActive;
        uint256 fee;              // Cross-chain fee in HBAR
        uint256 createdAt;
    }

    struct CrossChainRequest {
        uint256 requestId;
        uint256 agentId;
        uint256 serviceId;
        bytes requestData;
        uint256 value;            // HBAR value to send
        uint256 targetChainId;
        address targetContract;
        bytes32 requestHash;
        RequestStatus status;
        uint256 createdAt;
        uint256 completedAt;
    }

    enum RequestStatus { PENDING, PROCESSING, COMPLETED, FAILED }

    // State variables
    mapping(uint256 => CrossChainService) public crossChainServices;
    mapping(uint256 => CrossChainRequest) public crossChainRequests;
    mapping(bytes32 => uint256) public requestHashToId;
    mapping(ChainType => mapping(uint256 => bool)) public supportedServices; // chainType => serviceId => supported

    uint256 public nextServiceId = 1;
    uint256 public nextRequestId = 1;

    // Bridge configurations
    mapping(ChainType => address) public bridgeAddresses;
    mapping(ChainType => uint256) public chainIds;

    // Events
    event CrossChainServiceRegistered(uint256 indexed serviceId, string serviceName, ChainType chainType);
    event CrossChainRequestCreated(uint256 indexed requestId, uint256 indexed agentId, uint256 indexed serviceId);
    event CrossChainRequestCompleted(uint256 indexed requestId, bytes result);
    event BridgeUpdated(ChainType chainType, address bridgeAddress);

    constructor(address _agentEconomy) {
        agentEconomy = AgentEconomy(_agentEconomy);

        // Initialize supported chains
        chainIds[ChainType.ETHEREUM] = 1;
        chainIds[ChainType.POLYGON] = 137;
        chainIds[ChainType.BSC] = 56;
        chainIds[ChainType.ARBITRUM] = 42161;
        chainIds[ChainType.OPTIMISM] = 10;
    }

    /**
     * @dev Register a cross-chain service
     */
    function registerCrossChainService(
        string memory serviceName,
        ChainType chainType,
        address contractAddress,
        BridgeType bridgeType,
        address bridgeContract,
        uint256 fee
    ) external onlyOwner returns (uint256) {
        uint256 serviceId = nextServiceId++;

        crossChainServices[serviceId] = CrossChainService({
            serviceId: serviceId,
            serviceName: serviceName,
            chainType: chainType,
            contractAddress: contractAddress,
            bridgeType: bridgeType,
            bridgeContract: bridgeContract,
            chainId: chainIds[chainType],
            isActive: true,
            fee: fee,
            createdAt: block.timestamp
        });

        supportedServices[chainType][serviceId] = true;

        emit CrossChainServiceRegistered(serviceId, serviceName, chainType);
        return serviceId;
    }

    /**
     * @dev Update bridge address for a chain
     */
    function updateBridgeAddress(ChainType chainType, address bridgeAddress) external onlyOwner {
        bridgeAddresses[chainType] = bridgeAddress;
        emit BridgeUpdated(chainType, bridgeAddress);
    }

    /**
     * @dev Create a cross-chain service request
     */
    function createCrossChainRequest(
        uint256 agentId,
        uint256 serviceId,
        bytes memory requestData,
        uint256 value
    ) external payable returns (uint256) {
        CrossChainService storage service = crossChainServices[serviceId];
        require(service.isActive, "Service not active");
        require(msg.value >= service.fee + value, "Insufficient payment");

        // Check agent has sufficient balance
        require(agentEconomy.getAgentBalance(agentId) >= value, "Insufficient agent balance");

        uint256 requestId = nextRequestId++;
        bytes32 requestHash = keccak256(abi.encodePacked(requestId, agentId, serviceId, requestData, block.timestamp));

        crossChainRequests[requestId] = CrossChainRequest({
            requestId: requestId,
            agentId: agentId,
            serviceId: serviceId,
            requestData: requestData,
            value: value,
            targetChainId: service.chainId,
            targetContract: service.contractAddress,
            requestHash: requestHash,
            status: RequestStatus.PENDING,
            createdAt: block.timestamp,
            completedAt: 0
        });

        requestHashToId[requestHash] = requestId;

        // Deduct from agent balance
        agentEconomy.transferBetweenAgents(agentId, 0, value, "cross-chain-service"); // 0 = system

        emit CrossChainRequestCreated(requestId, agentId, serviceId);
        return requestId;
    }

    /**
     * @dev Execute cross-chain request via bridge
     */
    function executeCrossChainRequest(uint256 requestId) external nonReentrant {
        CrossChainRequest storage request = crossChainRequests[requestId];
        require(request.status == RequestStatus.PENDING, "Request not pending");

        CrossChainService storage service = crossChainServices[request.serviceId];
        request.status = RequestStatus.PROCESSING;

        // Execute via bridge
        if (service.bridgeType == BridgeType.NATIVE) {
            _executeNativeBridge(request, service);
        } else if (service.bridgeType == BridgeType.THIRD_PARTY) {
            _executeThirdPartyBridge(request, service);
        } else {
            _executeCustomBridge(request, service);
        }
    }

    /**
     * @dev Complete cross-chain request with result
     */
    function completeCrossChainRequest(
        bytes32 requestHash,
        bytes memory result,
        bool success
    ) external {
        uint256 requestId = requestHashToId[requestHash];
        require(requestId > 0, "Request not found");

        CrossChainRequest storage request = crossChainRequests[requestId];
        require(request.status == RequestStatus.PROCESSING, "Request not processing");

        if (success) {
            request.status = RequestStatus.COMPLETED;

            // Process result and potentially return value to agent
            _processCrossChainResult(request, result);
        } else {
            request.status = RequestStatus.FAILED;

            // Refund agent
            agentEconomy.depositToAgent(request.agentId, request.value);
        }

        request.completedAt = block.timestamp;

        emit CrossChainRequestCompleted(requestId, result);
    }

    /**
     * @dev Get supported services for a chain
     */
    function getSupportedServices(ChainType chainType) external view returns (uint256[] memory) {
        uint256[] memory services = new uint256[](nextServiceId);
        uint256 count = 0;

        for (uint256 i = 1; i < nextServiceId; i++) {
            if (supportedServices[chainType][i]) {
                services[count] = i;
                count++;
            }
        }

        // Resize array
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = services[i];
        }

        return result;
    }

    /**
     * @dev Estimate cross-chain fee
     */
    function estimateCrossChainFee(uint256 serviceId, uint256 value) external view returns (uint256) {
        CrossChainService storage service = crossChainServices[serviceId];
        require(service.isActive, "Service not active");

        // Base fee + value-dependent fee
        uint256 baseFee = service.fee;
        uint256 valueFee = (value * 5) / 1000; // 0.5% of value

        return baseFee + valueFee;
    }

    // Internal bridge execution functions

    function _executeNativeBridge(CrossChainRequest memory request, CrossChainService memory service) internal {
        // Native Hedera bridge logic (simplified)
        // In practice, this would interact with Hedera's cross-chain services

        // For demo purposes, simulate successful execution
        bytes memory mockResult = abi.encode("success", request.requestId);
        _completeRequest(request.requestId, mockResult, true);
    }

    function _executeThirdPartyBridge(CrossChainRequest memory request, CrossChainService memory service) internal {
        // Third-party bridge (e.g., Multichain, Celer) logic
        address bridge = bridgeAddresses[service.chainType];
        require(bridge != address(0), "Bridge not configured");

        // Call bridge contract (simplified)
        (bool success,) = bridge.call(
            abi.encodeWithSignature(
                "sendMessage(uint256,address,bytes,uint256)",
                request.targetChainId,
                request.targetContract,
                request.requestData,
                request.value
            )
        );

        if (!success) {
            _completeRequest(request.requestId, "", false);
        }
    }

    function _executeCustomBridge(CrossChainRequest memory request, CrossChainService memory service) internal {
        // Custom bridge logic
        address bridge = service.bridgeContract;

        (bool success,) = bridge.call(
            abi.encodeWithSignature(
                "initiateCrossChainCall(bytes32,uint256,address,bytes,uint256)",
                request.requestHash,
                request.targetChainId,
                request.targetContract,
                request.requestData,
                request.value
            )
        );

        if (!success) {
            _completeRequest(request.requestId, "", false);
        }
    }

    function _processCrossChainResult(CrossChainRequest memory request, bytes memory result) internal {
        // Process the result from cross-chain execution
        // This could involve:
        // - Updating agent balances
        // - Triggering follow-up actions
        // - Storing results for agent consumption

        // For now, just log the result
        // In practice, decode result and take appropriate actions
    }

    function _completeRequest(uint256 requestId, bytes memory result, bool success) internal {
        bytes32 requestHash = crossChainRequests[requestId].requestHash;
        completeCrossChainRequest(requestHash, result, success);
    }

    // View functions

    function getCrossChainService(uint256 serviceId) external view returns (
        uint256, string memory, ChainType, address, BridgeType, address, uint256, bool, uint256
    ) {
        CrossChainService storage service = crossChainServices[serviceId];
        return (
            service.serviceId,
            service.serviceName,
            service.chainType,
            service.contractAddress,
            service.bridgeType,
            service.bridgeContract,
            service.chainId,
            service.isActive,
            service.fee
        );
    }

    function getCrossChainRequest(uint256 requestId) external view returns (
        uint256, uint256, uint256, bytes memory, uint256, uint256, address, bytes32, RequestStatus, uint256, uint256
    ) {
        CrossChainRequest storage request = crossChainRequests[requestId];
        return (
            request.requestId,
            request.agentId,
            request.serviceId,
            request.requestData,
            request.value,
            request.targetChainId,
            request.targetContract,
            request.requestHash,
            request.status,
            request.createdAt,
            request.completedAt
        );
    }
}