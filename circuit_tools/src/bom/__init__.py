'''
@package bom
@file bom/__init__.py
@brief Bill Of Materials package
'''
__all__ = ["parser", "circuit", "component"]

from bom.circuit import BOMCircuit
from bom.component import BOMComponent


#parser = bom.parser