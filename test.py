import torch

print(torch.cuda.is_available())  # should print True
print(torch.version.hip)  # should report “6.4.1” or similar
