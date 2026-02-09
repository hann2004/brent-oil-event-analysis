# Task 1: Analysis Foundation and Plan
## Brent Oil Price Analysis with Bayesian Change Point Detection

### 1. Project Overview
**Objective**: Analyze how geopolitical/economic events affect Brent oil prices using Bayesian change point detection to identify structural breaks and quantify event impacts.

### 2. Analysis Workflow Steps

#### Phase 1: Data Preparation & Exploration (Current Status: ✓ Partial Completion)
1. **Data Loading & Cleaning** - `src/data_preprocessing.py` implemented
   - Load historical Brent oil prices (1987-2022)
   - Parse dates in "day-month-year" format
   - Handle missing values with linear interpolation
   - Load geopolitical events data

2. **Exploratory Data Analysis (EDA)** - `notebooks/01_eda.ipynb` started
   - Visualize price trends over 35-year period
   - Calculate and analyze returns (percentage and log returns)
   - Test for stationarity (ADF test implemented)
   - Analyze volatility patterns

#### Phase 2: Time Series Analysis (To Be Completed)
3. **Statistical Properties Analysis**
   - Trend analysis using moving averages (30-day, 90-day, 365-day)
   - Seasonality detection (monthly, quarterly patterns)
   - Volatility clustering analysis (GARCH properties)
   - Breakpoint visualization with events overlay

4. **Event-Window Analysis**
   - Extract price behavior ±30 days around each event
   - Calculate pre/post event price changes
   - Analyze volatility shifts around events
   - Correlate event types with impact magnitude

#### Phase 3: Bayesian Change Point Modeling (To Be Completed)
5. **Model Specification** - `src/bayesian_model.py` started
   - Define prior distributions for change points (DiscreteUniform)
   - Specify likelihood function (Normal distribution)
   - Set up MCMC sampling parameters (chains, draws, tuning)

6. **Model Implementation**
   - Implement single change point model (completed)
   - Extend to multiple change point detection
   - Run MCMC sampling with PyMC
   - Check convergence diagnostics (R-hat, trace plots)

7. **Change Point Detection & Quantification**
   - Identify posterior distribution of change points
   - Quantify parameter shifts (mean, volatility changes)
   - Calculate credible intervals (95% HDI)
   - Map detected changes to known events

#### Phase 4: Insights & Reporting (To Be Completed)
8. **Impact Analysis**
   - Quantify event impacts in USD and percentage terms
   - Calculate confidence intervals for impact estimates
   - Rank events by impact magnitude

9. **Stakeholder Recommendations**
   - Investment strategy implications
   - Policy development insights
   - Operational planning guidance

### 3. Event Data Compilation
**Current Status**: 24 key events compiled (1990-2022)
- **File**: `data/events/key_events.csv`
- **Coverage**: Conflicts, economic crises, OPEC decisions, supply disruptions, pandemics
- **Time Span**: 32 years of major oil market events

**Event Categories**:
1. **Conflicts/Geopolitical** (9 events): Iraq invasions, Gulf War, Arab Spring, Russia-Ukraine war
2. **Economic Crises** (4 events): Asian financial crisis, dot-com slowdown, 2008 crisis, COVID-19
3. **OPEC/Policy Decisions** (4 events): Production cuts, output decisions
4. **Supply Disruptions** (3 events): Hurricane Katrina, Libya civil war, Abqaiq attack
5. **Sanctions/Other** (4 events): Iran deal, price caps, etc.

### 4. Assumptions & Limitations

#### Key Assumptions:
1. **Market Efficiency Assumption**: Oil prices reflect all available information at time t
2. **Exogeneity Assumption**: Events are external shocks to the market
3. **Structural Break Assumption**: Price dynamics change abruptly at detected points
4. **Data Quality Assumption**: Historical data is accurate and representative
5. **Model Specification**: Normal distribution adequately captures price returns

#### Important Limitations:
1. **Causality vs Correlation**: 
   - **Critical Limitation**: Detected change points may correlate with but not necessarily be caused by listed events
   - **Example**: A change point might coincide with an event but be driven by unobserved factors
   - **Mitigation**: Use event windows and control for other known factors

2. **Multiple Simultaneous Events**:
   - Events often cluster in time (e.g., 2008 financial crisis with OPEC decisions)
   - Attribution of price changes to specific events is challenging
   - **Approach**: Use Bayesian model averaging to assess probabilities

