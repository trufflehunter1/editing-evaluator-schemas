import torch


def get_device() -> torch.device:
    """Apple MPS if available, else CPU."""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")
