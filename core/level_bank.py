
import random

TOTAL_LEVELS = 200
DOMAINS = ["memory", "attention", "language", "sequencing", "reasoning", "visual"]
DOMAIN_LABELS = {
    "memory": "Memory", "attention": "Attention", "language": "Language",
    "sequencing": "Sequencing", "reasoning": "Reasoning", "visual": "Visual",
}


def level_domain(n):
    return DOMAINS[(n - 1) % len(DOMAINS)]


def level_difficulty(n):
    if n <= 67:
        return 1
    if n <= 134:
        return 2
    return 3


def required_skill(n):
    return round((n - 1) * 100 / TOTAL_LEVELS, 1)


# ---------- word lists (kept disjoint so every answer is unambiguous) ----------

FRUITS = ["Apple", "Mango", "Banana", "Grape", "Pear", "Cherry", "Peach", "Lemon"]
ANIMALS = ["Dog", "Cat", "Cow", "Horse", "Lion", "Tiger", "Rabbit", "Goat"]
VEHICLES = ["Bus", "Car", "Train", "Bicycle", "Boat", "Plane", "Scooter", "Truck"]
FURNITURE = ["Chair", "Table", "Sofa", "Bed", "Desk", "Shelf", "Stool", "Wardrobe"]
COLOURS = ["Red", "Blue", "Green", "Yellow", "Purple", "Pink", "Brown", "Grey"]
KITCHEN = ["Plate", "Spoon", "Cup", "Pan", "Bowl", "Fork", "Kettle", "Knife"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SEASONS = ["Spring", "Summer", "Autumn", "Winter"]
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
NAMES = ["Ravi", "Meera", "Asha", "Kiran", "Dev", "Lena", "Omar"]

ANTONYMS = [("hot", "cold"), ("big", "small"), ("up", "down"), ("day", "night"), ("happy", "sad"),
            ("fast", "slow"), ("open", "closed"), ("light", "dark"), ("early", "late"), ("rich", "poor"),
            ("strong", "weak"), ("young", "old"), ("full", "empty"), ("brave", "timid")]
SYNONYMS = [("joyful", "happy"), ("rapid", "quick"), ("begin", "start"), ("tiny", "small"),
            ("buy", "purchase"), ("huge", "large"), ("inquire", "ask"), ("tired", "sleepy"), ("clever", "smart"),
            ("gentle", "kind"), ("silent", "quiet"), ("ancient", "old"), ("answer", "reply"), ("shout", "yell"),
            ("scared", "afraid"), ("pretty", "lovely"), ("wise", "sage"), ("cheap", "inexpensive")]
RHYMES = [("cat", "hat"), ("dog", "log"), ("sun", "fun"), ("cake", "lake"), ("tree", "bee"), ("ball", "wall"),
          ("night", "light"), ("book", "hook"), ("rain", "train"), ("bear", "chair"), ("star", "car")]
NON_RHYME_WORDS = ["Table", "Window", "Pencil", "Garden", "Flower", "Bottle"]
SENTENCES = [("She goes home.", ["She go home.", "She going home."]),
             ("They are happy.", ["They is happy.", "They am happy."]),
             ("He has a book.", ["He have a book.", "He haves a book."]),
             ("We played outside.", ["We plays outside.", "We playing outside."]),
             ("The cats are sleeping.", ["The cats is sleeping.", "The cats sleeps."]),
             ("I like tea.", ["I likes tea.", "I liking tea."]),
             ("She has two bags.", ["She have two bags.", "She has two bag."])]
HEAVY_PAIRS = [("a feather", "a brick"), ("a grain of rice", "a sack of rice"),
               ("a ping-pong ball", "a bowling ball")]
SIDES = {"triangle": 3, "square": 4, "pentagon": 5, "hexagon": 6, "octagon": 8}
MIXES = [(("Blue", "Yellow"), "Green"), (("Red", "Yellow"), "Orange"), (("Red", "Blue"), "Purple")]
MIX_DISTRACTORS = ["Green", "Orange", "Purple", "Brown", "Pink"]
MIRROR_PAIRS = [("b", "d"), ("p", "q")]
SYMBOLS = ["★", "●", "▲", "■"]


def _shuffled(rng, items):
    items = list(items)
    rng.shuffle(items)
    return items


def _memory(rng, d):
    category = rng.choice([FRUITS, ANIMALS, KITCHEN, VEHICLES, COLOURS])
    k = 2 + d                                  # 3, 4 or 5 items to remember
    items = rng.sample(category, k)
    pos = rng.randrange(k)
    ordinal = ["first", "second", "third", "fourth", "fifth"][pos]
    answer = items[pos]
    distractors = rng.sample([c for c in category if c not in items], 2)
    text = f"Remember: {', '.join(items)}. Which one was {ordinal}?"
    return text, _shuffled(rng, [answer] + distractors), answer, "Count from the start of the list."


def _attention(rng, d):
    main, other = rng.sample([FRUITS, ANIMALS, VEHICLES, FURNITURE, COLOURS, KITCHEN], 2)
    a, b = rng.sample(main, 2)
    odd = rng.choice(other)
    options = _shuffled(rng, [a, b, odd])
    text = f"Which one does not belong: {', '.join(options)}?"
    return (text, options, odd, "Think about what the other two have in common.")


def _cap(word):
    return word[:1].upper() + word[1:]


def _language(rng, d):
    kind = rng.choice(["rhyme", "antonym"] if d == 1 else ["antonym", "synonym"] if d == 2
                      else ["synonym", "sentence"])
    if kind == "rhyme":
        word, answer = rng.choice(RHYMES)
        answer = _cap(answer)
        stem = rng.choice(["Which word rhymes with '{w}'?", "Pick the word that rhymes with '{w}'."])
        return (stem.format(w=word), _shuffled(rng, [answer] + rng.sample(NON_RHYME_WORDS, 2)),
                answer, "Listen to the ending sound.")
    if kind == "antonym":
        word, answer = rng.choice(ANTONYMS)
        pool = [_cap(b) for a, b in ANTONYMS if a != word and b != answer]
        answer = _cap(answer)
        stem = rng.choice(["Which word means the opposite of '{w}'?", "What is the opposite of '{w}'?"])
        return (stem.format(w=word), _shuffled(rng, [answer] + rng.sample(pool, 2)),
                answer, "Think of the word that describes the other side.")
    if kind == "synonym":
        word, answer = rng.choice(SYNONYMS)
        answer = _cap(answer)
        stem = rng.choice(["Which word means the same as '{w}'?", "'{w}' has the same meaning as which word?",
                           "Pick the word that matches '{w}' in meaning."])
        return (stem.format(w=word), _shuffled(rng, [answer] + rng.sample(["Angry", "Slow", "Heavy", "Bright", "Quiet", "Tall", "Sharp"], 2)),
                answer, "Pick the word that has the same meaning.")
    correct, wrong = rng.choice(SENTENCES)
    stem = rng.choice(["Which sentence is correct?", "Choose the grammatically correct sentence.",
                       "Which of these sentences is right?"])
    return (stem, _shuffled(rng, [correct] + wrong), correct, "Check that the verb matches the subject.")


def _sequencing(rng, d):
    if rng.random() < 0.5:
        step = rng.choice([[1, 2], [2, 3, 5], [3, 4, 6, 7, 9]][d - 1])
        start = rng.randint(1, 20)
        shown = [start + i * step for i in range(4)]
        answer = start + 4 * step
        return (f"What comes next: {', '.join(map(str, shown))}, ...?",
                _shuffled(rng, [str(answer), str(answer + 1), str(answer + 2)]), str(answer),
                f"The numbers go up by {step} each time.")
    cycle = [WEEKDAYS, SEASONS, MONTHS][d - 1]
    i = rng.randrange(len(cycle))
    n = len(cycle)
    answer = cycle[(i + 1) % n]
    stem = rng.choice(["What comes after {x}?", "Which one follows {x}?", "{x} is followed by which one?",
                       "Pick the item that comes right after {x}."])
    return (stem.format(x=cycle[i]),
            _shuffled(rng, [answer, cycle[(i + 2) % n], cycle[(i - 1) % n]]), answer,
            "Think about the order it is always listed in.")


def _reasoning(rng, d):
    kind = rng.choice(["order", "category", "weight"]) if d > 1 else rng.choice(["order", "category"])
    if kind == "order":
        people = rng.sample(NAMES, 2 + d)                  # 3, 4 or 5 people in a chain
        tallest_first = people
        text = " ".join(f"{a} is taller than {b}." for a, b in zip(tallest_first, tallest_first[1:]))
        ask_tallest = rng.random() < 0.5
        answer = tallest_first[0] if ask_tallest else tallest_first[-1]
        choices = [answer] + rng.sample([p for p in tallest_first if p != answer], 2)
        word = "tallest" if ask_tallest else "shortest"
        return (f"{text} Who is the {word}?", _shuffled(rng, choices), answer,
                "Follow the chain one step at a time.")
    if kind == "category":
        thing, group = rng.choice([("roses", "flowers"), ("dogs", "animals"), ("oaks", "trees"),
                                   ("cars", "vehicles"), ("apples", "fruits"), ("carrots", "vegetables")])
        answer = f"A {group[:-1]}"
        scene = rng.choice(NAMES)
        distractors = rng.sample(["A stone", "A car", "A cloud", "A table", "A shoe"], 2)
        return (f"{scene} says: all {thing} are {group}. This is a {thing[:-1]}. What must it be?",
                _shuffled(rng, [answer] + distractors), answer,
                "Use the first statement to decide.")
    a, b = rng.choice(HEAVY_PAIRS)
    answer = b[0].upper() + b[1:]
    return (f"Which is heavier: {a} or {b}?", _shuffled(rng, [a[0].upper() + a[1:], answer, "They weigh the same"]),
            answer, "Think about which one you could lift more easily.")


def _visual(rng, d):
    kind = rng.choice(["sides", "mix", "count", "mirror"])
    if kind == "sides":
        shape = rng.choice(list(SIDES))
        answer = str(SIDES[shape])
        others = [str(v) for v in SIDES.values() if str(v) != answer]
        return (f"How many sides does a {shape} have?", _shuffled(rng, [answer] + rng.sample(others, 2)),
                answer, "Count the straight edges around the shape.")
    if kind == "mix":
        (x, y), answer = rng.choice(MIXES)
        return (f"What colour do you get when you mix {x.lower()} and {y.lower()}?",
                _shuffled(rng, [answer] + rng.sample([c for c in MIX_DISTRACTORS if c != answer], 2)),
                answer, "Think about colours you know from paint.")
    if kind == "count":
        length = [5, 7, 9][d - 1]
        row = [rng.choice(SYMBOLS) for _ in range(length)]
        if "★" not in row:
            row[rng.randrange(length)] = "★"
        count = row.count("★")
        return (f"How many ★ are in this row: {' '.join(row)}?",
                _shuffled(rng, [str(count), str(count + 1), str(count - 1)]), str(count),
                "Go left to right and tick each star.")
    (x, y) = rng.choice(MIRROR_PAIRS)
    distractors = rng.sample(["m", "w", "k", "t", "s"], 2)
    return (f"Which letter is a left-right mirror image of '{x}'?", _shuffled(rng, [y] + distractors), y,
            "Imagine flipping the letter like a mirror.")


GENERATORS = {
    "memory": _memory, "attention": _attention, "language": _language,
    "sequencing": _sequencing, "reasoning": _reasoning, "visual": _visual,
}


def _raw_level(n, attempt):
    domain = level_domain(n)
    difficulty = level_difficulty(n)
    rng = random.Random(n * 7919 + attempt * 104729)
    text, options, answer, hint = GENERATORS[domain](rng, difficulty)
    return {
        "level_number": n,
        "domain": domain,
        "difficulty": difficulty,
        "required_skill": required_skill(n),
        "question_text": text,
        "options": options,
        "correct_answer": answer,
        "hint": hint,
    }


_CACHE = None


def all_levels():
    """All 200 levels. Every question text is unique: if a generated text repeats, the
    level is regenerated with the next deterministic seed."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    levels, seen = [], set()
    for n in range(1, TOTAL_LEVELS + 1):
        for attempt in range(200):
            level = _raw_level(n, attempt)
            key = level["question_text"].casefold()
            if key not in seen:
                seen.add(key)
                break
        else:
            raise RuntimeError(f"could not build a unique question for level {n}")
        levels.append(level)
    _CACHE = levels
    return levels


def build_level(n):
    """Deterministic content for level n (1-200)."""
    if not 1 <= n <= TOTAL_LEVELS:
        raise ValueError("level must be between 1 and 200")
    return all_levels()[n - 1]
