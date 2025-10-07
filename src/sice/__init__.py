import importlib.metadata

assert __package__
__version__ = importlib.metadata.version(__package__)
__doc__ = importlib.metadata.metadata(__package__)["Summary"]
