# Experiment 10 — Scheduling and Tracking: PERT, CPM, and EVA

## PERT network and schedule baseline

Use the expected-duration formula `TE = (O + 4M + P) / 6`. Values below are candidate calendar weeks and planning assumptions. Actual start/end dates and resource assignments must be filled from the team's approved semester calendar.

| ID | Activity | Predecessor | O (weeks) | M (weeks) | P (weeks) | TE (weeks) |
|---|---|---|---:|---:|---:|---:|
| A | Adopt project and confirm scope | — | 0.5 | 1 | 1.5 | 1 |
| B | Complete approved field interviews/observation | A | 1 | 2 | 3 | 2 |
| C | Baseline requirements and SRS | B | 1 | 2 | 3 | 2 |
| D | DFD, data dictionary and UML design | C | 1 | 2 | 3 | 2 |
| E | Database, role and authentication foundation | D | 1 | 2 | 3 | 2 |
| F | Student menu, cart and order workflow | E | 2 | 3 | 4 | 3 |
| G | Staff queue and dashboard | E | 1 | 2 | 3 | 2 |
| H | Integrate student and staff workflows | F, G | 1 | 2 | 3 | 2 |
| I | System testing and defect fixes | H | 1 | 2 | 3 | 2 |
| J | Stakeholder acceptance and final corrections | I | 0.5 | 1 | 1.5 | 1 |
| K | Demo, viva and handover record | J | 0.5 | 1 | 1.5 | 1 |

The critical path is `A → B → C → D → E → F → H → I → J → K`, totaling **18 weeks**. Path through G is 17 weeks and has about one week of schedule float before H. Keep two weeks of management reserve in a proposed **20-week** baseline. On the critical path, PERT variance is the sum of `(P − O)^2 / 36`; standard deviation is approximately `0.93 weeks`. This is a planning approximation, not a confidence guarantee.

## Milestone and tracking sheet

| Planned week | Milestone | Planned date | Actual date | Evidence / variance reason |
|---:|---|---|---|---|
| 1 | Charter and team working agreement | `[date]` | `[date]` | `[minutes/board]` |
| 3 | Fieldwork and SRS review | `[date]` | `[date]` | `[consented notes/review]` |
| 7 | Design baseline and data model | `[date]` | `[date]` | `[diagram revision]` |
| 12 | Student ordering increment | `[date]` | `[date]` | `[demo/build identifier]` |
| 15 | Staff/admin increment integrated | `[date]` | `[date]` | `[demo/build identifier]` |
| 18 | Test and acceptance exit | `[date]` | `[date]` | `[actual test/UAT record]` |
| 20 | Demo, viva and handover | `[date]` | `[date]` | `[faculty completion]` |

Update planned value (PV), earned value (EV), and actual cost (AC) weekly using the same person-day basis. Attach dated board exports or meeting notes; do not backfill assumed progress as actual.

## Worked EVA example (illustrative only)

No actual project tracking log was supplied. The values below are a clearly labeled arithmetic example, not team performance data.

Assume Budget at Completion (BAC) = 100 person-days. At an illustrative week-10 checkpoint, PV = 50 person-days, EV = 45 person-days, and AC = 55 person-days.

- Schedule variance: `SV = EV − PV = 45 − 50 = −5 person-days`
- Cost variance: `CV = EV − AC = 45 − 55 = −10 person-days`
- Schedule performance index: `SPI = EV / PV = 45 / 50 = 0.90`
- Cost performance index: `CPI = EV / AC = 45 / 55 = 0.82`
- Estimate at completion using current CPI: `EAC = BAC / CPI ≈ 100 / 0.82 = 122 person-days`
- Estimate to complete: `ETC = EAC − AC = 122 − 55 = 67 person-days`
- Variance at completion: `VAC = BAC − EAC = 100 − 122 = −22 person-days`

Interpretation: in this example, completed-value progress trails plan and cost efficiency is below 1.0. Investigate scope churn, rework, and integration delay; agree corrective action with the instructor or product representative. Replace all three inputs with the team's actual weekly data before using EVA as a status report.
