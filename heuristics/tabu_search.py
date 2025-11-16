from tools import *
from heuristics import construction

def solve(customers, vehicles, to_fulfilled, rho):
    x = construction.solve(customers, vehicles, to_fulfilled, rho)