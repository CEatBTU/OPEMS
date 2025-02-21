import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
size = 1000000  # Size of the tensors
arr1 = torch.rand(size, dtype=torch.float32, device=device)
arr2 = torch.rand(size, dtype=torch.float32, device=device)

result = arr1 + arr2
print(f"Result of first 10 elements: {result[:10]}")