3. **Market Anticipation Effects**:
   - Prices may adjust before official event dates (e.g., sanctions announcements)
   - **Impact**: Change points may precede actual event dates
   - **Solution**: Include announcement dates where available

4. **Model Simplifications**:
   - Single change point model may miss multiple regime shifts
   - Normal distribution may not capture fat tails in oil returns
   - **Plan**: Extend to multiple change points and student-t distributions

5. **Time Lag Considerations**:
   - Event impacts may unfold over days/weeks, not instantaneously
   - **Approach**: Analyze event windows (±30 days) rather than single dates

6. **Confounding Variables**:
   - Macroeconomic factors (GDP, inflation, USD strength)
   - Technological changes (shale revolution)
   - **Acknowledgment**: These are not explicitly modeled in initial analysis

### 5. Communication Channels

#### Primary Outputs:
1. **Technical Report**: Comprehensive analysis document (Markdown/PDF)
   - **Location**: `docs/results.md`
   - **Audience**: Data science team, technical stakeholders

2. **Interactive Dashboard**: Web application for exploration
   - **Technology**: React frontend + Flask backend
   - **Purpose**: Stakeholder self-service analysis

3. **Executive Summary**: 1-page key findings document
   - **Format**: PDF with infographics
   - **Audience**: C-level executives, policymakers

4. **Jupyter Notebooks**: Reproducible analysis
   - **Location**: `notebooks/` directory
   - **Files**: EDA, modeling, visualization notebooks

5. **GitHub Repository**: Code and documentation
   - **URL**: Your repository link
   - **Features**: Issues, projects, documentation

#### Presentation Formats:
- **Investors**: Focus on risk management and timing insights
- **Policymakers**: Emphasize stability and security implications
- **Energy Companies**: Highlight operational planning applications

### 6. Technical Implementation Plan

#### Completed Components (✓):
- ✅ Data loading and preprocessing (`src/data_preprocessing.py`)
- ✅ Basic EDA notebook (`notebooks/01_eda.ipynb`)
- ✅ Bayesian model skeleton (`src/bayesian_model.py`)
- ✅ Visualization utilities (`src/visualization.py`)
- ✅ Time series utilities (`src/time_series.py`)

#### To Be Developed:
1. **Enhanced EDA** (2 days):
   - Complete stationarity analysis
   - Volatility clustering visualization
   - Event overlay plots

2. **Bayesian Modeling** (3 days):
   - Complete single change point implementation
   - Add convergence diagnostics
   - Implement multiple change point detection
   - Model comparison metrics

3. **Impact Analysis** (2 days):
   - Event-window impact quantification
   - Statistical significance testing
   - Confidence interval calculation

4. **Dashboard Development** (3 days):
   - Flask API endpoints
   - React frontend components
   - Interactive visualizations

### 7. Risk Management

#### Technical Risks:
1. **Computational Intensity**: MCMC sampling for long time series
   - **Mitigation**: Use efficient sampling, reduce tuning steps initially

2. **Model Convergence**: Poor mixing or non-convergence
   - **Mitigation**: Multiple chains, extensive diagnostics, parameter tuning

3. **Data Quality Issues**: Gaps or anomalies in price data
   - **Mitigation**: Robust interpolation, outlier detection

#### Project Risks:
1. **Scope Creep**: Adding too many features
   - **Mitigation**: Stick to core Bayesian analysis, defer enhancements

2. **Interpretation Complexity**: Explaining Bayesian results to non-technical stakeholders
   - **Mitigation**: Clear visualizations, simple language summaries

### 8. Success Metrics

#### Quantitative:
- Model convergence (R-hat < 1.05 for all parameters)
- Change point detection with >90% posterior probability
- Quantified impact estimates with 95% credible intervals
- Correlation of >70% between detected change points and known events

#### Qualitative:
- Clear, actionable insights for all stakeholder groups
- Intuitive dashboard interface
- Comprehensive documentation
- Reproducible analysis pipeline

---

## Next Steps for Task 1 Completion

1. **Complete EDA Analysis**:
   - Run full stationarity tests on price and returns
   - Create comprehensive visualization suite
   - Document key time series properties

2. **Finalize Assumptions Document**:
   - Add specific examples for each limitation
   - Document mitigation strategies
   - Create stakeholder-specific caveats

3. **Prepare Interim Submission**:
   - Compile all Task 1 deliverables
   - Ensure GitHub repository is organized
   - Create README with setup instructions

**Estimated Completion Time**: 1-2 days