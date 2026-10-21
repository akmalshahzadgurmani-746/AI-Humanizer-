import sys, os
# Ensure the backend package is importable
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app.nlp_pipeline import NLPEngine

text = "The quick brown fox jumps over the lazy dog."
rewritten, engine = NLPEngine.rewrite(text, mode="academic")
print('Engine:', engine)
print('Result:', rewritten)
