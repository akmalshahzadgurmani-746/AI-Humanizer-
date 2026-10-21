import re

def split_into_sentences(text: str) -> list[str]:
    """
    Split text into individual sentences while respecting common academic abbreviations
    like e.g., i.e., Al., Prof., Dr., etc.
    """
    if not text:
        return []
    
    # Split by standard sentence terminators (. ! ?) followed by spaces
    raw_splits = re.split(r'(?<=[.!?])\s+', text.strip())
    
    # Common abbreviations to merge back
    abbreviations = {
        "dr.", "prof.", "mr.", "mrs.", "ms.", "e.g.", "i.e.", "al.", 
        "vs.", "gen.", "col.", "sgt.", "jan.", "feb.", "mar.", "apr.", 
        "jun.", "jul.", "aug.", "sep.", "oct.", "nov.", "dec."
    }
    
    sentences = []
    buffer = ""
    
    for split in raw_splits:
        if buffer:
            buffer += " " + split
        else:
            buffer = split
            
        # Check if the last word of the buffer is in the abbreviations set
        words = buffer.split()
        if words:
            last_word = words[-1].lower().rstrip(",:;")
            # Merge if last word is a known abbreviation or is a single-letter initials like A.
            if last_word in abbreviations or (len(last_word) > 1 and last_word.endswith(".") and last_word[:-1].isalpha() and len(last_word[:-1]) <= 2):
                continue
        
        sentences.append(buffer)
        buffer = ""
        
    if buffer:
        sentences.append(buffer)
        
    return [s.strip() for s in sentences if s.strip()]

def count_syllables_in_word(word: str) -> int:
    """
    Estimate the number of syllables in a word using basic linguistic rules.
    Includes adjustments for silent e, hiatusses, and typical endings.
    """
    word = word.lower().strip(".:;,!?\"'()[]{}*-_")
    if not word:
        return 0
    
    if len(word) <= 3:
        return 1
        
    vowels = "aeiouy"
    count = 0
    prev_char = ""
    
    for char in word:
        if char in vowels:
            if not prev_char or prev_char not in vowels:
                count += 1
            # Hiatus split: consecutive vowels that belong to separate syllables
            elif prev_char + char in ["io", "ia", "eo", "ea", "ua", "uo", "ae", "iu", "ie"]:
                # Exclude simple dipthongs that act as single vowels (like ea in meat, ie in pie)
                # Keep true hiatuses like i-o (biology), i-a (giant), e-o (stereo), u-a (dual), i-e (science, quiet)
                if prev_char + char in ["io", "ia", "eo", "ua", "uo", "ae", "iu", "ie"]:
                    count += 1
        prev_char = char
        
    # Adjust for silent 'e' at the end
    if word.endswith("e") and not word.endswith("le"):
        if count > 1:
            count -= 1
            
    # Adjust for common suffixes
    if word.endswith("ed") and not word.endswith("ted") and not word.endswith("ded"):
        if count > 1:
            count -= 1
            
    if word.endswith("es") and not any(word.endswith(s) for s in ["ces", "ses", "xes", "zes", "ches", "shes"]):
        if count > 1:
            count -= 1
            
    return max(1, count)

def calculate_readability_score(text: str) -> float:
    """
    Calculate the Flesch Reading Ease score.
    Formula: 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
    Score Scale:
      90-100 : Very Easy (5th grade)
      80-89  : Easy
      70-79  : Fairly Easy
      60-69  : Standard
      50-59  : Fairly Difficult
      30-49  : Difficult (College level)
      0-29   : Very Difficult (Academic / Graduate level)
    """
    if not text.strip():
        return 100.0

    words = [w for w in re.findall(r"\b\w+\b", text) if w]
    sentences = split_into_sentences(text)
    
    total_words = len(words)
    total_sentences = len(sentences)
    
    if total_words == 0:
        return 100.0
    if total_sentences == 0:
        total_sentences = 1
        
    total_syllables = sum(count_syllables_in_word(w) for w in words)
    
    # Flesch Reading Ease Formula
    score = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
    
    # Bound the score between 0 and 100
    return max(0.0, min(100.0, round(score, 1)))

def calculate_lexical_diversity(text: str) -> float:
    """
    Calculate Type-Token Ratio (TTR) as a measure of lexical diversity.
    Returns value between 0.0 and 1.0 (higher = more diverse vocabulary).
    """
    words = [w.lower() for w in re.findall(r"\b\w+\b", text) if w]
    if not words:
        return 0.0
    
    unique_words = set(words)
    return round(len(unique_words) / len(words), 3)

def generate_changes_summary(original: str, enhanced: str) -> list[str]:
    """
    Analyze changes between original and enhanced text to produce key insights.
    """
    orig_words = [w for w in re.findall(r"\b\w+\b", original) if w]
    enh_words = [w for w in re.findall(r"\b\w+\b", enhanced) if w]
    
    orig_sents = split_into_sentences(original)
    enh_sents = split_into_sentences(enhanced)
    
    changes = []
    
    if original.strip() != enhanced.strip():
        changes.append("Refactored sentence flow, improved overall grammar structure, and aligned tone with target setting.")
    
    # Readability changes
    orig_read = calculate_readability_score(original)
    enh_read = calculate_readability_score(enhanced)
    
    # Lexical diversity changes
    orig_div = calculate_lexical_diversity(original)
    enh_div = calculate_lexical_diversity(enhanced)
    
    # Word count and sentence structure change
    word_diff = len(enh_words) - len(orig_words)
    
    if len(orig_sents) > 0 and len(enh_sents) > 0:
        orig_avg_len = len(orig_words) / len(orig_sents)
        enh_avg_len = len(enh_words) / len(enh_sents)
        if abs(enh_avg_len - orig_avg_len) > 2:
            changes.append(
                f"Adjusted average sentence length from {orig_avg_len:.1f} to {enh_avg_len:.1f} words to improve flow and structural variety."
            )
            
    if enh_div > orig_div + 0.02:
        changes.append("Enhanced lexical diversity by using richer, more precise academic vocabulary.")
    elif enh_div < orig_div - 0.05:
        changes.append("Simplified vocabulary density to prioritize clarity and readability.")
        
    if enh_read < orig_read - 5:
        changes.append("Elevated style complexity (scholarly tone shift) suitable for peer-reviewed publication.")
    elif enh_read > orig_read + 5:
        changes.append("Improved reading accessibility, reducing convoluted sentences.")
        
    # Check for specific academic substitutions
    informal_academic_pairs = [
        (r"\b(get|got)\b", "acquire / obtain"),
        (r"\b(lots of|a lot of)\b", "numerous / substantial"),
        (r"\b(basically|essentially)\b", "fundamentally"),
        (r"\b(find out)\b", "discover / determine"),
        (r"\b(think about)\b", "consider / contemplate"),
        (r"\b(showed)\b", "demonstrated / indicated"),
        (r"\b(bad)\b", "adverse / unfavorable"),
        (r"\b(good)\b", "beneficial / advantageous"),
        (r"\b(but)\b", "however / yet"),
        (r"\b(so)\b", "therefore / consequently")
    ]
    
    detected_replacements = []
    for pattern, replacement in informal_academic_pairs:
        if re.search(pattern, original.lower()) and not re.search(pattern, enhanced.lower()):
            detected_replacements.append(replacement.split(" / ")[0])
            
    if detected_replacements:
        changes.append(f"Substituted informal words/phrases with scholarly equivalents (e.g., replaced with {', '.join(detected_replacements[:3])}).")
        
    # Default message if no changes occurred
    if not changes:
        changes.append("No significant style modifications required for this text section.")
            
    return changes
