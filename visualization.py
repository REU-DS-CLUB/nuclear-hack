import numpy as np
import matplotlib as plt
from sklearn.metrics import mean_squared_error


def stability_plot(X_test, y_test, model, sampling_count=300, sample_size=200):
    mse_scores = []

    for _ in range(sampling_count):
        sample_indices = rng.choice(X_test.index, size=sample_size, replace=False)
        X_test_sample = X_test.loc[sample_indices]
        y_test_sample = y_test.loc[sample_indices]

        y_pred_sample = model.predict(X_test_sample)

        mse = mean_squared_error(y_test_sample, y_pred_sample)
        mse_scores.append(mse)

    plt.hist(mse_scores, bins=10, density=True, color='skyblue')
    plt.title('Distribution of MSE for random samples of the test set')
    plt.xlabel('MSE Score')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.show()

    quantile_5 = np.percentile(mse_scores, 5)
    quantile_95 = np.percentile(mse_scores, 95)

    print(f"5th percentile: {quantile_5}")
    print(f"95th percentile: {quantile_95}")