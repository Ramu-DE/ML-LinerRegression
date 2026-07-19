# Linear Regression - Complete Guide

## 📚 What is Linear Regression?

Linear regression is a statistical method to model the relationship between a dependent variable (y) and one or more independent variables (x) using a straight line.

## 🎯 The Core Equation

```
y = mx + b
```

Where:
- **y** = predicted value (dependent variable)
- **x** = input value (independent variable)  
- **m** = slope (rate of change)
- **b** = y-intercept (value when x=0)

Alternative notation: `ŷ = β₀ + β₁x`

## 📐 Key Formulas

### 1. Slope (m)
```
m = Σ[(xᵢ - x̄)(yᵢ - ȳ)] / Σ[(xᵢ - x̄)²]
```
Or using covariance:
```
m = Cov(x,y) / Var(x)
```

### 2. Intercept (b)
```
b = ȳ - m·x̄
```
Where x̄ and ȳ are the means of x and y

### 3. Mean Squared Error (MSE)
```
MSE = (1/n) Σ(yᵢ - ŷᵢ)²
```
Measures average squared difference between actual and predicted values

### 4. Root Mean Squared Error (RMSE)
```
RMSE = √MSE
```
Same units as the target variable

### 5. R² Score (Coefficient of Determination)
```
R² = 1 - (SS_res / SS_tot)

Where:
SS_res = Σ(yᵢ - ŷᵢ)²  (residual sum of squares)
SS_tot = Σ(yᵢ - ȳ)²   (total sum of squares)
```

**Interpretation:**
- R² = 1.0 → Perfect fit
- R² = 0.0 → No better than predicting the mean
- Range: 0 to 1 (higher is better)

## 🔍 Step-by-Step Process

1. **Collect Data**: Gather (x, y) pairs
2. **Calculate Means**: Find x̄ and ȳ
3. **Calculate Slope**: Use the slope formula
4. **Calculate Intercept**: Use b = ȳ - m·x̄
5. **Make Predictions**: Use ŷ = mx + b
6. **Evaluate**: Calculate MSE and R²

## 📊 Files Included

1. **linear_regression_visual.html** - Interactive visualization with:
   - Adjustable slope and intercept sliders
   - Real-time residuals display
   - Formula explanations
   - Best-fit line calculator

2. **linear_regression_examples.py** - Python implementation with:
   - Custom LinearRegression class from scratch
   - 4 complete examples with real datasets
   - Step-by-step manual calculations
   - Comparison with scikit-learn

## 🚀 Quick Start

### View Interactive Visualization
```bash
# Open in browser
xdg-open linear_regression_visual.html
```

### Run Python Examples
```bash
# Install dependencies
pip install numpy matplotlib

# Run all examples
python linear_regression_examples.py
```

## 📈 Example Output

### Example 1: Salary Prediction
```
Years | Salary ($k)
--------------------
    1 |     40
    2 |     45
    3 |     50
    ...

Model trained successfully!
Equation: y = 5.9394x + 34.5455

Model Performance:
R² Score: 0.9897 (98.97% variance explained)
MSE: 6.8595
RMSE: 2.6191

Predictions:
3 years experience → $52.36k predicted salary
7 years experience → $76.12k predicted salary
```

## 🎨 Visualizations Generated

The Python script generates:
- `salary_prediction.png` - Salary vs Experience plot
- `house_price_prediction.png` - House Price vs Size plot

## 💡 Key Concepts

### Residuals
The difference between actual and predicted values:
```
residual = yᵢ - ŷᵢ
```

### Least Squares Method
Finds the line that minimizes the sum of squared residuals:
```
minimize: Σ(yᵢ - ŷᵢ)²
```

### Assumptions
1. **Linearity**: Relationship between x and y is linear
2. **Independence**: Observations are independent
3. **Homoscedasticity**: Constant variance of residuals
4. **Normality**: Residuals are normally distributed

## 🔧 Usage Examples

### Basic Usage
```python
from linear_regression_examples import LinearRegression
import numpy as np

# Create and train model
model = LinearRegression()
X = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 5, 4, 5])
model.fit(X, y)

# Make predictions
predictions = model.predict(np.array([6, 7, 8]))

# Evaluate
r2_score = model.score(X, y)
mse = model.mse(X, y)
```

## 📚 Real-World Applications

1. **Finance**: Stock price prediction, risk assessment
2. **Real Estate**: Property valuation
3. **Marketing**: Sales forecasting, ROI prediction
4. **Healthcare**: Disease progression modeling
5. **Economics**: GDP forecasting, demand estimation

## 🎓 When to Use Linear Regression

✅ **Good for:**
- Continuous target variables
- Linear relationships
- Simple, interpretable models
- Quick baseline models

❌ **Not ideal for:**
- Non-linear relationships (use polynomial regression)
- Categorical targets (use logistic regression)
- Complex patterns (use neural networks)

## 📖 Further Reading

- Multiple Linear Regression (multiple features)
- Polynomial Regression (non-linear relationships)
- Regularization (Ridge, Lasso)
- Gradient Descent optimization

---

**Created for educational purposes**
Complete implementation with formulas, visualizations, and working code examples.
