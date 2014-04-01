import numpy as np

def autocorrelation(x):
    n = x.shape[0]
    x = x - x.mean()
    r = np.correlate(x, x, mode='full')[-n:]
    return r/(x.var()*np.arange(n, 0, -1))

def test_autocorrelation():
    x = np.random.rand(100) + np.random.rand()
    n = len(x)
    x = x - x.mean()
    r = autocorrelation(x)
    assert np.allclose(r*x.var()*np.arange(n, 0, -1), [(x[:n-k]*x[-(n-k):]).sum() for k in range(n)])

if __name__ == '__main__':
    test_autocorrelation()
