import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app.deep_heuristic import DeepHeuristicRewriter
print(DeepHeuristicRewriter.rewrite('The quick brown fox jumps over the lazy dog.'))
