"""
Templates Module
Contains all experiment template generators
"""

from .base_template import BaseTemplate
from .network import NetworkTemplate
from .particles import ParticlesTemplate
from .flocking import FlockingTemplate
from .waves import WavesTemplate

__all__ = [
    "BaseTemplate",
    "NetworkTemplate",
    "ParticlesTemplate",
    "FlockingTemplate",
    "WavesTemplate"
]
