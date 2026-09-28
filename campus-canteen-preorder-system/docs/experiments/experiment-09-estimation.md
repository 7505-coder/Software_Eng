# Experiment 9 — Estimation: Function Points and COCOMO

## Function point estimate

This is a planning estimate for the defined prototype scope. Counts and complexity ratings must be revisited after real fieldwork and instructor review; they are not measured user-function counts.

| Function type | Count | Assumed complexity | Standard weight | Subtotal |
|---|---:|---|---:|---:|
| External Inputs (EI) | 7 | Average | 4 | 28 |
| External Outputs (EO) | 6 | Average | 5 | 30 |
| External Inquiries (EQ) | 4 | Low | 3 | 12 |
| Internal Logical Files (ILF) | 5 | Low | 7 | 35 |
| External Interface Files (EIF) | 1 | Low | 5 | 5 |
| **Unadjusted Function Points (UFP)** |  |  |  | **110** |

Assume 14 total points across the 14 General System Characteristics (each rated 0–5). The Value Adjustment Factor is `0.65 + (0.01 × 14) = 0.79`. Adjusted estimate: `110 × 0.79 = 86.9 ≈ 87 function points`.

For an early sizing conversion only, assume 22 delivered source lines per adjusted function point for the mixed Python/HTML/CSS/JavaScript implementation: `86.9 × 22 = 1,912 LOC ≈ 1.9 KLOC`. LOC-per-function-point varies by language, style, and generated code, so this is a rough sizing cross-check rather than a promise.

## Basic COCOMO estimate

Treat the prototype as an **organic, small software project** and use the basic COCOMO constants as a classroom model:

- Size: `2.0 KLOC` (rounded from the function-point sizing cross-check)
- Effort: `2.4 × KLOC^1.05 = 2.4 × 2.0^1.05 ≈ 4.98 person-months`
- Development time: `2.5 × Effort^0.38 = 2.5 × 4.98^0.38 ≈ 4.60 months`
- Average staffing: `Effort ÷ Development time = 4.98 ÷ 4.60 ≈ 1.08 full-time equivalents`

For a five-person student team, 1.08 FTE corresponds to roughly 22% average availability per member across 4.6 calendar months. This is a theoretical average, not a claim about the team's actual time. The estimate excludes production integrations, online payment, external notification services, and security certification.

## Sensitivity and risk

If final scope grows by 25%, size rises to 2.5 KLOC. The basic organic model then estimates `2.4 × 2.5^1.05 ≈ 6.17 PM` and `2.5 × 6.17^0.38 ≈ 4.98 months`. The largest uncertainty is not arithmetic; it is unvalidated queue, pickup, and stock policy. Re-estimate when Experiment 4 field evidence and the instructor-approved scope are available.
