import joblib
import json

# Load model
model = joblib.load("ml/model.pkl")

# Score a sample strategy
def score_strategy(strategy_json):
    features = extract_features_from_strategy(strategy_json)
    score = model.predict_proba([features])[0][1]  # e.g. probability of low risk
    return score

# Mocked extractor (replace with real feature mapping)
def extract_features_from_strategy(strategy):
    return [
        strategy['allocations']['strategy_1'],
        strategy['allocations']['strategy_2'],
        strategy['allocations']['strategy_3'],
        strategy['expected_yield'],
        strategy['risk_level'] == 'low',
        strategy['oracle_health_score'],
        strategy['vault_tvl_ratio']
    ]
