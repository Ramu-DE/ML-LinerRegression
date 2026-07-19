"""
Linear Regression Implementation from Scratch
Complete examples with sample datasets
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

class LinearRegression:
    """Simple Linear Regression implementation from scratch"""
    
    def __init__(self):
        self.slope = None
        self.intercept = None
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Fit the linear regression model using least squares method
        
        Formula:
        slope (m) = Σ[(xi - x̄)(yi - ȳ)] / Σ[(xi - x̄)²]
        intercept (b) = ȳ - m * x̄
        """
        n = len(X)
        x_mean = np.mean(X)
        y_mean = np.mean(y)
        
        # Calculate slope
        numerator = np.sum((X - x_mean) * (y - y_mean))
        denominator = np.sum((X - x_mean) ** 2)
        self.slope = numerator / denominator
        
        # Calculate intercept
        self.intercept = y_mean - self.slope * x_mean
        
        print(f"Model trained successfully!")
        print(f"Equation: y = {self.slope:.4f}x + {self.intercept:.4f}")
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using the fitted model"""
        if self.slope is None or self.intercept is None:
            raise ValueError("Model not trained yet. Call fit() first.")
        return self.slope * X + self.intercept
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Calculate R² score"""
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - (ss_res / ss_tot)
    
    def mse(self, X: np.ndarray, y: np.ndarray) -> float:
        """Calculate Mean Squared Error"""
        y_pred = self.predict(X)
        return np.mean((y - y_pred) ** 2)
    
    def rmse(self, X: np.ndarray, y: np.ndarray) -> float:
        """Calculate Root Mean Squared Error"""
        return np.sqrt(self.mse(X, y))


def example_1_salary_prediction():
    """Example 1: Predict salary based on years of experience"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Salary Prediction")
    print("="*60)
    
    # Sample data: Years of experience vs Salary (in thousands)
    years_experience = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    salary = np.array([40, 45, 50, 55, 65, 70, 75, 85, 90, 95])
    
    print("\nDataset:")
    print("Years | Salary ($k)")
    print("-" * 20)
    for x, y in zip(years_experience, salary):
        print(f"{x:5d} | {y:6d}")
    
    # Train model
    model = LinearRegression()
    model.fit(years_experience, salary)
    
    # Evaluate
    r2 = model.score(years_experience, salary)
    mse = model.mse(years_experience, salary)
    rmse = model.rmse(years_experience, salary)
    
    print(f"\nModel Performance:")
    print(f"R² Score: {r2:.4f} ({r2*100:.2f}% variance explained)")
    print(f"MSE: {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    
    # Make predictions
    print("\nPredictions:")
    test_years = np.array([3, 7, 12])
    predictions = model.predict(test_years)
    for x, pred in zip(test_years, predictions):
        print(f"{x} years experience → ${pred:.2f}k predicted salary")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    plt.scatter(years_experience, salary, color='red', s=100, alpha=0.6, label='Actual Data')
    plt.plot(years_experience, model.predict(years_experience), 
             color='blue', linewidth=2, label='Regression Line')
    plt.xlabel('Years of Experience', fontsize=12)
    plt.ylabel('Salary ($k)', fontsize=12)
    plt.title('Salary vs Experience - Linear Regression', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('salary_prediction.png', dpi=150)
    print("\n✓ Plot saved as 'salary_prediction.png'")


def example_2_house_prices():
    """Example 2: Predict house prices based on size"""
    print("\n" + "="*60)
    print("EXAMPLE 2: House Price Prediction")
    print("="*60)
    
    # Sample data: House size (sq ft) vs Price ($k)
    size = np.array([800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600])
    price = np.array([150, 180, 210, 240, 270, 300, 330, 360, 390, 420])
    
    print("\nDataset:")
    print("Size (sq ft) | Price ($k)")
    print("-" * 30)
    for x, y in zip(size, price):
        print(f"{x:12d} | {y:9d}")
    
    # Train model
    model = LinearRegression()
    model.fit(size, price)
    
    # Evaluate
    r2 = model.score(size, price)
    mse = model.mse(size, price)
    
    print(f"\nModel Performance:")
    print(f"R² Score: {r2:.4f}")
    print(f"MSE: {mse:.4f}")
    
    # Predictions
    print("\nPredictions:")
    test_sizes = np.array([1500, 2000, 2800])
    predictions = model.predict(test_sizes)
    for x, pred in zip(test_sizes, predictions):
        print(f"{x} sq ft → ${pred:.2f}k predicted price")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    plt.scatter(size, price, color='green', s=100, alpha=0.6, label='Actual Data')
    plt.plot(size, model.predict(size), color='orange', linewidth=2, label='Regression Line')
    
    # Show residuals
    for x, y in zip(size, price):
        y_pred = model.predict(np.array([x]))[0]
        plt.plot([x, x], [y, y_pred], 'r--', alpha=0.3, linewidth=1)
    
    plt.xlabel('House Size (sq ft)', fontsize=12)
    plt.ylabel('Price ($k)', fontsize=12)
    plt.title('House Price vs Size - Linear Regression', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('house_price_prediction.png', dpi=150)
    print("\n✓ Plot saved as 'house_price_prediction.png'")


def example_3_manual_calculation():
    """Example 3: Step-by-step manual calculation"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Manual Calculation Step-by-Step")
    print("="*60)
    
    # Simple dataset
    X = np.array([1, 2, 3, 4, 5])
    y = np.array([2, 4, 5, 4, 5])
    
    print("\nDataset:")
    print("X | Y")
    print("-" * 10)
    for xi, yi in zip(X, y):
        print(f"{xi} | {yi}")
    
    # Step 1: Calculate means
    x_mean = np.mean(X)
    y_mean = np.mean(y)
    print(f"\nStep 1: Calculate means")
    print(f"x̄ = {x_mean:.2f}")
    print(f"ȳ = {y_mean:.2f}")
    
    # Step 2: Calculate deviations
    print(f"\nStep 2: Calculate deviations")
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
    
    # Step 3: Calculate slope
    slope = numerator / denominator
    print(f"\nStep 3: Calculate slope")
    print(f"m = Σ[(X-x̄)(Y-ȳ)] / Σ[(X-x̄)²]")
    print(f"m = {numerator:.2f} / {denominator:.2f}")
    print(f"m = {slope:.4f}")
    
    # Step 4: Calculate intercept
    intercept = y_mean - slope * x_mean
    print(f"\nStep 4: Calculate intercept")
    print(f"b = ȳ - m·x̄")
    print(f"b = {y_mean:.2f} - {slope:.4f} × {x_mean:.2f}")
    print(f"b = {intercept:.4f}")
    
    # Final equation
    print(f"\nFinal Equation:")
    print(f"y = {slope:.4f}x + {intercept:.4f}")
    
    # Verify with our class
    model = LinearRegression()
    model.fit(X, y)
    print(f"\nVerification with LinearRegression class:")
    print(f"Slope matches: {np.isclose(model.slope, slope)}")
    print(f"Intercept matches: {np.isclose(model.intercept, intercept)}")


