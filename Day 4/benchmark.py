"""Compare a Python loop with a vectorized NumPy expression."""
from time import perf_counter
import numpy as np

def loop_transform(values: np.ndarray) -> np.ndarray:
    result = np.empty_like(values)
    for i, value in enumerate(values):
        result[i] = value * value + 2 * value + 1
    return result

def vectorized_transform(values: np.ndarray) -> np.ndarray:
    return values * values + 2 * values + 1

def median_runtime(function, values, repeats=5):
    timings = []
    for _ in range(repeats):
        start = perf_counter()
        result = function(values)
        timings.append(perf_counter() - start)
    return float(np.median(timings)), result

def main():
    rng = np.random.default_rng(42)
    values = rng.random(500_000)
    loop_time, loop_result = median_runtime(loop_transform, values)
    vector_time, vector_result = median_runtime(vectorized_transform, values)
    print(f"Python loop median: {loop_time:.6f} seconds")
    print(f"NumPy vectorized median: {vector_time:.6f} seconds")
    print(f"Speedup: {loop_time / vector_time:.2f}x")
    print("Results match:", np.allclose(loop_result, vector_result))

if __name__ == "__main__":
    main()
