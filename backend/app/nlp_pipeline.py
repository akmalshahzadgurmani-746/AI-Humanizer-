import re
import logging
import random
from app.config import settings
from app.utils import split_into_sentences
from .deep_heuristic import DeepHeuristicRewriter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Optional API imports ────────────────────────────────────────────────────
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not found. Gemini API unavailable.")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai not found. OpenAI API unavailable.")

_nltk_ready = False
_hf_pipeline_obj = None

def _ensure_nltk():
    global _nltk_ready
    if _nltk_ready:
        return True
    try:
        import nltk
        for pkg in ["punkt", "averaged_perceptron_tagger",
                    "punkt_tab", "averaged_perceptron_tagger_eng"]:
            try:
                nltk.download('wordnet', quiet=True)
                nltk.download('omw-1.4', quiet=True)
            except Exception:
                pass
        _nltk_ready = True
        return True
    except Exception as e:
        logger.warning(f"NLTK setup failed: {e}")
        return False

def load_hf_pipeline():
    global _hf_pipeline_obj
    if _hf_pipeline_obj is not None:
        return _hf_pipeline_obj
    if not settings.ENABLE_LOCAL_HF:
        return None
    try:
        from transformers import pipeline as hf_pipeline
        logger.info(f"Loading HuggingFace model: {settings.HF_MODEL_NAME}…")
        _hf_pipeline_obj = hf_pipeline("text2text-generation",
                                       model=settings.HF_MODEL_NAME)
        logger.info("HuggingFace model loaded.")
        return _hf_pipeline_obj
    except Exception as e:
        logger.error(f"HF load failed: {e}")
        settings.ENABLE_LOCAL_HF = False
        return None

# ═══════════════════════════════════════════════════════════════════════════
#  MASTER SYSTEM PROMPT (used for Gemini + OpenAI)
# ═══════════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT_ACADEMIC = """You are an advanced Academic Text Rewriting and Style Enhancement engine.

Your task is to transform the user's input text into a more human-written, academically refined version while preserving the original meaning.

Core Objective:
When the user provides text (paragraphs, essays, or articles), you MUST:
- Rewrite the text completely in a natural human style
- Convert it into formal academic tone
- Improve clarity, fluency, and readability
- Remove repetition and awkward phrasing
- Ensure the output sounds like a well-written research or academic document

Strict Rules:
- NEVER return the original text as output
- NEVER copy sentences directly unless absolutely necessary
- Do NOT simply change a few words — fully restructure sentences
- Maintain same meaning but different structure
- Output must be significantly rephrased
- Keep same number of paragraphs as input (important)
- Do NOT add extra information not present in input

Writing Style Guidelines:
- Use formal academic vocabulary
- Prefer passive voice where appropriate
- Use scholarly transitions like: furthermore, however, therefore, in addition, consequently
- Vary sentence structure (short + long mix)
- Ensure coherence and logical flow

Output Requirements:
- Output ONLY rewritten text
- No explanations, no bullet points, no headings
- Same paragraph structure as input
- Natural human academic writing style

Example:
Input: AI is very useful in education. It helps students learn faster.
Output: Artificial intelligence has become highly beneficial in the field of education, as it enables students to learn and understand concepts more efficiently and at a faster pace.

Always prioritize natural human-like academic rewriting over literal paraphrasing. The result must feel like it was written by a skilled researcher or university-level student."""

SYSTEM_PROMPT_FORMAL = """You are a professional document editor specializing in formal business and institutional writing.

Transform the user's text into a polished, formal, professional style:
- Rewrite fully — do NOT return the original sentences unchanged
- Use professional vocabulary and precise language
- Eliminate colloquialisms, slang, and contractions
- Improve sentence structure and logical flow
- Use transitions: moreover, consequently, in this regard, it should be noted
- Output ONLY the rewritten text. No commentary, headings, or bullet points.
- Maintain the same paragraph structure as the input."""

SYSTEM_PROMPT_SIMPLE = """You are a plain-language editor focused on clarity and accessibility.

