const { Functions } = require("@chainlink/functions-toolkit");

const execute = async (args) => {
  try {
    // Parse input arguments
    const oracleAddresses = JSON.parse(args[0]);
    const timestamp = parseInt(args[1]);
    const deviationThreshold = parseFloat(args[2]);
    
    // Validate inputs
    if (!Array.isArray(oracleAddresses) || isNaN(timestamp) || isNaN(deviationThreshold)) {
      throw new Error("Invalid input parameters");
    }
    
    const oracleStatus = {};
    
    // Check health of each oracle
    for (const oracle of oracleAddresses) {
      try {
        // In production, this would query the actual Chainlink oracle contracts
        // For now, we'll simulate the health check
        
        // Simulate price deviation check (0-1% deviation)
        const deviation = Math.random() * 0.01; // 0-1% random deviation
        
        // Simulate last update time (within 5 minutes)
        const lastUpdate = timestamp - Math.floor(Math.random() * 300);
        
        // Simulate confidence level (95-100%)
        const confidence = 0.95 + (Math.random() * 0.05);
        
        oracleStatus[oracle] = {
          healthy: deviation < deviationThreshold,
          deviation: deviation,
          last_update: lastUpdate,
          confidence: confidence,
          price: 1000 + (Math.random() * 100), // Simulated price
          heartbeat: true // Simulated heartbeat
        };
        
      } catch (error) {
        console.warn(`Failed to check oracle ${oracle}:`, error.message);
        oracleStatus[oracle] = {
          healthy: false,
          deviation: 1.0, // Max deviation
          last_update: timestamp,
          confidence: 0.0,
          error: error.message
        };
      }
    }
    
    // Calculate overall health metrics
    const healthyOracles = Object.values(oracleStatus).filter(status => status.healthy);
    const overallHealth = healthyOracles.length === oracleAddresses.length;
    const averageDeviation = Object.values(oracleStatus)
      .reduce((sum, status) => sum + (status.deviation || 0), 0) / oracleAddresses.length;
    
    // Generate verification hash
    const verificationData = {
      oracleAddresses: oracleAddresses.sort(),
      timestamp,
      deviationThreshold,
      oracleStatus,
      overallHealth,
      averageDeviation
    };
    
    const verificationHash = Functions.encodeString(
      JSON.stringify(verificationData, Object.keys(verificationData).sort())
    );
    
    // Prepare result
    const result = {
      oracle_status: oracleStatus,
      overall_health: overallHealth,
      average_deviation: averageDeviation,
      healthy_count: healthyOracles.length,
      total_count: oracleAddresses.length,
      timestamp: timestamp,
      verification_hash: verificationHash
    };
    
    return Functions.encodeString(JSON.stringify(result));
    
  } catch (error) {
    console.error("Error in oracle health check:", error);
    throw new Error(`Oracle health check failed: ${error.message}`);
  }
};

module.exports = { execute }; 