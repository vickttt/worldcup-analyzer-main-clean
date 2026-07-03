def build_model_methodology():
    return {
        "version": "model_methodology_transparency_v2",
        "disclaimer": (
            "Model Methodology Transparency Layer 只解释计算方法，不参与 TPB、Market Structure、"
            "Scenario、Portfolio、Ranking、Stake 或 Execution 的任何计算。"
        ),
        "system_definition": {
            "identity": "Market Structure + Scenario-Weighted Bounded Optimization + Probability Anchor System",
            "not": [
                "prediction model",
                "optimal odds finder",
                "profit maximization engine",
                "EV/ROI optimizer",
            ],
            "does": [
                "market structure inference",
                "scenario coverage space construction",
                "bounded scenario weighting",
                "risk-coverage balance synthesis",
            ],
        },
        "tpb_definition": {
            "role": "probability normalization anchor and coordinate system",
            "not": [
                "predictive model",
                "decision engine",
                "true probability claim",
            ],
        },
        "odds_definition": {
            "odds_are": "market pricing with bookmaker bias and noisy signal",
            "odds_are_not": "true probability",
        },
        "ev_roi_boundary": {
            "excluded_reason": (
                "EV/ROI depend on an assumed true probability. This system does not assume "
                "true probability exists outside quoted market structure."
            ),
            "system_method": "market structure inference, not value-betting optimization",
        },
        "optimizer_boundary": {
            "allowed": [
                "bounded heuristic coverage optimization",
                "scenario weighting",
                "scenario balancing",
                "risk exposure smoothing",
            ],
            "forbidden": [
                "EV optimizer",
                "ROI optimizer",
                "profit maximization engine",
                "ML training system",
                "black-box scoring system",
            ],
        },
        "market_structure_methods": {
            "directional_strength": {
                "name": "Directional Strength",
                "inputs": [
                    "TPB probability concentration",
                    "Asian Handicap alignment with 1X2 direction",
                    "odds convergence / market consistency",
                ],
                "logic": (
                    "先读取 TPB 最高方向与第二方向的差距，再观察亚洲让球是否支持同一方向，"
                    "并参考大小球是否支持相同比赛节奏。方向差距和盘口一致性越强，方向强度越高。"
                ),
                "thresholds": {
                    "Strong Direction": "direction score >= 35",
                    "Medium Direction": "18 <= direction score < 35",
                    "Weak Direction": "direction score < 18",
                },
            },
            "market_conflict_index": {
                "name": "Market Conflict Index",
                "inputs": [
                    "1X2 vs Asian Handicap deviation",
                    "Asian Handicap vs Over/Under tempo mismatch",
                    "multi-market disagreement",
                    "Correct Score tail density",
                ],
                "logic": (
                    "以平局概率、热门差距不足、盘口缺失/冲突、低总进球与强热门不一致、"
                    "以及波胆尾部分布作为冲突来源，映射到 0-100。"
                ),
                "thresholds": {
                    "Low conflict": "0-30",
                    "Medium conflict": "30-70",
                    "High conflict": "70-100",
                },
            },
            "efficiency_score": {
                "name": "Market Efficiency Score",
                "inputs": [
                    "TPB bookmaker dispersion",
                    "bookmaker market depth",
                    "Asian Handicap / Over-Under consistency",
                    "Correct Score long-tail distribution",
                ],
                "logic": (
                    "盘口越深、博彩公司分歧越低、尾部赔率越少，效率分越高；"
                    "分歧和长尾越多，说明市场定价越不稳定。"
                ),
            },
            "volatility_index": {
                "name": "Volatility Index",
                "inputs": [
                    "draw probability",
                    "market disagreement",
                    "odds variance / conflict index",
                    "Correct Score tail density",
                ],
                "logic": (
                    "平局概率、冲突指数、波胆尾部越高，比赛结构波动越高。"
                    "输出 Low / Medium / High。"
                ),
            },
        },
        "scenario_probability_derivation": {
            "name": "Scenario Probability Derivation Method",
            "principle": "Scenario probability is a structural projection, not a score prediction.",
            "inputs": [
                "TPB baseline anchor",
                "Market Structure weighting signals",
                "fixed S1-S6 scenario taxonomy",
            ],
            "logic": (
                "TPB 提供基础概率重心；Market Structure 提供冲突、效率、波动、爆冷和尾部密度权重；"
                "Scenario Engine 将这些结构信号投影到固定的 S1-S6 概率空间。"
            ),
            "forbidden": [
                "No exact score prediction",
                "No EV / ROI transformation",
                "No profit optimizer",
                "No ML training",
                "No black-box optimizer",
                "No user input",
            ],
        },
        "scenario_weighting_method_v2": {
            "name": "Scenario Weighting Function v2",
            "principle": "Scenario weights are normalized bounded heuristic signals, not learned probabilities.",
            "formula": "w(Si) = f(TPB baseline, Market Structure, Volatility, Upset Probability)",
            "constraints": [
                "weights are normalized",
                "weights are explainable",
                "weights are deterministic",
                "weights do not override TPB",
                "weights do not use user input",
            ],
            "forbidden": [
                "No EV / ROI optimization",
                "No profit maximization",
                "No ML training",
                "No black-box learned weights",
            ],
        },
        "scenario_mapping_method": {
            "name": "Scenario Mapping Method",
            "logic": (
                "S1-S6 来自 TPB strength distribution、market bias、volatility clustering 和 tail density。"
                "taxonomy 固定，不按比赛动态新增类型。"
            ),
            "taxonomy": {
                "S1": "Strong Favorite Win",
                "S2": "Narrow Favorite Win",
                "S3": "Draw",
                "S4": "Upset Win",
                "S5": "Low Scoring Match",
                "S6": "High Variance Match",
            },
        },
        "coverage_mapping_logic": {
            "name": "Coverage Mapping Logic",
            "primary_coverage": "High TPB alignment scenarios become the primary coverage path.",
            "defensive_coverage": "Draw, volatility, low scoring, or upset protection become defensive coverage.",
            "tail_coverage": "Upset and long-tail/high-variance scenarios become tail optionality.",
            "coverage_efficiency_score": (
                "Coverage Efficiency Score combines coverage completeness, risk concentration, and redundancy. "
                "It is a transparency score, not EV, ROI, profit optimization, or stake input."
            ),
            "coverage_efficiency_score_v2": (
                "Coverage Efficiency v2 = scenario coverage / (risk exposure + redundancy). "
                "It is a bounded heuristic coverage score for scenario-weighted portfolio synthesis."
            ),
        },
        "coverage_optimization_v2": {
            "name": "Coverage Optimization Engine v2",
            "objective": {
                "maximize": [
                    "scenario coverage",
                    "probability alignment",
                    "risk balance",
                ],
                "minimize": [
                    "tail exposure",
                    "conflict exposure",
                    "redundancy",
                ],
            },
            "type": "bounded deterministic heuristic",
            "forbidden": [
                "EV optimization",
                "ROI optimization",
                "profit maximization",
                "ML training or learning systems",
                "black-box optimization",
                "user input influence",
            ],
        },
        "scenario_weighted_ranking_v2": {
            "name": "Scenario-weighted Ranking v2",
            "allowed_inputs": [
                "TPB baseline",
                "Market Structure signals",
                "normalized Scenario Weights",
            ],
            "forbidden_inputs": [
                "user odds",
                "customer execution layer",
                "EV / ROI",
                "profit optimizer",
                "black-box optimizer",
            ],
        },
        "audit_guards": [
            "No black-box scoring",
            "No hidden ranking weights",
            "No implicit EV logic",
            "No EV/ROI/profit optimizer reasoning",
            "No ML training behavior",
            "All scenario mappings must be traceable",
            "All ranking basis text must be explainable",
        ],
    }
