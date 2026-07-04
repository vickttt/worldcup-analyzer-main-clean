def build_model_methodology():
    return {
        "version": "lite_model_methodology_v1",
        "disclaimer": (
            "Model Methodology Transparency Layer 只解释 Lite v1 计算方法；"
            "不参与 TPB、Market、Scenario、Portfolio、Ranking、Stake 或 Execution 的任何计算。"
        ),
        "system_definition": {
            "identity": "Lite Explainable Betting Decision System v1",
            "not": [
                "prediction model",
                "EV/ROI optimizer",
                "profit maximization engine",
                "black-box heuristic stack",
            ],
            "does": [
                "TPB probability anchoring",
                "three-metric market structure summary",
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
            "market_agreement": {
                "name": "Market Agreement",
                "inputs": ["bookmaker dispersion", "available market depth"],
                "logic": "Higher agreement means lower bookmaker dispersion and sufficient market depth.",
            },
            "market_conflict_index": {
                "name": "Market Conflict",
                "inputs": ["Market Agreement Score"],
                "logic": "Market Conflict = 100 - Market Agreement Score in the active Lite model. The legacy conflict function is deprecated and not used.",
            },
            "volatility_pressure": {
                "name": "Volatility Pressure",
                "inputs": ["draw probability", "market disagreement", "correct-score tail density"],
                "logic": "Draw pressure, disagreement, and tail density are compressed into Low / Medium / High pressure.",
            },
        },
        "signal_strength": {
            "formula": "SS = (max(TPB probabilities) - second max(TPB probabilities)) * 100",
            "role": "primary signal strength display and ranking input",
        },
        "investment_score": {
            "formula": "Investment Score = Signal × Risk Adjustment",
            "signal": "Signal = TPB Edge + Scenario Alignment",
            "risk": "Risk Adjustment is derived from RSI Low / Medium / High. RSI does not enter the stake mapping function directly; it indirectly influences stake through Investment Score.",
        },
        "scenario_projection": {
            "name": "Scenario Projection Layer",
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
            "formula": "RSI = qualitative max(Market disagreement, Scenario dispersion, Tail density)",
            "outputs": ["Low", "Medium", "High"],
            "role": "RSI is a risk adjustment factor. It affects Investment Score through Risk Adjustment and therefore can indirectly affect stake.",
            "not": ["100-point RSS", "EV input", "ROI input", "direct stake mapping input"],
        },
        "coverage_quality_score": {
            "name": "Coverage Quality Score (CQS)",
            "formula": "CQS = coverage completeness - redundancy",
            "role": "portfolio coverage quality display only; not ranking score",
        },
        "ranking": {
            "name": "Ranking Score",
            "formula": "Ranking Score = SS + Scenario Alignment - RSI",
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
            "role": "high variance structural signal layer, not execution signal",
            "boundaries": [
                "does not enter Investment Score",
                "does not enter Ranking Score",
                "does not enter stake mapping",
            ],
        },
        "semantic_alignment": {
            "TPB": "probability anchor",
            "Scenario": "bounded structural weighting layer",
            "Portfolio": "coverage layer",
            "Ranking": "ordering layer, not final execution instruction",
            "RSI": "risk adjustment factor that indirectly influences stake through Investment Score",
            "Stake": "final execution mapping from Investment Score only",
            "Market Conflict": "inverse of Market Agreement Score in the active Lite model; legacy conflict function is deprecated and not used",
            "Correct Score": "high variance structural signal layer, not execution signal",
        },
        "audit_guards": [
            "No hidden ranking weights",
            "No EV/ROI transformation",
            "No portfolio score feeding ranking",
            "No correct-score signal feeding ranking score",
            "No user input influence",
        ],
    }
