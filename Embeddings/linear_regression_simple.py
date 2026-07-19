"""
Linear Regression - Simple Implementation (No Dependencies)
"""

class LinearRegression:
    def __init__(self):
        self.slope = None
        self.intercept = None
    
    def fit(self, X, y):
        """Fit using least squares method"""
        n = len(X)
        x_mean = sum(X) / n
        y_mean = sum(y) / n
        
        # Calculate slope
        numerator = sum((X[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((X[i] - x_mean) ** 2 for i in range(n))
        self.slope = numerator / denominator
        
        # Calculate intercept
        self.intercept = y_mean - self.slope * x_mean
        
        print(f"✓ Model trained!")
        print(f"  Equation: y = {self.slope:.4f}x + {self.intercept:.4f}")
    
    def predict(self, X):
        """Make predictions"""
        return [self.slope * x + self.intercept for x in X]
    
    def score(self, X, y):
        """Calculate R² score"""
        y_pred = self.predict(X)
        y_mean = sum(y) / len(y)
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(len(y)))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(len(y)))
        return 1 - (ss_res / ss_tot)
    
    def mse(self, X, y):
        """Calculate Mean Squared Error"""
        y_pred = self.predict(X)
        return sum((y[i] - y_pred[i]) ** 2 for i in range(len(y))) / len(y)


def example_salary():
    """Salary prediction example"""
    print("\n" + "="*60)
    print("EXAMPLE: Salary Prediction Based on Experience")
    print("="*60)
    
    # Data: Years of experience vs Salary (in thousands)
    years = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    salary = [40, 45, 50, 55, 65, 70, 75, 85, 90, 95]
    
    print("\nDataset:")
    print("Years | Salary ($k)")
    print("-" * 25)
    for x, y in zip(years, salary):
        print(f"  {x:2d}  |   {y:3d}")
    
    # Train model
    print("\nTraining model...")
    model = LinearRegression()
    model.fit(years, salary)
    
    # Evaluate
    r2 = model.score(years, salary)
    mse = model.mse(years, salary)
    
    print(f"\nModel Performance:")
    print(f"  R² Score: {r2:.4f} ({r2*100:.2f}% variance explained)")
    print(f"  MSE: {mse:.4f}")
    
    # Predictions
    print("\nPredictions for new data:")
    test_years = [3, 7, 12, 15]
    predictions = model.predict(test_years)
    for x, pred in zip(test_years, predictions):
        print(f"  {x:2d} years → ${pred:.2f}k predicted salary")


def example_manual():
    """Step-by-step manual calculation"""
    print("\n" + "="*60)
    print("MANUAL CALCULATION - Step by Step")
    print("="*60)
    
    X = [1, 2, 3, 4, 5]
    y = [2, 4, 5, 4, 5]
    
    print("\nDataset:")
    print("X | Y")
    print("-" * 10)
    for xi, yi in zip(X, y):
        print(f"{xi} | {yi}")
    
    # Step 1: Means
    n = len(X)
    x_mean = sum(X) / n
    y_mean = sum(y) / n
    print(f"\nStep 1: Calculate means")
    print(f"  x̄ = {x_mean:.2f}")
    print(f"  ȳ = {y_mean:.2f}")
    
    # Step 2: Deviations
    print(f"\nStep 2: Calculate deviations and products")
    print("X | Y | (X-x̄) | (Y-ȳ) | (X-x̄)(Y-ȳ) | (X-x̄)²")
    print("-" * 60)
    
    numerator = 0
    denominator = 0
    for xi, yi in zip(X, y):
        x_dev = xi - x_mean
        y_dev = yi - y_mean
        xy_prod = x_dev * y_dev
        x_sq = x_dev ** 2
        numerator += xy_prod
        denominator += x_sq
        print(f"{xi} | {yi} | {x_dev:6.2f} | {y_dev:6.2f} | {xy_prod:11.2f} | {x_sq:7.2f}")
    
    # Step 3: Slope
    slope = numerator / denominator
    print(f"\nStep 3: Calculate slope")
    print(f"  m = Σ[(X-x̄)(Y-ȳ)] / Σ[(X-x̄)²]")
    print(f"  m = {numerator:.2f} / {denominator:.2f}")
    print(f"  m = {slope:.4f}")
    
    # Step 4: Intercept
    intercept = y_mean - slope * x_mean
    print(f"\nStep 4: Calculate intercept")
    print(f"  b = ȳ - m·x̄")
    print(f"  b = {y_mean:.2f} - {slope:.4f} × {x_mean:.2f}")
    print(f"  b = {intercept:.4f}")
    
    print(f"\n✓ Final Equation: y = {slope:.4f}x + {intercept:.4f}")
    
    # Verify
    model = LinearRegression()
    model.fit(X, y)
    print(f"\nVerification:")
    print(f"  Slopes match: {abs(model.slope - slope) < 0.0001}")
    print(f"  Intercepts match: {abs(model.intercept - intercept) < 0.0001}")


def example_house_prices():
    """House price prediction"""
    print("\n" + "="*60)
    print("EXAMPLE: House Price Prediction")
    print("="*60)
    
    # Data: Size (sq ft) vs Price ($k)
    size = [800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600]
    price = [150, 180, 210, 240, 270, 300, 330, 360, 390, 420]
    
    print("\nDataset:")
    print("Size (sq ft) | Price ($k)")
    print("-" * 30)
    for x, y in zip(size, price):
        print(f"    {x:4d}     |    {y:3d}")
    
    # Train
    model = LinearRegression()
    model.fit(size, price)
    
    # Evaluate
    r2 = model.score(size, price)
    print(f"\nR² Score: {r2:.4f}")
    
    # Predictions
    print("\nPredictions:")
    test_sizes = [1500, 2000, 2800, 3000]
    predictions = model.predict(test_sizes)
    for x, pred in zip(test_sizes, predictions):
        print(f"  {x:4d} sq ft → ${pred:.2f}k")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LINEAR REGRESSION - COMPLETE EXAMPLES")
    print("No external dependencies required!")
    print("="*60)
    
    example_salary()
    example_manual()
    example_house_prices()
    
    print("\n" + "="*60)
    print("✓ All examples completed successfully!")
    print("="*60)
    print("\nKey Formulas:")
    print("  Slope:     m = Σ[(x-x̄)(y-ȳ)] / Σ[(x-x̄)²]")
    print("  Intercept: b = ȳ - m·x̄")
    print("  Equation:  y = mx + b")
    print("  R² Score:  R² = 1 - (SS_res / SS_tot)")
    print("="*60 + "\n")
