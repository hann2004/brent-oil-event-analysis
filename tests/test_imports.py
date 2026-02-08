"""Import sanity checks for core dependencies."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc as pm


def test_imports():
    """Test that all required packages can be imported."""
    assert plt is not None
    assert pd.__version__ >= "2.0.0"
    assert np.__version__ >= "1.24.0"
    assert pm.__version__ >= "5.0.0"

    print("All imports successful!")