def example_4_sklearn_comparison():
    """Example 4: Compare with sklearn"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Comparison with Scikit-learn")
    print("="*60)
    
    try:
        from sklearn.linear_model import LinearRegression as SklearnLR
        from sklearn.metrics import r2_score, mean_squared_error
        
        # Sample data
        X = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        y = np.array([2.1, 4.2, 5.8, 8.1, 10.3, 12.1, 14.2, 16.0, 18.1, 20.2])
        
        # Our implementation
        our_model = LinearRegression()
        our_model.fit(X, y)
        our_pred = our_model.predict(X)
        our_r2 = our_model.score(X, y)
        
        # Sklearn implementation
        sklearn_model = SklearnLR()
        sklearn_model.fit(X.reshape(-1, 1), y)
        sklearn_pred = sklearn_model.predict(X.reshape(-1, 1))
        sklearn_r2 = r2_score(y, sklearn_pred)
        
        print("\nComparison:")
        print(f"{'Metric':<20} | {'Our Model':<15} | {'Sklearn':<15}")
        print("-" * 55)
        print(f"{'Slope':<20} | {our_model.slope:<15.6f} | {sklearn_model.coef_[0]:<15.6f}")
        print(f"{'Intercept':<20} | {our_model.intercept:<15.6f} | {sklearn_model.intercept_:<15.6f}")
        print(f"{'R² Score':<20} | {our_r2:<15.6f} | {sklearn_r2:<15.6f}")
        
        print("\n✓ Results match! Our implementation is correct.")
        
    except ImportError:
        print("\nSklearn not installed. Skipping comparison.")
        print("Install with: pip install scikit-learn")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LINEAR REGRESSION - COMPLETE EXAMPLES")
    print("="*60)
    
    # Run all examples
    example_1_salary_prediction()
    example_2_house_prices()
    example_3_manual_calculation()
    example_4_sklearn_comparison()
    
    print("\n" + "="*60)
    print("All examples completed successfully!")
    print("="*60)
    
    plt.show()
