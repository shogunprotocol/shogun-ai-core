// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@chainlink/contracts/src/v0.8/functions/v1_0_0/FunctionsConsumer.sol";
import "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";

/**
 * @title ShogunFunctionsConsumer
 * @dev Smart contract to interact with deployed Chainlink Functions
 * @author Shogun AI Core Team
 */
contract ShogunFunctionsConsumer is FunctionsConsumer, ConfirmedOwner {
    using Functions for Functions.Request;

    // Events
    event StrategyRiskScoreReceived(bytes32 indexed requestId, uint256 riskScore);
    event CrossChainAPYReceived(bytes32 indexed requestId, uint256 apy);
    event AllocationOptimized(bytes32 indexed requestId, uint256[] allocations);
    event OracleHealthChecked(bytes32 indexed requestId, bool isHealthy);

    // Function IDs (replace with your actual deployed function IDs)
    bytes32 public constant STRATEGY_RISK_SCORING_FUNCTION_ID = bytes32("YOUR_STRATEGY_RISK_FUNCTION_ID");
    bytes32 public constant CROSS_CHAIN_APY_FUNCTION_ID = bytes32("YOUR_CROSS_CHAIN_APY_FUNCTION_ID");
    bytes32 public constant ALLOCATION_OPTIMIZATION_FUNCTION_ID = bytes32("YOUR_ALLOCATION_OPT_FUNCTION_ID");
    bytes32 public constant ORACLE_HEALTH_CHECK_FUNCTION_ID = bytes32("YOUR_ORACLE_HEALTH_FUNCTION_ID");

    // Gas limit for function execution
    uint32 public constant GAS_LIMIT = 300000;

    // Latest results
    mapping(bytes32 => uint256) public latestRiskScores;
    mapping(bytes32 => uint256) public latestAPYs;
    mapping(bytes32 => uint256[]) public latestAllocations;
    mapping(bytes32 => bool) public latestOracleHealth;

    constructor(address router) FunctionsConsumer(router) ConfirmedOwner(msg.sender) {}

    /**
     * @dev Request strategy risk scoring
     * @param strategyAddress The strategy contract address
     * @param tokens Array of token addresses
     * @param currentAllocation Current allocation percentage
     * @param maxAllocation Maximum allocation percentage
     * @param baseRiskScore Base risk score
     */
    function requestStrategyRiskScoring(
        string memory strategyAddress,
        string memory tokens,
        string memory currentAllocation,
        string memory maxAllocation,
        string memory baseRiskScore
    ) external onlyOwner returns (bytes32 requestId) {
        string[] memory args = new string[](5);
        args[0] = strategyAddress;
        args[1] = tokens;
        args[2] = currentAllocation;
        args[3] = maxAllocation;
        args[4] = baseRiskScore;

        Functions.Request memory req;
        req.initializeRequestForInlineJavaScript(""); // Source code is in the function
        req.addArgs(args);

        requestId = _sendRequest(req, STRATEGY_RISK_SCORING_FUNCTION_ID, GAS_LIMIT);
    }

    /**
     * @dev Request cross-chain APY data
     * @param protocol The protocol name
     * @param chain The chain name
     */
    function requestCrossChainAPY(
        string memory protocol,
        string memory chain
    ) external onlyOwner returns (bytes32 requestId) {
        string[] memory args = new string[](2);
        args[0] = protocol;
        args[1] = chain;

        Functions.Request memory req;
        req.initializeRequestForInlineJavaScript(""); // Source code is in the function
        req.addArgs(args);

        requestId = _sendRequest(req, CROSS_CHAIN_APY_FUNCTION_ID, GAS_LIMIT);
    }

    /**
     * @dev Request allocation optimization
     * @param vaults Array of vault addresses
     * @param currentAllocations Current allocation percentages
     * @param targetAPY Target APY
     */
    function requestAllocationOptimization(
        string memory vaults,
        string memory currentAllocations,
        string memory targetAPY
    ) external onlyOwner returns (bytes32 requestId) {
        string[] memory args = new string[](3);
        args[0] = vaults;
        args[1] = currentAllocations;
        args[2] = targetAPY;

        Functions.Request memory req;
        req.initializeRequestForInlineJavaScript(""); // Source code is in the function
        req.addArgs(args);

        requestId = _sendRequest(req, ALLOCATION_OPTIMIZATION_FUNCTION_ID, GAS_LIMIT);
    }

    /**
     * @dev Request oracle health check
     * @param oracleAddress The oracle address to check
     */
    function requestOracleHealthCheck(
        string memory oracleAddress
    ) external onlyOwner returns (bytes32 requestId) {
        string[] memory args = new string[](1);
        args[0] = oracleAddress;

        Functions.Request memory req;
        req.initializeRequestForInlineJavaScript(""); // Source code is in the function
        req.addArgs(args);

        requestId = _sendRequest(req, ORACLE_HEALTH_CHECK_FUNCTION_ID, GAS_LIMIT);
    }

    /**
     * @dev Callback function for strategy risk scoring
     */
    function _fulfillStrategyRiskScoring(bytes32 requestId, bytes memory response, bytes memory err) internal {
        if (err.length > 0) {
            revert("Strategy risk scoring failed");
        }

        // Parse the response (simplified - you'd want proper JSON parsing)
        uint256 riskScore = abi.decode(response, (uint256));
        latestRiskScores[requestId] = riskScore;

        emit StrategyRiskScoreReceived(requestId, riskScore);
    }

    /**
     * @dev Callback function for cross-chain APY
     */
    function _fulfillCrossChainAPY(bytes32 requestId, bytes memory response, bytes memory err) internal {
        if (err.length > 0) {
            revert("Cross-chain APY request failed");
        }

        uint256 apy = abi.decode(response, (uint256));
        latestAPYs[requestId] = apy;

        emit CrossChainAPYReceived(requestId, apy);
    }

    /**
     * @dev Callback function for allocation optimization
     */
    function _fulfillAllocationOptimization(bytes32 requestId, bytes memory response, bytes memory err) internal {
        if (err.length > 0) {
            revert("Allocation optimization failed");
        }

        uint256[] memory allocations = abi.decode(response, (uint256[]));
        latestAllocations[requestId] = allocations;

        emit AllocationOptimized(requestId, allocations);
    }

    /**
     * @dev Callback function for oracle health check
     */
    function _fulfillOracleHealthCheck(bytes32 requestId, bytes memory response, bytes memory err) internal {
        if (err.length > 0) {
            revert("Oracle health check failed");
        }

        bool isHealthy = abi.decode(response, (bool));
        latestOracleHealth[requestId] = isHealthy;

        emit OracleHealthChecked(requestId, isHealthy);
    }

    /**
     * @dev Override the _handleOracleFulfillment function
     */
    function _handleOracleFulfillment(
        bytes32 requestId,
        bytes memory response,
        bytes memory err
    ) internal override {
        // Route to appropriate fulfillment function based on request type
        // This is a simplified example - you'd want to track request types
        _fulfillStrategyRiskScoring(requestId, response, err);
    }

    /**
     * @dev Withdraw LINK tokens (emergency function)
     */
    function withdrawLink() external onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(chainlinkTokenAddress());
        require(link.transfer(msg.sender, link.balanceOf(address(this))), "Unable to transfer");
    }
} 