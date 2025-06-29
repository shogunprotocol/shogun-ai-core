const { Functions } = require("@chainlink/functions-toolkit");

const execute = async (args) => {
  try {
    // Parse input arguments
    const currentAllocations = JSON.parse(args[0]);
    const constraints = JSON.parse(args[1]);
    const tvl = parseFloat(args[2]);
    const riskTolerance = parseFloat(args[3]);
    
    // Validate inputs
    if (!currentAllocations || !constraints || isNaN(tvl) || isNaN(riskTolerance)) {
      throw new Error("Invalid input parameters");
    }
    
    // Simple optimization algorithm
    const strategies = Object.keys(constraints);
    const optimalAllocations = {};
    
    // Calculate total available allocation
    let totalAllocated = 0;
    for (const strategy of strategies) {
      const maxAlloc = constraints[strategy].max_allocation || 0.4;
      const riskScore = constraints[strategy].risk_score || 0.3;
      
      // Adjust allocation based on risk tolerance and constraints
      const optimalAlloc = Math.min(
        maxAlloc * (1 - riskScore * riskTolerance),
        maxAlloc
      );
      
      optimalAllocations[strategy] = optimalAlloc;
      totalAllocated += optimalAlloc;
    }
    
    // Normalize allocations to sum to 1.0
    if (totalAllocated > 0) {
      for (const strategy of strategies) {
        optimalAllocations[strategy] = optimalAllocations[strategy] / totalAllocated;
      }
    }
    
    // Calculate expected performance metrics
    let expectedReturn = 0;
    let portfolioRiskScore = 0;
    
    for (const strategy of strategies) {
      const allocation = optimalAllocations[strategy];
      const riskScore = constraints[strategy].risk_score || 0.3;
      const expectedApy = constraints[strategy].expected_apy || 0.08; // 8% default
      
      expectedReturn += allocation * expectedApy;
      portfolioRiskScore += allocation * riskScore;
    }
    
    // Generate verification hash
    const verificationData = {
      currentAllocations,
      constraints,
      tvl,
      riskTolerance,
      optimalAllocations,
      expectedReturn,
      portfolioRiskScore,
      timestamp: Date.now()
    };
    
    const verificationHash = Functions.encodeString(
      JSON.stringify(verificationData, Object.keys(verificationData).sort())
    );
    
    // Prepare result
    const result = {
      optimal_allocations: optimalAllocations,
      expected_return: expectedReturn,
      risk_score: portfolioRiskScore,
      total_value_locked: tvl,
      timestamp: Date.now(),
      verification_hash: verificationHash
    };
    
    return Functions.encodeString(JSON.stringify(result));
    
  } catch (error) {
    console.error("Error in allocation optimization:", error);
    throw new Error(`Allocation optimization failed: ${error.message}`);
  }
};

module.exports = { execute }; 