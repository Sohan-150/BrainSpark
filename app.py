import streamlit as st
import random
import json
import os

# ══════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════

st.set_page_config(
    page_title="BrainSpark ⚡",
    page_icon="⚡",
    layout="centered",
)

st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    div[data-testid="metric-container"] { text-align: center; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  HIGH SCORE PERSISTENCE
# ══════════════════════════════════════════════════════

HS_FILE = "highscores.json"

def load_highscores():
    """Load high scores from file, or return defaults if file doesn't exist."""
    if os.path.exists(HS_FILE):
        with open(HS_FILE) as f:
            return json.load(f)
    return {"math": 0, "english": 0}

def save_highscores():
    """Save the current high scores to a JSON file."""
    with open(HS_FILE, "w") as f:
        json.dump(st.session_state.hs, f)


# ══════════════════════════════════════════════════════
#  SESSION STATE INITIALISATION
# ══════════════════════════════════════════════════════

def init_session():
    """Set default values for all session state variables on first load."""
    defaults = {
        "screen":     "menu",   # which screen to show: "menu" | "game" | "gameover"
        "mode":       None,     # which game mode: "math" | "english"
        "score":      0,
        "lives":      3,
        "difficulty": 1,        # 1 (Grade 3) → 5 (Grade 7)
        "q":          None,     # current question dict
        "answered":   False,
        "correct":    None,
        "feedback":   "",
        "eng_idx":    0,        # cycles through vocab / grammar / sentence
        "used_qs":    set(),    # question indices already seen this session
        "hs":         load_highscores(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()


# ══════════════════════════════════════════════════════
#  NAVIGATION HELPERS
# ══════════════════════════════════════════════════════

def go_menu():
    """Return to the main menu and clear the current question."""
    st.session_state.screen = "menu"
    st.session_state.q = None

def start_game(mode):
    """Reset all game state and begin a new session."""
    st.session_state.update({
        "screen":     "game",
        "mode":       mode,
        "score":      0,
        "lives":      3,
        "difficulty": 1,
        "q":          None,
        "answered":   False,
        "correct":    None,
        "feedback":   "",
        "eng_idx":    0,
        "used_qs":    set(),
    })

def calc_difficulty(score):
    """Increase difficulty every 3 correct answers, capped at level 5."""
    return min(5, score // 3 + 1)


# ══════════════════════════════════════════════════════
#  MATH QUESTION GENERATOR
# ══════════════════════════════════════════════════════

def generate_math_question(d):
    """
    Generate a random math question at difficulty d (1–5).
    Returns a dict with 'text' (the question string) and 'answer' (the number).

    Difficulty levels:
      1 → Grade 3–4: addition/subtraction within 100, times tables
      2 → Grade 4–5: 3-digit arithmetic, times tables up to 12
      3 → Grade 5:   multi-digit multiplication, long division, multi-step
      4 → Grade 6:   decimals, basic percentages
      5 → Grade 7:   order of operations, algebra, harder percentages
    """

    def r(a, b):
        """Shorthand for random.randint."""
        return random.randint(a, b)

    if d == 1:
        t = r(0, 2)
        if t == 0:
            x, y = r(10, 80), r(5, 20)
            return {"text": f"{x} + {y} = ?", "answer": x + y}
        elif t == 1:
            x = r(20, 99)
            y = r(5, x - 1)
            return {"text": f"{x} − {y} = ?", "answer": x - y}
        else:
            x, y = r(2, 9), r(2, 9)
            return {"text": f"{x} × {y} = ?", "answer": x * y}

    elif d == 2:
        t = r(0, 3)
        if t == 0:
            x, y = r(100, 700), r(50, 200)
            return {"text": f"{x} + {y} = ?", "answer": x + y}
        elif t == 1:
            x = r(200, 999)
            y = r(50, x - 1)
            return {"text": f"{x} − {y} = ?", "answer": x - y}
        elif t == 2:
            x, y = r(4, 12), r(4, 12)
            return {"text": f"{x} × {y} = ?", "answer": x * y}
        else:
            x, y = r(2, 9), r(2, 9)
            return {"text": f"{x * y} ÷ {x} = ?", "answer": y}

    elif d == 3:
        t = r(0, 2)
        if t == 0:
            x, y = r(12, 49), r(11, 29)
            return {"text": f"{x} × {y} = ?", "answer": x * y}
        elif t == 1:
            x = r(3, 9)
            mult = r(10, 19)
            return {"text": f"{x * mult} ÷ {x} = ?", "answer": mult}
        else:
            x, y, z = r(100, 400), r(100, 400), r(10, 99)
            return {"text": f"({x} + {y}) − {z} = ?", "answer": x + y - z}

    elif d == 4:
        t = r(0, 1)
        if t == 0:
            a = round(random.uniform(1.0, 9.9), 1)
            b = round(random.uniform(1.0, 9.9), 1)
            return {"text": f"{a} + {b} = ?", "answer": round(a + b, 1)}
        else:
            pct = random.choice([10, 20, 25, 50])
            base = random.choice([20, 40, 60, 80, 100, 200])
            return {"text": f"{pct}% of {base} = ?", "answer": pct * base // 100}

    else:  # d == 5
        t = r(0, 2)
        if t == 0:
            coeff = r(2, 9)
            rhs = coeff * r(2, 9)
            return {"text": f"If {coeff} × n = {rhs}, what is n?", "answer": rhs // coeff}
        elif t == 1:
            a, b, c = r(2, 8), r(2, 8), r(2, 8)
            return {
                "text": f"{a} + {b} × {c} = ?  (use order of operations)",
                "answer": a + b * c,
            }
        else:
            pct = random.choice([15, 30, 35, 40, 60, 75])
            base = random.choice([20, 40, 60, 80, 120, 200])
            return {"text": f"{pct}% of {base} = ?", "answer": round(pct * base / 100)}


# ══════════════════════════════════════════════════════
#  ENGLISH QUESTION BANKS
# ══════════════════════════════════════════════════════

# Each VOCAB entry: (difficulty, word, [options], correct_index, explanation)
VOCAB = [
    (1, "ancient",      ["Very old", "Very small", "Very fast", "Very bright"],           0, "Ancient means extremely old, like ancient ruins or civilisations."),
    (1, "enormous",     ["Very large", "Very quiet", "Very cold", "Very slow"],            0, "Enormous means extremely large or huge."),
    (1, "timid",        ["Shy and nervous", "Brave and bold", "Loud and funny", "Tired"],  0, "Timid means lacking confidence — shy and easily frightened."),
    (1, "gleam",        ["To shine brightly", "To hide away", "To fall down", "To shout"], 0, "Gleam means to shine or glow with a soft light."),
    (1, "swift",        ["Moving very fast", "Moving very slowly", "Completely still", "Very tall"], 0, "Swift means moving with great speed."),
    (2, "compassion",   ["Caring deeply for others", "Fear of heights", "Love of music", "Dislike of noise"], 0, "Compassion is sympathy and concern for others' suffering."),
    (2, "diligent",     ["Hardworking and careful", "Lazy and careless", "Confused", "Very angry"], 0, "Diligent means showing steady, careful effort."),
    (2, "vibrant",      ["Bright and lively", "Dull and lifeless", "Cold and distant", "Weak"], 0, "Vibrant means full of energy; bright and striking."),
    (2, "scarce",       ["Rare; not enough of it", "Plentiful and available", "Very expensive", "Recently made"], 0, "Scarce means in short supply."),
    (2, "cunning",      ["Cleverly deceptive", "Completely honest", "Very kind-hearted", "Loud and clumsy"], 0, "Cunning means clever in a crafty or deceptive way."),
    (3, "ambiguous",    ["Open to more than one meaning", "Perfectly clear", "Completely boring", "Very important"], 0, "Ambiguous means having more than one possible interpretation."),
    (3, "persevere",    ["Keep going despite difficulty", "Give up easily", "Sleep deeply", "Move quickly"], 0, "Persevere means to continue steadfastly despite obstacles."),
    (3, "eloquent",     ["Expressing ideas clearly and well", "Speaking very rudely", "Being very quiet", "Being extremely tall"], 0, "Eloquent means using language persuasively and clearly."),
    (3, "futile",       ["Having no useful result", "Very productive", "Full of meaning", "Quite enjoyable"], 0, "Futile means incapable of producing any result; pointless."),
    (4, "obsolete",     ["No longer used or needed", "Newly invented", "Very popular", "Extremely useful"], 0, "Obsolete means no longer produced or used; out of date."),
    (4, "meticulous",   ["Very careful and precise", "Careless and sloppy", "Loud and disruptive", "Shy"], 0, "Meticulous means showing great attention to detail."),
    (4, "benevolent",   ["Kind and generous", "Cruel and harsh", "Completely indifferent", "Very boastful"], 0, "Benevolent means well meaning and kindly; generous."),
    (4, "apprehensive", ["Anxious about what may happen", "Very happy", "Completely bored", "Quite hungry"], 0, "Apprehensive means worried about something in the future."),
    (5, "ephemeral",    ["Lasting only a short time", "Lasting forever", "Very expensive", "Extremely large"], 0, "Ephemeral means lasting for a very short time; transitory."),
    (5, "pragmatic",    ["Practical and realistic", "Dreamy and idealistic", "Emotional and impulsive", "Reckless"], 0, "Pragmatic means dealing with things sensibly and realistically."),
    (5, "tenacious",    ["Very determined; not giving up", "Quick to give up", "Easily distracted", "Very generous"], 0, "Tenacious means very determined; not giving up easily."),
]

# Each GRAMMAR entry: (difficulty, sentence, is_correct, explanation)
GRAMMAR = [
    (1, "She don't like apples.",                    False, 'Should be "doesn\'t" — use doesn\'t with she/he/it.'),
    (1, "They are playing in the park.",             True,  '"They are" is the correct subject-verb agreement.'),
    (1, "He goed to school yesterday.",              False, '"Went" is the correct past tense of "go".'),
    (1, "The dog runs very fast.",                   True,  '"Runs" correctly agrees with the singular subject "The dog".'),
    (1, "The cats is sleeping.",                     False, '"Cats" is plural, so use "are": The cats are sleeping.'),
    (2, "Me and my friend went to the store.",       False, 'Should be "My friend and I went…" — use "I" as the subject.'),
    (2, "He swam across the river quickly.",         True,  '"Swam" is the proper past tense of "swim".'),
    (2, "She has less friends than her brother.",    False, 'Use "fewer" for countable nouns: fewer friends.'),
    (2, "The birds flew south for winter.",          True,  '"Flew" is the past tense of "fly".'),
    (2, "I seen that film already.",                 False, 'Should be "I have seen" or "I saw" — "seen" needs a helper verb.'),
    (3, "Between you and I, this is a secret.",      False, '"Between" takes object pronouns: "Between you and me."'),
    (3, "Whom did you call yesterday?",              True,  '"Whom" is the object of "call" — correct.'),
    (3, "I should of studied harder.",               False, 'Should be "should have" — "of" sounds like "have" but is wrong.'),
    (3, "She speaks more quietly than her sister.",  True,  '"Quietly" is the correct adverb form here.'),
    (4, "The number of students are increasing.",    False, '"The number" is singular: "The number of students is increasing."'),
    (4, "Neither the teacher nor the students were ready.", True, 'The verb agrees with the closer noun "students" — correct.'),
    (4, "He laid the book on the table.",            True,  '"Laid" is the past tense of "lay" (to place something).'),
    (4, "Irregardless of the weather, we will play.", False, '"Irregardless" is not standard. Use "regardless".'),
    (5, "Whomever finishes first wins the prize.",   False, '"Whoever" is needed — it is the subject of "finishes".'),
    (5, "She is one of the students who excel in math.", True, 'The clause refers to "students" (plural), so "excel" is right.'),
    (5, "The reason is because I was tired.",        False, '"The reason is that…" — "because" is redundant after "reason is".'),
    (5, "The data are being analysed by scientists.", True, '"Data" is technically plural, so "are" is formally correct.'),
]

# Each SENTENCES entry: (difficulty, sentence, type, explanation)
# type is one of: "simple", "compound", "complex"
SENTENCES = [
    (1, "The cat sat on the mat.",                       "simple",   "One subject and one predicate — no dependent clauses."),
    (1, "She studied hard, and she passed the test.",    "compound", 'Two independent clauses joined by "and".'),
    (1, "The dog barked loudly.",                        "simple",   "One subject and one verb — clean and direct."),
    (1, "I like reading because it is fun.",             "complex",  '"Because it is fun" is a dependent clause.'),
    (2, "I went to the store, but it was closed.",       "compound", 'Two independent clauses joined by "but".'),
    (2, "Because it was raining, we stayed inside.",     "complex",  '"Because it was raining" is a dependent clause.'),
    (2, "My sister bakes amazing cakes.",                "simple",   "One subject, one predicate."),
    (2, "Tom likes pizza, and Jerry likes pasta.",       "compound", 'Two independent clauses joined by "and".'),
    (3, "Although she was tired, she finished her homework.", "complex", '"Although she was tired" is a dependent clause.'),
    (3, "The teacher who helped me is very kind.",       "complex",  '"Who helped me" is a relative (dependent) clause.'),
    (3, "We went to the park after school.",             "simple",   '"After school" is a phrase, not a full clause.'),
    (3, "It rained, so the match was cancelled.",        "compound", 'Two independent clauses joined by "so".'),
    (4, "I will go if I finish my work.",                "complex",  '"If I finish my work" is a conditional dependent clause.'),
    (4, "She reads books that challenge her thinking.",  "complex",  '"That challenge her thinking" is a relative clause.'),
    (4, "My brother and I cleaned the house and cooked dinner.", "simple", "Compound subject and predicate, but still one clause."),
    (4, "The film was long, but it was entertaining.",   "compound", 'Two independent clauses linked by "but".'),
    (5, "While the team practised, the coach observed their technique.", "complex", '"While the team practised" is a dependent adverbial clause.'),
    (5, "The scientist discovered a new element and published her findings.", "simple", "One subject and a compound predicate."),
    (5, "He laughed, she smiled, and they both agreed.", "compound", "Three independent clauses joined by commas and 'and'."),
    (5, "Students who work hard often succeed in whatever they attempt.", "complex", 'Contains two dependent clauses: "who work hard" and "whatever they attempt".'),
]

ENG_TYPES = ["vocab", "grammar", "sentence"]


# ══════════════════════════════════════════════════════
#  ENGLISH QUESTION HELPERS
# ══════════════════════════════════════════════════════

def pick_question(bank, d, used):
    """
    Pick an unused question from bank at difficulty d.
    If all questions at that level are used, tries nearby levels.
    If everything is used, clears the used set and starts over.
    Returns (index, question_tuple).
    """
    for delta in range(5):
        for direction in [0, -1, 1]:
            target = d + direction * delta
            if not (1 <= target <= 5):
                continue
            candidates = [
                (i, q) for i, q in enumerate(bank)
                if q[0] == target and i not in used
            ]
            if candidates:
                return random.choice(candidates)

    # All questions exhausted — reset and pick fresh
    used.clear()
    candidates = [(i, q) for i, q in enumerate(bank) if q[0] == d]
    return random.choice(candidates) if candidates else (0, bank[0])


def shuffle_options(opts, correct_idx):
    """
    Shuffle the answer options randomly.
    Returns the new list of options and the new index of the correct answer.
    """
    indexed = list(enumerate(opts))
    random.shuffle(indexed)
    new_opts = [opt for _, opt in indexed]
    new_correct = next(
        new_i for new_i, (old_i, _) in enumerate(indexed) if old_i == correct_idx
    )
    return new_opts, new_correct


def generate_eng_question(d, eng_idx, used):
    """
    Generate an English question, rotating between vocab / grammar / sentence.
    Returns a question dict with keys: type, text, opts, answer, feedback.
    """
    qtype = ENG_TYPES[eng_idx % 3]

    if qtype == "vocab":
        idx, q = pick_question(VOCAB, d, used)
        used.add(idx)
        _, word, opts, ans, exp = q
        shuffled_opts, new_ans = shuffle_options(opts, ans)
        return {
            "type":     "vocab",
            "text":     f'What does <strong>"{word}"</strong> mean?',
            "opts":     shuffled_opts,
            "answer":   new_ans,
            "feedback": exp,
        }

    elif qtype == "grammar":
        idx, q = pick_question(GRAMMAR, d, used)
        used.add(idx)
        _, sent, is_correct, exp = q
        return {
            "type":     "grammar",
            "text":     f'Is this sentence grammatically <strong>correct</strong> or <strong>incorrect</strong>?<br><br><em>"{sent}"</em>',
            "opts":     ["✓ Correct", "✗ Incorrect"],
            "answer":   0 if is_correct else 1,
            "feedback": exp,
        }

    else:  # sentence classification
        idx, q = pick_question(SENTENCES, d, used)
        used.add(idx)
        _, sent, stype, exp = q
        type_map = {"simple": 0, "compound": 1, "complex": 2}
        return {
            "type":     "sentence",
            "text":     f'What type of sentence is this?<br><br><em>"{sent}"</em>',
            "opts":     ["Simple", "Compound", "Complex"],
            "answer":   type_map[stype],
            "feedback": exp,
        }


# ══════════════════════════════════════════════════════
#  ANSWER HANDLERS
# ══════════════════════════════════════════════════════

def handle_answer(chosen):
    """Process a multiple-choice answer and update score / lives."""
    s = st.session_state
    correct = (chosen == s.q["answer"])
    s.answered = True
    s.correct = correct

    if correct:
        s.score += 1
        s.feedback = "✅ Correct!  " + s.q["feedback"]
    else:
        s.lives -= 1
        correct_label = s.q["opts"][s.q["answer"]]
        s.feedback = (
            f'❌ Not quite. The answer was **{correct_label}**.\n\n'
            f'{s.q["feedback"]}'
        )


def handle_math_answer(value):
    """Process a numeric math answer and update score / lives."""
    s = st.session_state
    correct = abs(float(value) - float(s.q["answer"])) < 0.01
    s.answered = True
    s.correct = correct

    if correct:
        s.score += 1
        s.feedback = f"✅ Correct! The answer is **{s.q['answer']}**."
    else:
        s.lives -= 1
        s.feedback = f"❌ Not quite. The correct answer was **{s.q['answer']}**."


def next_question():
    """Advance to the next question, or trigger game over if no lives remain."""
    s = st.session_state
    if s.lives <= 0:
        # Check and save high score before leaving
        if s.score > s.hs[s.mode]:
            s.hs[s.mode] = s.score
            save_highscores()
        s.screen = "gameover"
    else:
        # Reset question state for the next question
        s.q        = None
        s.answered = False
        s.correct  = None
        s.feedback = ""


# ══════════════════════════════════════════════════════
#  SCREEN: MENU
# ══════════════════════════════════════════════════════

def show_menu():
    s = st.session_state

    st.markdown("<h1 style='text-align:center'>⚡ BrainSpark</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:gray;'>Math & English · Grades 3–7</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='margin-bottom:0'>🔢 Math</h3>", unsafe_allow_html=True)
        st.caption("Mental arithmetic · Adaptive difficulty")
        st.metric("High Score", s.hs["math"])
        if st.button("Play Math", use_container_width=True, type="primary"):
            start_game("math")
            st.rerun()
        if st.button("Reset Math Score", use_container_width=True, key="reset_math"):
            s.hs["math"] = 0
            save_highscores()
            st.rerun()

    with col2:
        st.markdown("<h3 style='margin-bottom:0'>📖 English</h3>", unsafe_allow_html=True)
        st.caption("Vocab · Grammar · Sentences")
        st.metric("High Score", s.hs["english"])
        if st.button("Play English", use_container_width=True, type="primary"):
            start_game("english")
            st.rerun()
        if st.button("Reset English Score", use_container_width=True, key="reset_english"):
            s.hs["english"] = 0
            save_highscores()
            st.rerun()


# ══════════════════════════════════════════════════════
#  SCREEN: GAME
# ══════════════════════════════════════════════════════

def show_game():
    s = st.session_state

    # ── Generate a new question if we don't have one ──
    if s.q is None:
        s.difficulty = calc_difficulty(s.score)
        if s.mode == "math":
            s.q = generate_math_question(s.difficulty)
        else:
            s.q = generate_eng_question(s.difficulty, s.eng_idx, s.used_qs)
            s.eng_idx += 1

    # ── HUD row ──
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("← Menu", use_container_width=True):
            go_menu()
            st.rerun()
    with col2:
        st.metric("Score", s.score)
    with col3:
        st.metric("Best", s.hs[s.mode])
    with col4:
        hearts = "❤️" * s.lives + "🖤" * (3 - s.lives)
        st.markdown(
            f"<p style='font-size:1.4rem; text-align:center; margin-top:18px'>{hearts}</p>",
            unsafe_allow_html=True,
        )

    # ── Difficulty bar ──
    grade = s.difficulty + 2  # maps 1→Grade 3, 5→Grade 7
    diff_pct = (s.difficulty - 1) / 4
    st.progress(diff_pct, text=f"Difficulty: Grade {grade}")

    # ── English question-type badge ──
    if s.mode == "english":
        type_labels = {
            "vocab":    "📚 Vocabulary",
            "grammar":  "✏️ Grammar Check",
            "sentence": "🔤 Sentence Type",
        }
        st.caption(type_labels.get(s.q.get("type", "vocab"), ""))

    # ── Question text ──
    st.markdown(
        f"<div style='font-size:1.25rem; font-weight:700; margin-bottom:0; line-height:1.5'>{s.q['text']}</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Answer area ──
    if not s.answered:

        if s.mode == "math":
            # Numeric input for math
            val = st.number_input("Your answer:", step=0.1, format="%.4g", key="math_input")
            if st.button("Submit ✓", use_container_width=True, type="primary"):
                handle_math_answer(val)
                st.rerun()

        elif s.q["type"] == "grammar":
            # Two side-by-side buttons for Correct / Incorrect
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✓ Correct", use_container_width=True):
                    handle_answer(0)
                    st.rerun()
            with c2:
                if st.button("✗ Incorrect", use_container_width=True):
                    handle_answer(1)
                    st.rerun()

        else:
            # Multiple-choice buttons (vocab & sentence type)
            for i, opt in enumerate(s.q["opts"]):
                if st.button(opt, use_container_width=True, key=f"opt_{i}"):
                    handle_answer(i)
                    st.rerun()

    # ── Feedback (shown after answering) ──
    else:
        if s.correct:
            st.success(s.feedback)
        else:
            st.error(s.feedback)

        if s.lives <= 0:
            st.warning("💀 No lives left — game over!")
            if st.button("See Results →", use_container_width=True, type="primary"):
                next_question()
                st.rerun()
        else:
            if st.button("Next Question →", use_container_width=True, type="primary"):
                next_question()
                st.rerun()


# ══════════════════════════════════════════════════════
#  SCREEN: GAME OVER
# ══════════════════════════════════════════════════════

def show_gameover():
    s = st.session_state

    st.markdown("<h1 style='text-align:center'>🎮 Game Over!</h1>", unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Your Score", s.score)
    with col2:
        st.metric("High Score", s.hs[s.mode])

    # Celebrate a new high score
    if s.score > 0 and s.score == s.hs[s.mode]:
        st.balloons()
        st.success("🏆 New High Score!")

    # Personalised message based on score
    if s.score == 0:
        st.info("Don't worry — every expert was once a beginner. Try again!")
    elif s.score < 5:
        st.info("Good effort! Keep practising and you'll go further each time.")
    elif s.score < 10:
        st.info("Well done! Solid performance — can you beat your high score?")
    else:
        st.success("🔥 Brilliant! Outstanding score!")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Play Again", use_container_width=True, type="primary"):
            start_game(s.mode)
            st.rerun()
    with col2:
        if st.button("← Main Menu", use_container_width=True):
            go_menu()
            st.rerun()


# ══════════════════════════════════════════════════════
#  MAIN ROUTER
# ══════════════════════════════════════════════════════

screen = st.session_state.screen

if screen == "menu":
    show_menu()
elif screen == "game":
    show_game()
elif screen == "gameover":
    show_gameover()
