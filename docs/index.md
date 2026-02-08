# Task 1: Foundation for Brent Oil Analysis
*10 Academy Week 11 Challenge*
*Date: 2026-02-05

## 1. Data Analysis Workflow

### Step 1: Data Loading & Preparation
- Load Brent oil prices CSV (1987-2022)
- Convert Date column to datetime format
- Handle missing values with interpolation
- Check for data quality issues

### Step 2: Exploratory Data Analysis (EDA)
- Plot raw price series over time
- Calculate daily returns and log returns
- Test for stationarity using Augmented Dickey-Fuller test
- Analyze volatility patterns and clustering
- Create summary statistics

### Step 3: Event Research & Compilation
- Research historical events affecting oil prices (already done)
- 25 events compiled in CSV file
- Categorize events: Conflicts, Economic Crises, OPEC Decisions, Supply/Demand Shocks

### Step 4: Bayesian Change Point Modeling
- Implement Bayesian model using PyMC
- Define priors: change point location, means before/after, standard deviations
- Run MCMC sampling (NUTS algorithm)
- Check convergence using R-hat statistics and trace plots

### Step 5: Results Interpretation
- Extract posterior distributions of change points
- Identify most probable change dates
- Match change points with historical events
- Quantify impact: mean change, volatility change, percentage impact

### Step 6: Communication & Visualization
- Create interactive dashboard (Flask + React)
- Generate technical report with findings
- Prepare executive summary for stakeholders

## 2. Event Data

**File:** `data/events/key_events.csv`  
**Events:** 25 key events from 1990-2023  
**Categories:** Geopolitical Conflicts (8), Economic Crises (5), OPEC/Policy (6), Supply/Demand Shocks (6)

## 3. Assumptions & Limitations

### Assumptions:
1. **Market Efficiency**: Oil prices quickly incorporate new information
2. **Data Quality**: Historical price data is accurate and complete
3. **Immediate Impact**: Events have immediate or near-immediate effects
4. **Model Specification**: Normal distribution adequately models price changes
5. **Representativeness**: Brent prices reflect global oil market dynamics

### Limitations:
1. **Correlation ≠ Causation**: 
   - Just because a price change occurs after an event doesn't prove the event caused it
   - Other factors could be responsible
   - We identify statistical associations, not definitive causal relationships
   
2. **Multiple Confounding Factors**:
   - Events often occur simultaneously
   - Global economic conditions, currency fluctuations, alternative energy developments
   
3. **Model Limitations**:
   - Single change point model may oversimplify
   - Assumes abrupt changes (not gradual)
   - May miss small but important changes
   
4. **Data Limitations**:
   - Daily data may miss intra-day reactions
   - Only considers price, not volume or other market indicators

## 4. Communication Channels

### Primary Channels:
1. **Interactive Web Dashboard** (Flask + React)
   - Real-time price visualization
   - Event highlighting and filtering
   - Impact quantification display

2. **Technical Documentation** (MkDocs + Jupyter)
   - Complete analysis methodology
   - Code and implementation details
   - Statistical results and diagnostics

3. **Executive Reports** (PDF/Medium)
   - Non-technical summary of findings
   - Actionable insights for stakeholders
   - Visualizations and key takeaways

4. **API Access** (RESTful API)
   - Programmatic access to analysis results
   - Integration with other systems

### Target Audiences:
- **Investors**: Portfolio timing, risk management
- **Policymakers**: Economic stability planning, energy security
- **Energy Companies**: Supply chain planning, cost management
- **Analysts**: Market intelligence, forecasting models

## 5. Understanding Time Series Properties

### Key Properties to Analyze:
1. **Trend**: Long-term upward/downward movement in prices
2. **Stationarity**: Whether statistical properties change over time
3. **Volatility**: How much prices fluctuate
4. **Seasonality**: Regular repeating patterns
5. **Autocorrelation**: Relationship between current and past values

### How This Informs Modeling:
- **Non-stationary data** → Use differencing or log returns
- **High volatility** → Consider volatility models (GARCH)
- **Autocorrelation** → Include lag terms if needed
- **Non-normal returns** → Consider alternative distributions

## 6. Change Point Models

### Purpose:
Identify points in time when the statistical properties of a time series change significantly.

### How They Help:
1. **Detect Structural Breaks**: Find when market "regimes" change
2. **Quantify Changes**: Measure how much parameters changed
3. **Associate with Events**: Match changes with historical events
4. **Provide Probabilistic Estimates**: Give confidence intervals, not just point estimates

### Expected Outputs:
1. **Change Point Dates**: Most probable dates when changes occurred
2. **Parameter Estimates**: Means and volatilities before/after changes
3. **Impact Quantification**: "Price increased by X% with Y% probability"
4. **Uncertainty Measures**: Confidence intervals, posterior distributions

### Model Limitations:
1. Assumes changes are abrupt
2. May require specifying number of change points
3. Sensitive to model specification
4. Requires sufficient data between change points

## 7. References Reviewed
- Bayesian Time Series Analysis (Warwick PDF)
- PyMC Documentation and Tutorials
- Change Point Detection Methods
- Oil Market Event History

## Grade Improvement Plan (Rubric Gaps)
- **Time Series Analysis (0/6):** Add stationarity tests (ADF/KPSS), volatility analysis (rolling std), and interpret findings in Task 2 EDA.
- **Core Modeling:** Implement a Bayesian change point model in PyMC with trace diagnostics, posterior plots, and quantified impacts.
- **Code Best Practices (1/3):** Move reusable logic to `src/` modules (data loading, tests, plots), add basic error handling, and reduce notebook clutter.

## Data Summary
- Dataset: Brent oil daily prices
- Date range: 1987–2022
- Fields: Date, Price (USD/barrel)
- Events: `data/events/key_events.csv`

## References (Task 1)
- https://www.datascience-pm.com/data-science-workflow/
- https://forecastegy.com/posts/change-point-detection-time-series-python/
- https://www.pymc.io/blog/chris_F_pydata2022.html

