const { Functions } = require("@chainlink/functions-toolkit");

const execute = async (args) => {
  try {
    // Parse input arguments
    const strategyAddress = args[0];
    const tokens = JSON.parse(args[1]);
    const currentAllocation = parseFloat(args[2]);
    const maxAllocation = parseFloat(args[3]);
    const baseRiskScore = parseFloat(args[4]);
    
    // Validate inputs
    if (!strategyAddress || !tokens || isNaN(currentAllocation) || isNaN(maxAllocation) || isNaN(baseRiskScore)) {
      throw new Error("Invalid input parameters");
    }
    
    // Calculate risk factors
    const allocationRisk = Math.min(currentAllocation / maxAllocation, 1.0);
    const tokenDiversityRisk = Math.max(0, 1.0 - (tokens.length / 10.0)); // More tokens = lower risk
    
    // Weighted risk calculation
    const finalRiskScore = Math.min(
      (baseRiskScore * 0.6) + (allocationRisk * 0.3) + (tokenDiversityRisk * 0.1),
      1.0
    );
    
    // Generate verification hash
    const verificationData = {
      strategyAddress,
      tokens: tokens.sort(), // Sort for consistent hashing
      currentAllocation,
      maxAllocation,
      baseRiskScore,
      finalRiskScore,
      timestamp: Date.now()
    };
    
    const verificationHash = Functions.encodeString(
      JSON.stringify(verificationData, Object.keys(verificationData).sort())
    );
    
    // Prepare result
    const result = {
      strategy_address: strategyAddress,
      risk_score: finalRiskScore,
      risk_factors: {
        base_risk: baseRiskScore,
        allocation_risk: allocationRisk,
        diversity_risk: tokenDiversityRisk
      },
      timestamp: Date.now(),
      verification_hash: verificationHash
    };
    
    return Functions.encodeString(JSON.stringify(result));
    
  } catch (error) {
    console.error("Error in strategy risk scoring:", error);
    throw new Error(`Strategy risk scoring failed: ${error.message}`);
  }
};

module.exports = { execute }; 