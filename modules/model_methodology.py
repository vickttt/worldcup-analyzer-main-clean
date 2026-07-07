def build_model_methodology():
    return {
        "version": "lite_model_methodology_v1",
        "disclaimer": (
            "Model Methodology Transparency Layer 只解释 Lite v1 计算方法；"
            "不参与 TPB、Market、Scenario、Portfolio、Ranking、Stake 或 Execution 的任何计算。"
        ),
        "system_definition": {
            "identity": "Lite Explainable Betting Decision System v2",
            "not": [
                "prediction model",
                "EV/ROI optimizer",
                "profit maximization engine",
                "black-box heuristic stack",
            ],
            "does": [
                "TPB probability anchoring",
                "three core market-structure metrics plus tail-probability display comparison",
                "scenario projection",
                "two-factor investment scoring",
                "single ranking score",
            ],
        },
        "tpb_definition": {
            "role": "probability anchor with p_home, p_draw, p_away",
            "not": [
                "entropy confidence engine",
                "ranking override",
                "true probability claim",
            ],
        },
        "market_structure_methods": {
            "directional_strength": {
                "name": "Direction Strength",
                "inputs": ["TPB top probability", "TPB second probability"],
                "logic": "Direction Strength follows TPB concentration only: top probability minus second probability.",
            },
            "market_consistency": {
                "name": "Market Consistency Score",
                "inputs": ["1X2 dispersion", "Asian Handicap direction/depth", "Over/Under vs Correct Score", "Polymarket if available"],
                "logic": "Market Consistency Score = weighted available components: 0.15×1X2 internal consistency + 0.25×1X2/AH direction + 0.20×AH depth/TPB + 0.25×OU/Correct Score + 0.15×Polymarket/API. Missing components are skipped and weights renormalized.",
            },
            "market_disagreement": {
                "name": "Market Disagreement",
                "inputs": ["Market Consistency Score"],
                "logic": "Market Disagreement = 100 - Market Consistency Score.",
            },
            "score_path_uncertainty": {
                "name": "Score Path Uncertainty",
                "inputs": ["draw probability", "Over/Under vs Correct Score consistency"],
                "logic": "Score Path Uncertainty = 0.60×draw stalemate pressure + 0.40×OU/Correct Score structure tension. True Tail Probability is not a direct input.",
            },
            "true_tail_probability": {
                "name": "True Tail Probability",
                "inputs": ["deduped Correct Score implied probabilities"],
                "logic": "True Tail Probability is normalized implied probability mass for upset, high-score draw, total goals >= 5, or extreme favorite-margin score paths. It is not row density.",
            },
        },
        "signal_strength": {
            "formula": "SS = (max(TPB probabilities) - second max(TPB probabilities)) * 100",
            "role": "primary signal strength display and ranking input",
        },
        "investment_score": {
            "formula": "Investment Score = Base Signal × Risk Adjustment",
            "signal": "Base Signal = max(TPB Edge, Main Path Support) + 0.35×min(TPB Edge, Main Path Support)",
            "risk": "Risk Adjustment = clamp(0.95 - 0.45×RSI Score/100, 0.50, 0.95). Stake mapping still reads only Investment Score.",
        },
        "scenario_projection": {
            "name": "情景概率投影层",
            "principle": "Scenario = bounded structural weighting layer from TPB + Market signal projection.",
            "role": "Scenario weights are used for portfolio construction, ranking adjustment, and risk estimation.",
            "constraints": [
                "fixed S1-S6 taxonomy",
                "one projection pass",
                "no v1/v2 double normalization",
                "no EV/ROI",
                "no ML training",
            ],
        },
        "risk_surface_index": {
            "name": "Risk Surface Index (RSI)",
            "formula": "RSI Score = 0.30×Market Disagreement + 0.25×Score Path Uncertainty + 0.25×True Tail Probability Risk + 0.20×Scenario Structure Risk",
            "outputs": ["score 0-100", "Low", "Medium", "High"],
            "role": "RSI is a structural risk index. True Tail Probability Risk enters RSI, and RSI can indirectly affect stake only through Investment Score via the continuous Risk Adjustment factor.",
            "not": ["100-point RSS", "EV input", "ROI input", "direct stake mapping input"],
        },
        "coverage_quality_score": {
            "name": "Coverage Quality Score (CQS)",
            "formula": "CQS = coverage completeness - redundancy",
            "role": "portfolio coverage quality display only; not ranking score",
        },
        "ranking": {
            "name": "Ranking Score",
            "formula": "Ranking Score = 0.60×SS + 0.40×path support; RSI is a displayed risk label and no longer a ranking penalty.",
            "outputs": "Top 3 ordered structure only",
            "role": "Ranking orders betting structures; it is not a final execution instruction. Final execution still depends on the stake decision layer.",
            "forbidden_inputs": [
                "Portfolio coverage score",
                "Correct Score tail signal",
                "user odds",
                "execution layer",
                "EV / ROI",
            ],
        },
        "correct_score": {
            "name": "Correct Score",
            "role": "Correct Score generates True Tail Probability and Score Extension Probability; it is not an execution signal.",
            "boundaries": [
                "True Tail Probability enters RSI through True Tail Probability Risk; Correct Score does not directly enter Investment Score",
                "does not enter Ranking Score",
                "does not enter stake mapping",
            ],
        },
        "semantic_alignment": {
            "TPB": "probability anchor",
            "Scenario": "bounded structural weighting layer",
            "Portfolio": "coverage layer",
            "Ranking": "ordering layer, not final execution instruction",
            "RSI": "weighted structural risk index that indirectly influences stake through Investment Score",
            "Stake": "final execution mapping from Investment Score only",
            "Market Disagreement": "100 - Market Consistency Score",
            "Correct Score": "source for true tail probability and score extension probability, not an execution signal",
        },
        "audit_guards": [
            "No hidden ranking weights",
            "No EV/ROI transformation",
            "No portfolio score feeding ranking",
            "No correct-score signal feeding ranking score",
            "No user input influence",
        ],
    }
