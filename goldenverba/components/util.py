import numpy as np

# Step 1: Standardize the data
def standardize_data(X):
    mean = np.mean(X, axis=0)
    std_dev = np.std(X, axis=0)
    return (X - mean) / std_dev

# Step 2: Compute the covariance matrix
def compute_covariance_matrix(X):
    return np.cov(X, rowvar=False)

# Step 3: Perform eigenvalue decomposition of the covariance matrix
def eigen_decomposition(C):
    eigenvalues, eigenvectors = np.linalg.eig(C)
    return eigenvalues, eigenvectors

# Step 4: Sort the eigenvalues and their corresponding eigenvectors
def sort_eigenvalues_eigenvectors(eigenvalues, eigenvectors):
    idx = eigenvalues.argsort()[::-1]
    sorted_eigenvalues = eigenvalues[idx]
    sorted_eigenvectors = eigenvectors[:, idx]
    return sorted_eigenvalues, sorted_eigenvectors

# Step 5: Select the top k eigenvectors (principal components)
def select_top_k_components(eigenvectors, k):
    return eigenvectors[:, :k]

# Step 6: Transform the original data to the new subspace
def transform_data(X, components):
    return X.dot(components)

# Function to perform PCA
def pca(X, k):
    print(X[:10])
    X_standardized = standardize_data(X)
    print(X_standardized[:10])
    covariance_matrix = compute_covariance_matrix(X_standardized)
    print(covariance_matrix)
    eigenvalues, eigenvectors = eigen_decomposition(covariance_matrix)
    print(eigenvalues, eigenvectors)
    sorted_eigenvalues, sorted_eigenvectors = sort_eigenvalues_eigenvectors(eigenvalues, eigenvectors)
    top_k_components = select_top_k_components(sorted_eigenvectors, k)
    X_pca = transform_data(X_standardized, top_k_components)
    return X_pca