FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install system dependencies including build tools
RUN apk add --no-cache \
    python3 \
    py3-pip \
    git \
    bash \
    make \
    g++

# Copy package files
COPY src/serverless/functions/package*.json ./functions/

# Install Node.js dependencies
WORKDIR /app/functions
RUN npm install

# Copy the rest of the application
WORKDIR /app
COPY . .

# Create a test script
RUN echo '#!/bin/bash' > /app/test_functions.sh && \
    echo 'echo "🚀 Testing Chainlink Functions in Docker"' >> /app/test_functions.sh && \
    echo 'echo "====================================="' >> /app/test_functions.sh && \
    echo 'cd /app/functions' >> /app/test_functions.sh && \
    echo 'echo "Testing strategy_risk_scoring.js..."' >> /app/test_functions.sh && \
    echo 'node -e "const { execute } = require(\"./strategy_risk_scoring.js\"); execute([\"0x1234567890123456789012345678901234567890\", \"[\\\"USDC\\\", \\\"WETH\\\"]\", \"0.3\", \"0.4\", \"0.25\"]).then(result => { console.log(\"✅ Test successful!\"); console.log(\"Result:\", result); }).catch(error => { console.error(\"❌ Test failed:\", error.message); });"' >> /app/test_functions.sh && \
    echo 'echo ""' >> /app/test_functions.sh && \
    echo 'echo "🎉 Ready to run Chainlink Functions!"' >> /app/test_functions.sh && \
    echo 'echo "To test other functions, run:"' >> /app/test_functions.sh && \
    echo 'echo "  node -e \"const { execute } = require(\"./cross_chain_apy.js\"); execute([...]).then(console.log);\""' >> /app/test_functions.sh && \
    chmod +x /app/test_functions.sh

# Set default command
CMD ["/app/test_functions.sh"] 