Rewrite the user's text to be clear, simple, and easy to read:
- Fully rewrite sentences in plain English — not just word changes
- Break complex ideas into digestible sentences
- Remove jargon; use everyday vocabulary
- Keep sentences concise and direct
- Maintain logical flow and paragraph structure
- Output ONLY the rewritten text. No commentary or headings."""

SYSTEM_PROMPTS = {
    "academic": SYSTEM_PROMPT_ACADEMIC,
    "formal":   SYSTEM_PROMPT_FORMAL,
    "simple":   SYSTEM_PROMPT_SIMPLE,
}

# ═══════════════════════════════════════════════════════════════════════════
#  SYNONYM BANKS (POS-aware)
# ═══════════════════════════════════════════════════════════════════════════
VERB_MAP = {
    "show":"demonstrate","shows":"demonstrates","showed":"demonstrated","showing":"demonstrating",
    "use":"utilize","uses":"utilizes","used":"utilized","using":"utilizing",
    "help":"facilitate","helps":"facilitates","helped":"facilitated","helping":"facilitating",
    "need":"necessitate","needs":"necessitates","needed":"necessitated",
    "get":"obtain","gets":"acquires","got":"acquired","getting":"obtaining",
    "make":"generate","makes":"generates","made":"generated","making":"generating",
    "find":"identify","finds":"identifies","found":"identified","finding":"identifying",
    "see":"observe","sees":"observes","saw":"observed","seeing":"observing",
    "look":"examine","looks":"examines","looked":"examined","looking":"examining",
    "know":"ascertain","knows":"ascertains","knew":"ascertained",
    "think":"postulate","thinks":"postulates","thought":"postulated",
    "start":"commence","starts":"commences","started":"commenced","starting":"commencing",
    "stop":"cease","stops":"ceases","stopped":"ceased",
    "increase":"augment","increases":"augments","increased":"augmented",
    "decrease":"diminish","decreases":"diminishes","decreased":"diminished",
    "improve":"enhance","improves":"enhances","improved":"enhanced",
    "change":"alter","changes":"alters","changed":"altered",
    "affect":"influence","affects":"influences","affected":"influenced",
    "allow":"enable","allows":"enables","allowed":"enabled",
    "cause":"engender","causes":"engenders","caused":"engendered",
    "explain":"elucidate","explains":"elucidates","explained":"elucidated",
    "provide":"furnish","provides":"furnishes","provided":"furnished",
    "suggest":"posit","suggests":"posits","suggested":"posited",
    "test":"assess","tests":"assesses","tested":"assessed",
    "create":"develop","creates":"develops","created":"developed",
    "support":"substantiate","supports":"substantiates","supported":"substantiated",
    "confirm":"corroborate","confirms":"corroborates","confirmed":"corroborated",
    "say":"assert","says":"asserts","said":"asserted","saying":"asserting",
    "tell":"inform","tells":"informs","told":"informed",
    "ask":"inquire","asks":"inquires","asked":"inquired",
    "give":"provide","gives":"provides","gave":"provided",
    "take":"undertake","takes":"undertakes","took":"undertaken",
    "have":"possess","has":"possesses","had":"possessed",
    "do":"conduct","does":"conducts","did":"conducted",
    "go":"proceed","goes":"proceeds","went":"proceeded",
    "come":"emerge","comes":"emerges","came":"emerged",
    "put":"place","puts":"places",
    "keep":"maintain","keeps":"maintains","kept":"maintained",
    "try":"endeavour","tries":"endeavours","tried":"endeavoured",
    "reach":"attain","reaches":"attains","reached":"attained",
    "understand":"comprehend","understands":"comprehends","understood":"comprehended",
    "consider":"contemplate","considers":"contemplates","considered":"contemplated",
    "study":"investigate","studies":"investigates","studied":"investigated",
    "show":"demonstrate","shows":"demonstrates","showed":"demonstrated",
}

ADJ_MAP = {
    "big":"substantial","large":"considerable","huge":"extensive","massive":"significant",
    "small":"minimal","little":"negligible","tiny":"infinitesimal",
    "good":"beneficial","great":"noteworthy","excellent":"exemplary","best":"optimal",
    "bad":"detrimental","poor":"substandard","worst":"most adverse",
    "new":"novel","recent":"contemporary","latest":"most recent",
    "old":"conventional","traditional":"established",
    "important":"paramount","critical":"pivotal","significant":"considerable",
    "useful":"efficacious","helpful":"instrumental","valuable":"indispensable",
    "hard":"arduous","difficult":"challenging","complex":"intricate",
    "easy":"straightforward","simple":"rudimentary","basic":"fundamental",
    "clear":"evident","obvious":"apparent","apparent":"discernible",
    "different":"disparate","various":"diverse","several":"numerous",
    "similar":"analogous","same":"identical","equal":"equivalent",
    "common":"prevalent","widespread":"pervasive","popular":"widely adopted",
    "rare":"infrequent","unusual":"atypical","unique":"singular",
    "real":"empirical","true":"verifiable","actual":"authentic",
    "false":"erroneous","wrong":"inaccurate","incorrect":"erroneous",
    "main":"principal","key":"pivotal","primary":"predominant","major":"substantial",
    "high":"elevated","low":"diminished","strong":"robust","weak":"tenuous",
    "full":"comprehensive","complete":"exhaustive","whole":"entire",
    "possible":"plausible","likely":"probable","certain":"definitive",
    "effective":"efficacious","efficient":"expedient","successful":"productive",
    "direct":"unequivocal","specific":"precise","exact":"meticulous",
}

ADV_MAP = {
    "very":"considerably","really":"substantially","quite":"notably","rather":"relatively",
    "just":"precisely","only":"solely","also":"furthermore","too":"additionally",
    "often":"frequently","sometimes":"occasionally","always":"invariably",
    "never":"by no means","usually":"typically","generally":"broadly",
    "mainly":"primarily","mostly":"predominantly","especially":"particularly",
    "clearly":"evidently","obviously":"manifestly","certainly":"undoubtedly",
    "quickly":"expeditiously","slowly":"gradually","easily":"effortlessly",
    "well":"effectively","badly":"adversely","hard":"rigorously",
    "actually":"in actuality","basically":"fundamentally","essentially":"inherently",
    "probably":"presumably","maybe":"potentially","perhaps":"conceivably",
    "almost":"approximately","nearly":"approximately","about":"approximately",
    "already":"hitherto","still":"nonetheless","yet":"thus far",
    "now":"currently","then":"subsequently","finally":"ultimately",
    "first":"initially","next":"subsequently","later":"thereafter",
}

# ── Phrase-level deep rewrites ─────────────────────────────────────────────
PHRASE_REWRITES = [
    (r"\bin this study[,\s]+we (show|find|examine|explore|investigate|analyze|analyse)",
     r"the present study \1s"),
    (r"\bin this paper[,\s]+we (show|find|examine|explore|investigate|analyze|analyse)",
     r"the present investigation \1s"),
    (r"\bwe found that\b",         "it was determined that"),
    (r"\bwe observed that\b",      "it was observed that"),
    (r"\bwe conclude that\b",      "it can be concluded that"),
    (r"\bwe can conclude\b",       "it can be concluded"),
    (r"\bwe believe that\b",       "it is posited that"),
    (r"\bI believe that\b",        "it is posited that"),
    (r"\bwe think that\b",         "it is posited that"),
    (r"\bwe know that\b",          "it is well established that"),
    (r"\bwe argue that\b",         "it is argued herein that"),
    (r"\bwe propose that\b",       "it is proposed that"),
    (r"\bwe suggest that\b",       "it is suggested that"),
    (r"\bwe show that\b",          "it is demonstrated that"),
    (r"\bthe results show\b",      "the empirical findings indicate"),
    (r"\bthe results indicate\b",  "the results of the analysis indicate"),
    (r"\bthe data shows\b",        "the empirical data indicates"),
    (r"\bthe data show\b",         "the empirical data indicate"),
    (r"\bour results show\b",      "the present findings demonstrate"),
    (r"\bit is important to note that\b",    "crucially,"),
    (r"\bit is worth noting that\b",         "it is noteworthy that"),
    (r"\bit is interesting to note that\b",  "notably,"),
    (r"\bthis is because\b",       "this is attributed to"),
    (r"\bdue to the fact that\b",  "owing to the fact that"),
    (r"\bin order to\b",           "to"),
    (r"\bit is clear that\b",      "it is evident that"),
    (r"\bit can be seen that\b",   "it is apparent that"),
    (r"\ba lot of\b",              "a substantial number of"),
    (r"\blots of\b",               "numerous"),
    (r"\bkind of\b",               "somewhat"),
    (r"\bsort of\b",               "to some extent"),
    (r"\bfind out\b",              "determine"),
    (r"\blook at\b",               "examine"),
    (r"\bset up\b",                "establish"),
    (r"\bpoint of view\b",         "perspective"),
    (r"\bso far\b",                "hitherto"),
    (r"\bmake sure\b",             "ensure"),
    (r"\bdeal with\b",             "address"),
    (r"\bgo on\b",                 "continue"),
    (r"\bput in\b",                "incorporate"),
    (r"\bkeep on\b",               "persist in"),
    (r"\ba number of\b",           "several"),
    (r"\ba wide range of\b",       "a diverse array of"),
    (r"\bin terms of\b",           "with respect to"),
    (r"\bwith regard to\b",        "concerning"),
    (r"\bas a result of\b",        "as a consequence of"),
    (r"\bfor example\b",           "for instance"),
    (r"\bfor instance\b",          "as an illustration"),
    (r"\bin conclusion\b",         "in summation"),
    (r"\bto sum up\b",             "in conclusion"),
    (r"\bon the other hand\b",     "conversely"),
    (r"\bat the same time\b",      "simultaneously"),
    (r"\bin addition to\b",        "beyond"),
    (r"\bmore and more\b",         "increasingly"),
    (r"\bgetting better\b",        "improving progressively"),
    (r"\bgets worse\b",            "deteriorates"),
    (r"\ball in all\b",            "on balance"),
    (r"\bthings like\b",           "such phenomena as"),
    (r"\bpeople who\b",            "individuals who"),
    (r"\bkids\b",                  "children"),
    (r"\bguy\b",                   "individual"),
    (r"\bguys\b",                  "individuals"),
    (r"\bstuff\b",                 "material"),
    (r"\bthings\b",                "aspects"),
    (r"\ba bit\b",                 "somewhat"),
    (r"\band so\b",                "consequently"),
]

CONTRACTIONS = {
    r"\bdon't\b":    "do not",    r"\bcan't\b":   "cannot",
    r"\bwon't\b":    "will not",  r"\bisn't\b":   "is not",
    r"\baren't\b":   "are not",   r"\bwasn't\b":  "was not",
    r"\bweren't\b":  "were not",  r"\bhaven't\b": "have not",
    r"\bhasn't\b":   "has not",   r"\bhadn't\b":  "had not",
    r"\bit's\b":     "it is",     r"\bthey're\b": "they are",
    r"\bwe're\b":    "we are",    r"\byou're\b":  "you are",
    r"\bI'm\b":      "I am",      r"\bshouldn't\b":"should not",
    r"\bwouldn't\b": "would not", r"\bcouldn't\b":"could not",
    r"\bthat's\b":   "that is",   r"\bwhat's\b":  "what is",
    r"\bthere's\b":  "there is",  r"\bhere's\b":  "here is",
    r"\bwho's\b":    "who is",    r"\bhe's\b":    "he is",
    r"\bshe's\b":    "she is",    r"\bthey've\b": "they have",
    r"\bwe've\b":    "we have",   r"\byou've\b":  "you have",
    r"\bI've\b":     "I have",    r"\bI'd\b":     "I would",
    r"\bwe'd\b":     "we would",  r"\bthey'd\b":  "they would",
}

CONNECTOR_REPLACEMENTS = {
    r"^Also,\s+":    "Additionally, ",
    r"^And\s+":      "Furthermore, ",
    r"^But\s+":      "However, ",
    r"^Plus,\s+":    "In addition, ",
    r"^So\s+":       "Consequently, ",
    r"^Anyway,\s+":  "Nevertheless, ",
    r"^Then\s+":     "Subsequently, ",
    r"^Next\s+":     "Furthermore, ",
    r"^Finally\s+":  "Ultimately, ",
    r"^Therefore\s+":"Therefore, ",
    r"^Thus\s+":     "Thus, ",
    r"^Hence\s+":    "Hence, ",
}

# Scholarly sentence-starter injections (alternating sentences)
ACADEMIC_STARTERS = [
    "Notably, {}",
    "Furthermore, {}",
    "In this regard, {}",
    "Evidently, {}",
    "Accordingly, {}",
    "It is worth emphasising that {}",
    "Upon closer examination, {}",
    "From a scholarly perspective, {}",
    "The analysis reveals that {}",
    "It is pertinent to acknowledge that {}",
    "As demonstrated by the evidence, {}",
    "In light of the above, {}",
]

FORMAL_STARTERS = [
    "It should be noted that {}",
    "In this context, {}",
    "As indicated, {}",
    "Accordingly, {}",
    "It is apparent that {}",
]

ALREADY_FORMAL = (
    "notably","furthermore","additionally","however","consequently",
    "accordingly","evidently","it is","it was","the present","the empirical",
    "crucially","in this","upon","as demonstrated","from a","the analysis",
    "it should","in addition","with reference","as indicated","moreover",
    "nevertheless","therefore","thus","hence","in conclusion","in summation",
    "conversely","simultaneously","the results","this study","this paper",
    "the findings","in the","this phenomenon","it can","it has",
)


class DeepHeuristicRewriter:
    """
    Production-quality offline rewriting engine.

    Per-sentence pipeline:
      1. Expand contractions
      2. Deep phrase-level substitutions (clause restructuring)
      3. Connector / sentence-starter normalisation
      4. POS-tag tokens → swap verbs / adj / adv with scholarly synonyms
      5. Inject academic opening phrases on alternating sentences
      6. Passive voice injection for first-person active constructions
    """

    @classmethod
    def rewrite(cls, text: str, mode: str) -> str:
        sentences = split_into_sentences(text)
        nltk_ok = _ensure_nltk()
        output = []

        for idx, sent in enumerate(sentences):
            if len(sent.strip()) < 4:
                output.append(sent)
                continue

            s = cls._expand_contractions(sent)
            s = cls._phrase_rewrite(s)
            s = cls._connector_fix(s)

            if nltk_ok:
                s = cls._pos_elevate(s, mode)
                s = cls._wordnet_synonym_replace(s)
                s = cls._passive_voice(s)

            if mode in ("academic", "formal"):
                s = cls._inject_starter(s, idx, mode)

            # Ensure sentence starts with capital
            s = s.strip()
            if s and s[0].islower():
                s = s[0].upper() + s[1:]

            output.append(s)

        return " ".join(output)

    # ── Step helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _expand_contractions(text: str) -> str:
        for pat, rep in CONTRACTIONS.items():
            text = re.sub(pat, rep, text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def _phrase_rewrite(text: str) -> str:
        for pat, rep in PHRASE_REWRITES:
            text = re.sub(pat, rep, text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def _connector_fix(text: str) -> str:
        for pat, rep in CONNECTOR_REPLACEMENTS.items():
            text = re.sub(pat, rep, text)
        return text

    @staticmethod
    def _pos_elevate(text: str, mode: str) -> str:
        """
        POS-tag every token and lift verbs, adjectives, and adverbs
        to scholarly equivalents — works on ANY English sentence.
        """
        try:
            import nltk
            tokens = nltk.word_tokenize(text)
            tagged  = nltk.pos_tag(tokens)
        except Exception:
            return text

        out = []
        for word, tag in tagged:
            low = word.lower()
            repl = word

            if tag.startswith("VB") and low in VERB_MAP:
                syn = VERB_MAP[low]
                repl = syn[0].upper() + syn[1:] if word[0].isupper() else syn

            elif tag.startswith("JJ") and mode != "simple" and low in ADJ_MAP:
                syn = ADJ_MAP[low]
                repl = syn[0].upper() + syn[1:] if word[0].isupper() else syn

            elif tag.startswith("RB") and mode != "simple" and low in ADV_MAP:
                syn = ADV_MAP[low]
                repl = syn[0].upper() + syn[1:] if word[0].isupper() else syn

            out.append(repl)

        # Detokenise — fix spaces before punctuation
        joined = " ".join(out)
        joined = re.sub(r"\s+([.,;:!?)\]'}])", r"\1", joined)
        joined = re.sub(r"([\[({'])\s+",        r"\1",  joined)
        joined = re.sub(r"\s+n't\b",             "n't",  joined)
        return joined

    @staticmethod
    def _inject_starter(sent: str, idx: int, mode: str) -> str:
        """
        Inject an academic / formal opening phrase on every other sentence
        that does not already start with a scholarly phrase.
        """
        first_word = sent.split()[0].lower().rstrip(",:;") if sent.split() else ""
        is_formal  = any(sent.lower().startswith(p) for p in ALREADY_FORMAL)
        if is_formal or idx % 2 != 1:
            return sent

        pool   = ACADEMIC_STARTERS if mode == "academic" else FORMAL_STARTERS
        tmpl   = random.choice(pool)
        # Lowercase the body when injecting a starter
        body   = sent[0].lower() + sent[1:] if sent and sent[0].isupper() else sent
        return tmpl.format(body)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════
class NLPEngine:
    """
    Cascading rewrite engine:
      Gemini API → OpenAI API → HuggingFace local → DeepHeuristicRewriter (NLTK)
    """

    @classmethod
    def rewrite(cls, text: str, mode: str = "academic") -> tuple[str, str]:
        mode = mode.lower()
        if mode not in ("academic", "formal", "simple"):
            mode = "academic"
        text = text.strip()
        if not text:
            return "", "None"

        # Helper to verify that each paragraph is fully rewritten (no verbatim sentences)
        def _paragraph_rewritten(orig: str, rew: str) -> bool:
            orig_sents = split_into_sentences(orig)
            rew_sents = split_into_sentences(rew)
            if not rew_sents:
                return False
            # If sentence count differs, assume rewrite occurred
            if len(orig_sents) != len(rew_sents):
                return True
            # Ensure no sentence is identical (case‑insensitive)
            for o, r in zip(orig_sents, rew_sents):
                if o.strip().lower() == r.strip().lower():
                    return False
            return True

        # Engine candidates in priority order
        candidates = [
            ("gemini", lambda t, m: cls._gemini(t, m) if settings.GEMINI_API_KEY and GEMINI_AVAILABLE else None),
            ("openai", lambda t, m: cls._openai(t, m) if settings.OPENAI_API_KEY and OPENAI_AVAILABLE else None),
            ("hf", lambda t, m: cls._hf(t, m, load_hf_pipeline()) if settings.ENABLE_LOCAL_HF and load_hf_pipeline() else None),
            ("heuristic", lambda t, m: (DeepHeuristicRewriter.rewrite(t, m), "Deep Heuristic + NLTK (Offline)")),
        ]

        for name, fn in candidates:
            if fn is None:
                continue
            try:
                result = fn(text, mode)
                if isinstance(result, tuple) and len(result) == 2:
                    rewritten, engine_label = result
                else:
                    rewritten = result
                    engine_label = name.capitalize() if name != "heuristic" else "Deep Heuristic + NLTK (Offline)"
                if rewritten and _paragraph_rewritten(text, rewritten):
                    return rewritten, engine_label
            except Exception as e:
                logger.error(f"{name.capitalize()} engine error: {e}")
                continue

        # Final fallback using heuristic (guaranteed change)
        fallback = DeepHeuristicRewriter.rewrite(text, mode)
        return fallback, "Deep Heuristic + NLTK (Offline)"

    # ── provider implementations ───────────────────────────────────────────

    @classmethod
    def _gemini(cls, text: str, mode: str) -> str:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = SYSTEM_PROMPTS[mode] + f"\n\n---\nText to rewrite:\n{text}"
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
        raise ValueError("Empty Gemini response")

    @classmethod
    def _openai(cls, text: str, mode: str) -> str:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",  "content": SYSTEM_PROMPTS[mode]},
                {"role": "user",    "content": f"Rewrite this text:\n\n{text}"},
            ],
            temperature=0.4,
        )
        result = resp.choices[0].message.content
        if result:
            return result.strip()
        raise ValueError("Empty OpenAI response")

    @classmethod
    def _hf(cls, text: str, mode: str, pipe) -> str:
        sentences = split_into_sentences(text)
        prefix_map = {
            "academic": "paraphrase for academic writing: ",
            "formal":   "rewrite in formal style: ",
            "simple":   "simplify and clarify: ",
        }
        prefix = prefix_map.get(mode, "paraphrase: ")
        out = []
        for sent in sentences:
            if len(sent.strip()) < 5:
                out.append(sent)
                continue
            result = pipe(prefix + sent, max_length=200, num_return_sequences=1)
            gen = result[0]["generated_text"].strip()
            # Fall back to deep heuristic if model echoes the input
            if not gen or gen.lower().strip() == sent.lower().strip():
                gen = DeepHeuristicRewriter.rewrite(sent, mode)
            out.append(gen)
        return " ".join(out)
