import unittest
from app.utils import split_into_sentences, count_syllables_in_word, calculate_readability_score, calculate_lexical_diversity, generate_changes_summary
from app.nlp_pipeline import RuleBasedHeuristics

class TestNLPComponents(unittest.TestCase):
    
    def test_sentence_splitter(self):
        text = "This is a sentence. Dr. Smith is here. We are studying e.g., biology. What is next? That's all!"
        sentences = split_into_sentences(text)
        
        self.assertEqual(len(sentences), 5)
        self.assertEqual(sentences[0], "This is a sentence.")
        self.assertEqual(sentences[1], "Dr. Smith is here.")
        self.assertEqual(sentences[2], "We are studying e.g., biology.")
        self.assertEqual(sentences[3], "What is next?")
        self.assertEqual(sentences[4], "That's all!")
        
    def test_syllable_counter(self):
        self.assertEqual(count_syllables_in_word("dog"), 1)
        self.assertEqual(count_syllables_in_word("biology"), 4)
        self.assertEqual(count_syllables_in_word("science"), 2)
        self.assertEqual(count_syllables_in_word("the"), 1)
        self.assertEqual(count_syllables_in_word("establish"), 3)

    def test_readability_score(self):
        # Academic text should have a low score (harder to read)
        academic_text = "The investigation demonstrated a substantial increase in cellular replication rates under elevated thermal conditions."
        simple_text = "This is a simple sentence about cells. It is very easy to read."
        
        score_academic = calculate_readability_score(academic_text)
        score_simple = calculate_readability_score(simple_text)
        
        # Simple text should have higher reading ease score
        self.assertTrue(score_simple > score_academic)

    def test_lexical_diversity(self):
        diverse = "The cat sat on a mat."
        repetitive = "The cat the cat the cat."
        
        div_score = calculate_lexical_diversity(diverse)
        rep_score = calculate_lexical_diversity(repetitive)
        
        self.assertTrue(div_score > rep_score)

    def test_heuristic_rewriter(self):
        input_text = "Basically, we think that a lot of cells got affected by the high heat."
        
        # Test academic style transformation
        enhanced_academic = RuleBasedHeuristics.apply(input_text, mode="academic")
        
        # Check that informal starters are replaced
        self.assertNotIn("Basically", enhanced_academic)
        self.assertIn("Fundamentally", enhanced_academic)
        
        # Check active to passive/formal conversion
        self.assertNotIn("we think that", enhanced_academic.lower())
        self.assertIn("it is posited that", enhanced_academic.lower())
        
        # Check informal vocabulary is elevated
        self.assertNotIn("a lot of", enhanced_academic)
        self.assertIn("a substantial number of", enhanced_academic)
        self.assertNotIn("got", enhanced_academic)
        self.assertIn("acquired", enhanced_academic)

if __name__ == "__main__":
    unittest.main()
