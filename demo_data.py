"""
Demo financial scenario documents for the Digital Junior Analyst.
These are embedded directly in Python so the app works immediately
without requiring external file uploads.
"""

DEMO_DOCUMENTS = [
    {
        "title": "ACME Corp — Q3 2024 Earnings Report",
        "source": "ACME_Q3_2024_Earnings.pdf",
        "content": """
ACME CORPORATION
Q3 2024 EARNINGS REPORT — RISK DISCLOSURE SUPPLEMENT
FOR THE QUARTER ENDED SEPTEMBER 30, 2024

EXECUTIVE SUMMARY
ACME Corporation reported Q3 2024 revenue of $4.2 billion, representing a 7.3% year-over-year decline
compared to $4.53 billion in Q3 2023. Net income contracted sharply to $312 million (EPS: $1.04),
down from $578 million (EPS: $1.89) in the prior year period. EBITDA margin compressed to 18.2%
from 24.7%, reflecting persistent cost inflation and demand softness in the enterprise software segment.

KEY FINANCIAL METRICS
- Revenue: $4.2B (vs $4.53B prior year; -7.3% YoY)
- Net Income: $312M (vs $578M prior year; -46.0% YoY)
- EPS (diluted): $1.04 (vs $1.89 prior year)
- EBITDA: $764M (margin: 18.2%)
- Free Cash Flow: $198M (vs $441M prior year; -55.1% YoY)
- Gross Margin: 52.1% (vs 58.4% prior year)
- Net Debt: $3.1B (leverage ratio: 4.06x EBITDA)
- Interest Coverage Ratio: 2.8x (below investment grade threshold of 3.0x)

RISK FACTORS

1. LIQUIDITY RISK — HIGH SEVERITY
ACME's cash and equivalents stand at $620M against $1.1B in short-term debt obligations due within
12 months. The current ratio has declined to 0.87 (below the critical 1.0 threshold), indicating a
potential near-term liquidity shortfall. The company drew down $400M of its $750M revolving credit
facility in September 2024, leaving limited headroom. Management is in active negotiations with
lenders to extend the maturity of the revolving credit facility by 18 months. Failure to secure
refinancing terms by Q1 2025 represents a material risk to operational continuity.

2. LEVERAGE RISK — HIGH SEVERITY
Net leverage of 4.06x EBITDA significantly exceeds ACME's stated target of 2.5x and the covenant
threshold of 4.5x embedded in its senior secured notes. Continued EBITDA erosion could trigger a
covenant breach as early as Q2 2025 if current trends persist. A covenant breach would accelerate
the maturity of $2.3B in senior secured notes, creating a potential default scenario.

3. MARKET RISK — MEDIUM SEVERITY
Enterprise software demand has softened considerably as customers delay discretionary IT spending.
ACME's largest vertical (financial services, 34% of revenue) is undergoing its own margin compression
cycle, resulting in contract renegotiations that reduced average contract value by 12% in Q3 2024.
Management has revised full-year revenue guidance downward to $16.8B-$17.0B (from $18.2B).

4. OPERATIONAL RISK — MEDIUM SEVERITY
ACME is executing a cost restructuring program targeting $350M in annualized savings. The program
includes a workforce reduction of approximately 4,200 employees (8% of global headcount) and
consolidation of 14 office locations. One-time charges of $185M were recorded in Q3 2024.
Execution risk is elevated given the scale of the restructuring and the concurrent strategic pivot
toward AI-integrated product offerings.

5. REGULATORY & COMPLIANCE RISK — LOW SEVERITY
ACME is subject to ongoing regulatory scrutiny related to data privacy practices in the EU under GDPR.
A potential fine of up to €120M has been assessed by the Data Protection Authority of Ireland
following an audit of ACME's data processing agreements. The company is contesting the finding.

CREDIT QUALITY ASSESSMENT
Moody's downgraded ACME's senior unsecured rating from Ba2 to B1 in October 2024. S&P placed
ACME on CreditWatch Negative. The risk of a further one-notch downgrade is elevated given
the deteriorating free cash flow trajectory and high leverage. A downgrade to CCC would likely
trigger margin calls on derivatives and restrict the company's access to commercial paper markets.

FORWARD GUIDANCE
Q4 2024 Revenue: $4.1B–$4.3B
Full Year 2024 Revenue: $16.8B–$17.0B (revised down from $18.2B)
Full Year 2024 EBITDA Margin: 17%-19%
Capital Expenditure: $420M (reduced from $550M to preserve liquidity)

CONCLUSION
ACME Corporation faces a compound risk environment characterized by deteriorating financial
metrics, near-term refinancing pressures, and structural demand headwinds. While management
has initiated a credible restructuring program, execution over the next two quarters will be
critical to restoring investor confidence and stabilizing the credit profile.
        """,
    },
    {
        "title": "Global Markets — Regulatory Compliance Risk Memo",
        "source": "Regulatory_Compliance_Memo_2024.pdf",
        "content": """
INTERNAL COMPLIANCE ADVISORY MEMORANDUM
CLASSIFICATION: CONFIDENTIAL — FOR SENIOR MANAGEMENT REVIEW
DATE: OCTOBER 15, 2024
SUBJECT: Escalating Regulatory Risk in Financial Services — Q4 2024 Threat Assessment

1. EXECUTIVE SUMMARY
The global regulatory environment for financial services firms has entered a period of
heightened enforcement activity. This memorandum summarizes the key regulatory risk vectors
identified by the Compliance Risk Assessment team for Q4 2024, with recommended mitigation
actions for each.

2. ANTI-MONEY LAUNDERING (AML) COMPLIANCE RISK — CRITICAL
Regulatory enforcement actions related to AML deficiencies have reached a decade high in 2024.
The Financial Crimes Enforcement Network (FinCEN) issued $2.3B in AML-related fines across
the financial services industry in the first nine months of 2024, a 67% increase year-over-year.

Risk Indicators in Our Portfolio:
- Transaction monitoring alert backlog has grown to 14,200 unreviewed alerts (up from 8,400 in Q2 2024)
- Customer Due Diligence (CDD) refresh rate for high-risk clients stands at 61% (target: >90%)
- Three politically exposed persons (PEPs) were onboarded in Q3 2024 without enhanced due diligence (EDD) approval
- Suspicious Activity Report (SAR) filing turnaround time has deteriorated to 42 days (regulatory maximum: 30 days)

Risk Assessment: CRITICAL — Immediate remediation required. Continued non-compliance creates
material exposure to regulatory censure, monetary penalty (estimated $80M-$150M), and potential
license restrictions. Recommend escalation to Board Risk Committee within 5 business days.

3. MARKET CONDUCT AND MiFID II COMPLIANCE — HIGH SEVERITY
MiFID II best execution reporting requirements have been strengthened by the EU following a
2023 review. Key gaps identified:
- Order execution policy was last reviewed in February 2023 (requirement: annual review)
- Best execution reports for Q1 and Q2 2024 were filed 18 days past deadline
- Pre-trade transparency waivers for 23 large-in-scale trades were applied incorrectly

Regulatory Exposure: Potential fine of £4M-£8M from the FCA. Reputational risk is elevated
given recent FCA public statements on best execution enforcement priorities.

4. BASEL III / CAPITAL ADEQUACY RISK — HIGH SEVERITY
The Basel III Endgame rules (US implementation) introduce significant changes to Risk-Weighted
Asset (RWA) calculations effective Q1 2025. Preliminary internal analysis indicates:
- Common Equity Tier 1 (CET1) ratio may decline by 80-120 basis points under new RWA rules
- Current CET1 of 11.8% provides limited buffer above the 10.5% minimum requirement (GSIB surcharge included)
- Operational risk RWA is expected to increase 18-22% under the Standardised Approach

Recommended Action: Accelerate capital optimization initiatives. Consider reducing RWA in
trading book by $4B through position reduction and restructuring of counterparty exposure.

5. DATA PRIVACY & AI GOVERNANCE — MEDIUM SEVERITY
The EU AI Act entered into force in August 2024. High-risk AI system classification applies to
our automated credit decisioning model and the real-time fraud detection algorithm. Requirements:
- Human oversight mechanisms must be documented and operational by February 2025
- Technical documentation for both systems must be submitted to regulators within 90 days
- Bias and fairness testing results must be publicly disclosed on an annual basis

Current readiness: 35% of AI Act requirements addressed. Gap remediation timeline: estimated
18-22 weeks. Resource requirements: 4 FTE dedicated compliance officers + external legal counsel.

6. SANCTIONS COMPLIANCE — MEDIUM SEVERITY
OFAC has expanded sanctions programs related to Russian entities, certain Chinese technology
firms, and several new designations in the Middle East. Screening system updates for new
designations are running with a 72-hour lag (target: <24 hours). Three screening misses were
identified in Q3 2024 post-event review, none of which resulted in prohibited transactions.

7. REMEDIATION PRIORITY MATRIX

| Risk Area            | Severity  | Estimated Exposure | Remediation Deadline |
|----------------------|-----------|-------------------|----------------------|
| AML / SAR Filing     | CRITICAL  | $80M - $150M      | Immediate            |
| Basel III RWA Impact | HIGH      | CET1 -80-120bps   | Q1 2025              |
| MiFID II Execution   | HIGH      | £4M - £8M         | Q4 2024              |
| EU AI Act Readiness  | MEDIUM    | Operational Risk  | Feb 2025             |
| Sanctions Screening  | MEDIUM    | Reputational      | Q4 2024              |

8. CONCLUSION
The firm faces a compound regulatory risk environment in Q4 2024. The AML control failures
require board-level escalation and immediate remediation investment estimated at $12M-$18M.
The Basel III capital impact requires strategic portfolio adjustments beginning Q4 2024 to
ensure adequate buffer before the Q1 2025 implementation date.
        """,
    },
    {
        "title": "Global Equity Portfolio — Risk Assessment Report",
        "source": "Portfolio_Risk_Assessment_Oct2024.pdf",
        "content": """
GLOBAL EQUITY PORTFOLIO
QUANTITATIVE RISK ASSESSMENT REPORT
PERIOD: OCTOBER 2024
PREPARED BY: Quantitative Risk Analytics Team

PORTFOLIO OVERVIEW
Assets Under Management: $12.4B (as of October 1, 2024)
Benchmark: MSCI All Country World Index (ACWI)
Active Positions: 147 securities across 28 countries

PERFORMANCE SUMMARY (YTD 2024)
- Portfolio Return: +8.2% (gross of fees)
- Benchmark Return: +12.7%
- Active Return (Alpha): -4.5% (significant underperformance)
- Sharpe Ratio: 0.61 (vs benchmark 0.94)
- Information Ratio: -0.72 (negative; poor risk-adjusted active return)
- Tracking Error: 6.2% annualized (above 4.5% target)
- Maximum Drawdown (YTD): -14.3% (peak-to-trough, March 2024)
- Beta vs ACWI: 1.18 (portfolio is more volatile than benchmark)

RISK DECOMPOSITION

1. MARKET RISK — MEDIUM-HIGH SEVERITY
Value at Risk (95% confidence, 1-day): $187M (1.51% of AUM)
Value at Risk (99% confidence, 1-day): $278M (2.24% of AUM)
Expected Shortfall (CVaR, 99%): $334M
The portfolio's high beta (1.18) means it experiences amplified drawdowns during market
sell-offs. Given rising geopolitical tensions and the US election uncertainty, our macro
scenario desk projects a 25% probability of a risk-off event exceeding 10% market correction
in Q4 2024.

2. CONCENTRATION RISK — HIGH SEVERITY
Top 10 holdings constitute 41.2% of portfolio (guideline maximum: 35%)
Single-name concentration breaches:
- Holding A (Technology): 6.8% weight (limit: 5.0%) — BREACH
- Holding B (Energy): 5.4% weight (limit: 5.0%) — BREACH
- Holding C (Financials): 5.1% weight (limit: 5.0%) — BREACH

Sector concentration:
- Technology sector: 34.1% (benchmark: 23.4% — overweight 10.7%)
- Energy sector: 18.2% (benchmark: 4.8% — overweight 13.4%)
- Healthcare sector: 4.1% (benchmark: 11.2% — underweight 7.1%)

The elevated technology and energy overweights are the primary drivers of tracking error
and the principal source of the -4.5% active return shortfall.

3. FACTOR RISK — MEDIUM SEVERITY
Factor exposure analysis (Barra Multi-Factor Model):
- Momentum: +1.42 standard deviations (high positive tilt — vulnerable in momentum reversal)
- Value: -0.87 standard deviations (anti-value tilt)
- Quality: -0.23 standard deviations (slight negative quality tilt)
- Size: +0.61 standard deviations (small-cap tilt adds volatility)
- Volatility: +1.18 standard deviations (high volatility tilt — increases tail risk)

The momentum factor tilt represents the most significant factor risk. The Barra model
identifies a 68% historical probability that momentum strategies undergo sharp reversal
within 6 months of reaching the current signal strength.

4. LIQUIDITY RISK — LOW-MEDIUM SEVERITY
21.4% of portfolio positions (by value) have average daily volume (ADV) coverage > 10 days
(meaning exiting these positions would take more than 10 trading days without market impact).
4.2% of portfolio ($521M) has ADV coverage > 30 days — illiquid threshold.
In a stress scenario requiring rapid de-risking, the portfolio could experience 2-4% of
market impact costs on the illiquid portion.

5. CURRENCY RISK — LOW SEVERITY
USD exposure: 52.3% | EUR: 18.7% | GBP: 8.2% | JPY: 6.1% | Other: 14.7%
Unhedged foreign currency exposure: 47.7% of AUM
DXY strengthening of 5% would reduce portfolio value by approximately $148M based on
current currency correlations. The investment committee approved a partial FX hedge
in September 2024 reducing unhedged exposure from 58% to 47.7%.

STRESS TEST SCENARIOS

| Scenario                          | Estimated P&L Impact | Probability |
|-----------------------------------|---------------------|-------------|
| Global recession (2008-style)     | -$2.8B (-22.6%)     | 8%          |
| Tech sector correction -30%       | -$1.4B (-11.3%)     | 18%         |
| Energy price collapse -40%        | -$890M (-7.2%)      | 12%         |
| Momentum factor reversal -15%     | -$680M (-5.5%)      | 22%         |
| USD strengthens +10%              | -$296M (-2.4%)      | 30%         |

RECOMMENDATIONS
1. Immediately reduce concentration breaches in Technology, Energy holdings to within limits
2. Consider systematic momentum reduction: reduce momentum factor exposure from +1.42 to below +0.80
3. Increase healthcare allocation to reduce sector tracking error
4. Initiate partial hedging program for illiquid small-cap positions
5. Review FX hedge ratio quarterly given geopolitical uncertainty
        """,
    },
    {
        "title": "Macro Risk Outlook — Q4 2024 Scenario Analysis",
        "source": "Macro_Risk_Outlook_Q4_2024.pdf",
        "content": """
MACRO RISK OUTLOOK
Q4 2024 SCENARIO ANALYSIS AND STRATEGIC RISK ASSESSMENT
GLOBAL MARKETS RESEARCH | RISK INTELLIGENCE UNIT

1. GLOBAL MACRO OVERVIEW
The global economy enters Q4 2024 in a state of fragile equilibrium. While headline inflation
across G7 economies has moderated significantly from 2022 peaks, core services inflation
remains elevated, constraining central bank easing cycles. Real GDP growth for 2024 is
tracking at 2.8% globally (IMF estimate), masking significant dispersion across regions.

2. INTEREST RATE RISK — HIGH SEVERITY
The Federal Reserve has initiated a rate-cutting cycle with a 50bp cut in September 2024,
but the pace of easing is uncertain. Key risk: if US core inflation re-accelerates above
3.5% in Q4, the Fed may pause or reverse course. This scenario (probability: 20-25%) would
trigger a significant repricing of risk assets, with equities likely falling 10-15% and
investment grade credit spreads widening 80-120bps.

Duration risk for fixed income portfolios:
- A 100bp parallel shift upward in the yield curve would reduce investment grade bond
  values by approximately 6-8% (based on average duration of 7.2 years)
- High yield portfolios are more protected by coupon income but credit spread widening
  could offset rate benefit

Recommended actions:
- Reduce portfolio duration toward lower end of benchmark band
- Increase allocation to floating rate instruments (SOFR-linked)
- Implement rate cap structures for floating rate liability portfolios

3. GEOPOLITICAL RISK — HIGH SEVERITY
Three major geopolitical risk clusters are active simultaneously in Q4 2024:

A. Middle East Conflict Escalation
Risk of regional escalation involving Iran could disrupt Strait of Hormuz oil flows
(20% of global seaborne oil). A 6-week disruption could push Brent crude above $120/barrel.
Supply chain impacts would affect manufacturing, shipping, and consumer goods sectors.
Insurance premiums for Middle East-exposed assets have increased 340% since October 2023.

B. US-China Technology Decoupling
New US export controls on advanced semiconductors take effect Q1 2025. Companies with >15%
China revenue exposure face supply chain restructuring costs estimated at $2-8% of revenue.
Portfolio screening has identified $1.8B in holdings with elevated China revenue concentration.

C. European Political Fragmentation
French and German coalition uncertainties create fiscal policy unpredictability. Risk premium
on peripheral European sovereign debt (Italy, Spain, Greece) has widened. BTP-Bund spread
above 200bps represents a material market stress signal.

4. CREDIT MARKET RISK — MEDIUM-HIGH SEVERITY
High yield default rates are projected to rise to 4.8-5.2% in 2025 (from 3.1% in 2024).
The following sectors show the most elevated credit stress indicators:
- Commercial Real Estate (CRE): Office vacancy rates at 18.2% nationally; $900B in CRE
  debt maturities between 2024-2026 face significant refinancing risk
- Regional Banks: Exposure to CRE loans averages 28% of loan books for regional banks
  vs 8% for money center banks
- Leveraged Buyout (LBO) Debt: 67% of outstanding LBO debt issued during 2020-2022
  low-rate environment; refinancing at current rates increases interest burden by 180-220bps

5. TECHNOLOGY SECTOR RISK — MEDIUM SEVERITY
AI infrastructure investment boom shows early signs of supply-demand imbalance:
- Data center power demand is projected to grow 160% by 2027, straining grid capacity
- GPU supply constraints are easing; H100 lead times have contracted from 52 weeks to 14 weeks
- Early indicators suggest enterprise AI ROI is not yet meeting investment thesis assumptions,
  potentially reducing 2025 AI capex growth rates from projected 35% to 15-20%

6. SCENARIO PROBABILITY MATRIX

| Scenario                          | Probability | Market Impact |
|-----------------------------------|-------------|---------------|
| Soft landing (base case)          | 45%         | +5% to +8% equities |
| Re-acceleration (inflation)       | 20%         | -10% to -15% equities |
| Hard landing (recession)          | 20%         | -20% to -30% equities |
| Geopolitical shock                | 15%         | -12% to -25% equities |

7. STRATEGIC RISK RECOMMENDATIONS
1. RATE RISK: Reduce duration; increase floating rate instruments
2. GEOPOLITICAL: Hedge oil price exposure; screen China revenue concentration  
3. CREDIT: Reduce CRE exposure; avoid CCC-rated credits; increase cash buffer to 5-7%
4. EQUITIES: Reduce beta toward 1.0; increase quality factor; reduce momentum tilt
5. LIQUIDITY: Maintain minimum 60-day liquidity buffer for redemption scenarios
        """,
    },
]
