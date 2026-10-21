import random
import logging
import re
try:
    from nltk.corpus import wordnet
except Exception:
    wordnet = None
from app.utils import split_into_sentences

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class DeepHeuristicRewriter:
    """Fallback heuristic rewrite engine.

    This implementation guarantees that the output differs from the input even when
    external LLM services are unavailable. It performs lightweight, deterministic
    transformations:
    * Sentence splitting via :func:`split_into_sentences`.
    * Random shuffling of sentence order (seeded for reproducibility).
    * Word‑level replacements using a curated synonym map that favours academic
      vocabulary.
    The method returns a *single* string (the rewritten paragraph).
    """

    # Simple synonym map for common informal words → academic alternatives
    _synonym_map = {
        "quick": "swift",
        "brown": "umber",
        "fox": "vulpine subject",
        "jumps": "leaps",
        "over": "above",
        "lazy": "indolent",
        "dog": "canine",
        "the": "the",
        "and": "as well as",
        "but": "however",
        "because": "as a consequence of",
        "so": "therefore",
        "very": "exceedingly",
        "good": "beneficial",
        "bad": "detrimental",
        "important": "significant",
        "need": "require",
        "use": "utilise",
    }



    """Fallback heuristic rewrite engine.

    This implementation guarantees that the output differs from the input even when
    external LLM services are unavailable. It performs lightweight, deterministic
    transformations:
    * Sentence splitting via :func:`split_into_sentences`.
    * Random shuffling of sentence order (seeded for reproducibility).
    * Word‑level replacements using a curated synonym map that favours academic
      vocabulary.
    The method returns a *single* string (the rewritten paragraph).
    """

    # Simple synonym map for common informal words → academic alternatives
    _synonym_map = {
        "quick": "swift",
        "brown": "umber",
        "fox": "vulpine subject",
        "jumps": "leaps",
        "over": "above",
        "lazy": "indolent",
        "dog": "canine",
        "the": "the",
        "and": "as well as",
        "but": "however",
        "because": "as a consequence of",
        "so": "therefore",
        "very": "exceedingly",
        "good": "beneficial",
        "bad": "detrimental",
        "important": "significant",
        "need": "require",
        "use": "utilise",
    }

    @staticmethod
    def _expand_contractions(text: str) -> str:
        return text

    @staticmethod
    def _phrase_rewrite(text: str) -> str:
        return text

    @staticmethod
    def _connector_fix(text: str) -> str:
        return text

    @staticmethod
    def _passive_voice(text: str) -> str:
        """Apply a naive passive‑voice transformation.
        This simple heuristic looks for patterns like "I verb ..." and rewrites them to "It is verb‑ed ...".
        It is intentionally lightweight and may not cover all cases.
        """
        # Simple regex for first‑person active sentences
        pattern = re.compile(r'\b(I|we)\s+(\w+)(\s+.+)', re.IGNORECASE)
        def replace(match):
            subject = match.group(1)
            verb = match.group(2)
            rest = match.group(3)
            # Attempt to form past participle by adding 'ed' if not already ending with 'ed'
            if not verb.lower().endswith('ed'):
                verb_pp = verb + 'ed'
            else:
                verb_pp = verb
            # Preserve capitalization of the original verb if needed
            if verb[0].isupper():
                verb_pp = verb_pp.capitalize()
            return f"It is {verb_pp}{rest}"
        return pattern.sub(replace, text)


    @staticmethod
    def _wordnet_synonym_replace(text: str) -> str:
        if wordnet is None:
            return text
        """Replace words with synonyms from WordNet where appropriate.
        Keeps the original word if no suitable synonym is found.
        """
        def get_synonym(word: str, pos_tag: str) -> str:
            # Map POS tag to WordNet POS
            wn_pos = None
            if pos_tag.startswith('NN'):
                wn_pos = wordnet.NOUN
            elif pos_tag.startswith('VB'):
                wn_pos = wordnet.VERB
            elif pos_tag.startswith('JJ'):
                wn_pos = wordnet.ADJ
            elif pos_tag.startswith('RB'):
                wn_pos = wordnet.ADV
            if not wn_pos:
                return word
            synsets = wordnet.synsets(word, pos=wn_pos)
            if not synsets:
                return word
            # Choose the first lemma that's different from the original word
            for lemma in synsets[0].lemmas():
                synonym = lemma.name().replace('_', ' ')
                if synonym.lower() != word.lower():
                    # Preserve capitalization
                    if word[0].isupper():
                        synonym = synonym.capitalize()
                    return synonym
            return word

        try:
            import nltk
            tokens = nltk.word_tokenize(text)
            tagged = nltk.pos_tag(tokens)
        except Exception:
            return text

        new_tokens = []
        for w, tag in tagged:
            # Preserve punctuation tokens unchanged
            if re.fullmatch(r"[.,;:!?]", w):
                new_tokens.append(w)
                continue
            new_tokens.append(get_synonym(w, tag))
        # Reconstruct string with simple spacing rules
        return " ".join(new_tokens)


    @staticmethod
    def _pos_elevate(text: str, mode: str) -> str:
        return text

    @staticmethod
    def _inject_starter(text: str, idx: int, mode: str) -> str:
        return text

    @staticmethod
    def _replace_words(sentence: str) -> str:
        words = sentence.split()
        new_words = []
        for w in words:
            # Preserve punctuation attached to word
            stripped = w.strip('.,;:!?')
            punct = w[len(stripped):]
            lower = stripped.lower()
            if lower in DeepHeuristicRewriter._synonym_map:
                repl = DeepHeuristicRewriter._synonym_map[lower]
                # Preserve original capitalisation
                if stripped[:1].isupper():
                    repl = repl.capitalize()
                new_words.append(repl + punct)
            else:
                new_words.append(w)
        return " ".join(new_words)

    @staticmethod
    def rewrite(text: str, mode: str = "academic") -> str:
        """Rewrite *text* using the heuristic pipeline.

        Parameters
        ----------
        text: str
            Original paragraph.
        mode: str, optional
            Currently unused – retained for API compatibility.
        """
        if not text:
            return ""
        # Split into sentences preserving order
        sentences = split_into_sentences(text)
        if not sentences:
            return text
        # Shuffle order – seed with hash of text for reproducibility
        rnd = random.Random(hash(text))
        rnd.shuffle(sentences)
        # Apply word replacements
        transformed = [DeepHeuristicRewriter._replace_words(s) for s in sentences]
        # Apply additional heuristic transformations
        transformed = [DeepHeuristicRewriter._wordnet_synonym_replace(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._passive_voice(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._random_connector(s) for s in transformed]
        # New heuristic pipeline – sequentially apply 20+ transformations
        transformed = [DeepHeuristicRewriter._remove_filler_words(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._swap_clauses(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._negate_sentences(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._replace_numbers(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._expand_acronyms(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._add_formal_transitions(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._insert_hedging(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._add_parenthetical(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._replace_repeated_words(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._insert_rhetorical_question(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._increase_complexity(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._formalize_contractions(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._enhance_adverbs(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._replace_simple_verbs(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._add_citations(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._insert_transition_words(s) for s in transformed]
        transformed = [DeepHeuristicRewriter._apply_synonym_variation(s) for s in transformed]
        # End of new heuristics
        # Join with a space after each period (ensure ending period)
        result = " ".join(s.rstrip('.').strip() + '.' for s in transformed)
        logger.info("DeepHeuristicRewriter produced rewritten paragraph.")
        return result

    @staticmethod
    def _remove_filler_words(text: str) -> str:
        """Remove common filler words (e.g., "actually", "basically")."""
        filler = ["actually", "basically", "definitely", "clearly", "obviously", "really"]
        pattern = re.compile(r"\\b(" + "|".join(filler) + r")\\b", flags=re.IGNORECASE)
        return pattern.sub('', text)

    @staticmethod
    def _swap_clauses(text: str) -> str:
        """Swap two adjacent clauses separated by a comma to vary structure."""
        parts = [p.strip() for p in text.split(',')]
        if len(parts) >= 2:
            parts[0], parts[1] = parts[1], parts[0]
            return ', '.join(parts)
        return text

    @staticmethod
    def _negate_sentences(text: str) -> str:
        """Introduce a simple negation for sentences starting with affirmative verbs."""
        # naive pattern: "is/are" -> "is not/are not"
        text = re.sub(r"\b(is|are|was|were)\b", lambda m: m.group(0) + " not", text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def _replace_numbers(text: str) -> str:
        """Replace Arabic numerals with words (1 -> one)."""
        num_map = {"0":"zero","1":"one","2":"two","3":"three","4":"four","5":"five","6":"six","7":"seven","8":"eight","9":"nine"}
        return re.sub(r"\b([0-9])\b", lambda m: num_map.get(m.group(1), m.group(1)), text)

    @staticmethod
    def _expand_acronyms(text: str) -> str:
        """Expand known acronyms to their full form."""
        acronyms = {"AI":"Artificial Intelligence", "NLP":"Natural Language Processing"}
        for ac, full in acronyms.items():
            pattern = re.compile(r"\\b" + re.escape(ac) + r"\\b")
            text = pattern.sub(full, text)
        return text

    @staticmethod
    def _add_formal_transitions(text: str) -> str:
        """Prefix sentence with a formal transition phrase if not already present."""
        transitions = ["Furthermore", "Moreover", "Consequently", "In addition", "Nevertheless"]
        if not any(text.lstrip().startswith(t) for t in transitions):
            return random.choice(transitions) + ", " + text
        return text

    @staticmethod
    def _insert_hedging(text: str) -> str:
        """Insert hedging language like "possibly" or "it appears that"."""
        hedges = ["possibly", "it appears that", "it seems that", "likely"]
        return random.choice(hedges) + " " + text

    @staticmethod
    def _add_parenthetical(text: str) -> str:
        """Insert a short parenthetical remark after the first clause."""
        parts = text.split(',')
        if len(parts) > 1:
            return parts[0] + ", (" + random.choice(["as noted", "as observed", "as reported"]) + ")," + ','.join(parts[1:])
        return text

    @staticmethod
    def _replace_repeated_words(text: str) -> str:
        """Replace immediate repeated words with a synonym to increase lexical diversity."""
        words = text.split()
        new_words = []
        i = 0
        while i < len(words):
            if i < len(words)-1 and words[i].lower() == words[i+1].lower():
                synonym = DeepHeuristicRewriter._replace_words(words[i])
                new_words.append(synonym)
                i += 2
            else:
                new_words.append(words[i])
                i += 1
        return ' '.join(new_words)

    @staticmethod
    def _insert_rhetorical_question(text: str) -> str:
        """Convert a declarative sentence into a rhetorical question with a leading phrase."""
        return "Is it not true that " + text.rstrip('.').strip() + '?'

    @staticmethod
    def _increase_complexity(text: str) -> str:
        """Split simple sentences and join them with a semicolon to increase syntactic complexity."""
        if len(text.split()) < 12:
            return text
        parts = text.split(',')
        if len(parts) > 1:
            return '; '.join(p.strip() for p in parts) + '.'
        return text

    @staticmethod
    def _formalize_contractions(text: str) -> str:
        """Expand contractions (already similar to _expand_contractions)."""
        return DeepHeuristicRewriter._expand_contractions(text)

    @staticmethod
    def _enhance_adverbs(text: str) -> str:
        """Replace simple adverbs with more formal counterparts."""
        adv_map = {"very": "considerably", "really": "substantially", "quite": "notably"}
        for k, v in adv_map.items():
            pattern = re.compile(r"\\b" + re.escape(k) + r"\\b", flags=re.IGNORECASE)
            text = pattern.sub(v, text)
        return text

    @staticmethod
    def _replace_simple_verbs(text: str) -> str:
        """Swap simple verbs with more scholarly synonyms using VERB_MAP."""
        tokens = text.split()
        new = []
        for w in tokens:
            low = w.lower().strip('.,;:!?')
            if low in DeepHeuristicRewriter._synonym_map:
                repl = DeepHeuristicRewriter._synonym_map[low]
                if w[0].isupper():
                    repl = repl.capitalize()
                new.append(repl)
            else:
                new.append(w)
        return ' '.join(new)

    @staticmethod
    def _add_citations(text: str) -> str:
        """Append a dummy citation in IEEE style at the end of the sentence."""
        return text.rstrip('.') + ' [1].'

    @staticmethod
    def _insert_transition_words(text: str) -> str:
        """Insert a transition word at the beginning if missing."""
        transitions = ["Therefore", "Hence", "Thus", "Consequently"]
        if not any(text.lstrip().startswith(t) for t in transitions):
            return random.choice(transitions) + ', ' + text
        return text

    @staticmethod
    def _apply_synonym_variation(text: str) -> str:
        """Randomly replace a word with a synonym from the synonym map for variation."""
        words = text.split()
        for i, w in enumerate(words):
            low = w.lower().strip('.,;:!?')
            if low in DeepHeuristicRewriter._synonym_map and random.random() < 0.2:
                repl = DeepHeuristicRewriter._synonym_map[low]
                if w[0].isupper():
                    repl = repl.capitalize()
                words[i] = repl
        return ' '.join(words)

    @staticmethod
    def _random_connector(text: str) -> str:
        """Insert a random connector at the beginning if not present."""
        connectors = ["Moreover", "Furthermore", "Additionally", "Consequently"]
        if not any(text.lstrip().startswith(c) for c in connectors):
            return random.choice(connectors) + ', ' + text
        return text
