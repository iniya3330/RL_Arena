"""RL Arena level bank: 500 levels in English (en), Hindi (hi) and Tamil (ta).

Pure Python (no Django imports) so it can be tested on its own.

- Levels come in sets of ten. Each set has 4 easy levels (positions 1-4),
  3 medium levels (positions 5-7) and 3 tricky levels (positions 8-10).
- Domains cycle level by level, so any stretch of play mixes all six domains.
- Every level has three options and exactly one correct answer.
- Each question is generated once from a seed, then written in every language with the
  same structure. Option order is the same in every language, so the answer is the same
  option position everywhere.
- A level's skill requirement rises with its number. A player unlocks a level once
  their skill in that level's domain reaches the requirement.
"""
import random

TOTAL_LEVELS = 500
SET_SIZE = 10
EASY_POSITIONS = 4      # positions 1-4 of every set of ten
MEDIUM_POSITIONS = 3    # positions 5-7; positions 8-10 are tricky
DOMAINS = ["memory", "attention", "language", "sequencing", "reasoning", "visual"]
DOMAIN_LABELS = {
    "memory": "Memory", "attention": "Attention", "language": "Language",
    "sequencing": "Sequencing", "reasoning": "Reasoning", "visual": "Visual",
}
DIFFICULTY_LABELS = {1: "easy", 2: "medium", 3: "tricky"}
LANGUAGE_CODES = ("en", "hi", "ta")


def level_domain(n):
    return DOMAINS[(n - 1) % len(DOMAINS)]


def set_position(n):
    """Where this level sits inside its set of ten (1-10)."""
    return (n - 1) % SET_SIZE + 1


def level_difficulty(n):
    position = set_position(n)
    if position <= EASY_POSITIONS:
        return 1
    if position <= EASY_POSITIONS + MEDIUM_POSITIONS:
        return 2
    return 3


def required_skill(n):
    return round((n - 1) * 100 / TOTAL_LEVELS, 1)


# ---------- English word lists. The keys below are also the keys of the translation tables. ----------

FRUITS = ["Apple", "Mango", "Banana", "Grape", "Pear", "Cherry", "Peach", "Lemon"]
ANIMALS = ["Dog", "Cat", "Cow", "Horse", "Lion", "Tiger", "Rabbit", "Goat"]
VEHICLES = ["Bus", "Car", "Train", "Bicycle", "Boat", "Plane", "Scooter", "Truck"]
FURNITURE = ["Chair", "Table", "Sofa", "Bed", "Desk", "Shelf", "Stool", "Wardrobe"]
COLOURS = ["Red", "Blue", "Green", "Yellow", "Purple", "Pink", "Brown", "Grey"]
KITCHEN = ["Plate", "Spoon", "Cup", "Pan", "Bowl", "Fork", "Kettle", "Knife"]
CATEGORIES = [FRUITS, ANIMALS, VEHICLES, FURNITURE, COLOURS, KITCHEN]
MEMORY_POOL = [word for category in CATEGORIES for word in category]
NAMES = ["Ravi", "Meera", "Asha", "Kiran", "Dev", "Lena", "Omar"]

ANTONYMS = [("hot", "cold"), ("big", "small"), ("up", "down"), ("day", "night"), ("happy", "sad"),
            ("fast", "slow"), ("open", "closed"), ("light", "dark"), ("early", "late"), ("rich", "poor"),
            ("strong", "weak"), ("young", "old"), ("full", "empty"), ("brave", "timid")]
SYNONYMS = [("joyful", "happy"), ("rapid", "quick"), ("begin", "start"), ("tiny", "small"),
            ("buy", "purchase"), ("huge", "large"), ("inquire", "ask"), ("tired", "sleepy"), ("clever", "smart"),
            ("gentle", "kind"), ("silent", "quiet"), ("answer", "reply"), ("shout", "yell"),
            ("scared", "afraid"), ("pretty", "lovely"), ("wise", "sage"), ("cheap", "inexpensive")]
SYNONYM_WRONG = ["Angry", "Slow", "Heavy", "Bright", "Tall", "Sharp", "Loud"]
SIDES = {"triangle": 3, "square": 4, "pentagon": 5, "hexagon": 6, "octagon": 8}
SYMBOLS = ["★", "●", "▲", "■"]
# (thing, group, singular, answer). "all <thing> are <group>", "the thing here is one <singular>".
CATEGORY_FACTS = [("roses", "flowers", "rose", "A flower"), ("dogs", "animals", "dog", "An animal"),
                  ("oaks", "trees", "oak", "A tree"), ("cars", "vehicles", "car", "A vehicle"),
                  ("apples", "fruits", "apple", "A fruit"), ("carrots", "vegetables", "carrot", "A vegetable")]
NOT_IN_GROUPS = ["A stone", "A cloud", "A shoe", "A table"]

# Every English key -> (Hindi, Tamil). English words are shown as they are.
WORD_TABLE = [
    # fruits
    ("Apple", "सेब", "ஆப்பிள்"), ("Mango", "आम", "மாம்பழம்"), ("Banana", "केला", "வாழைப்பழம்"),
    ("Grape", "अंगूर", "திராட்சை"), ("Pear", "नाशपाती", "பேரிக்காய்"), ("Cherry", "चेरी", "செர்ரி"),
    ("Peach", "आड़ू", "பீச்"), ("Lemon", "नींबू", "எலுமிச்சை"),
    # animals
    ("Dog", "कुत्ता", "நாய்"), ("Cat", "बिल्ली", "பூனை"), ("Cow", "गाय", "பசு"), ("Horse", "घोड़ा", "குதிரை"),
    ("Lion", "शेर", "சிங்கம்"), ("Tiger", "बाघ", "புலி"), ("Rabbit", "खरगोश", "முயல்"), ("Goat", "बकरी", "ஆடு"),
    # vehicles
    ("Bus", "बस", "பேருந்து"), ("Car", "कार", "கார்"), ("Train", "रेलगाड़ी", "ரயில்"),
    ("Bicycle", "साइकिल", "சைக்கிள்"), ("Boat", "नाव", "படகு"), ("Plane", "हवाई जहाज़", "விமானம்"),
    ("Scooter", "स्कूटर", "ஸ்கூட்டர்"), ("Truck", "ट्रक", "லாரி"),
    # furniture
    ("Chair", "कुर्सी", "நாற்காலி"), ("Table", "मेज़", "மேசை"), ("Sofa", "सोफ़ा", "சோபா"), ("Bed", "बिस्तर", "படுக்கை"),
    ("Desk", "डेस्क", "எழுதுமேசை"), ("Shelf", "शेल्फ़", "அலமாரிப் பலகை"), ("Stool", "स्टूल", "முக்காலி"),
    ("Wardrobe", "अलमारी", "அலமாரி"),
    # colours
    ("Red", "लाल", "சிவப்பு"), ("Blue", "नीला", "நீலம்"), ("Green", "हरा", "பச்சை"), ("Yellow", "पीला", "மஞ்சள்"),
    ("Purple", "बैंगनी", "ஊதா"), ("Pink", "गुलाबी", "இளஞ்சிவப்பு"), ("Brown", "भूरा", "பழுப்பு"), ("Grey", "स्लेटी", "சாம்பல்"),
    # kitchen
    ("Plate", "प्लेट", "தட்டு"), ("Spoon", "चम्मच", "கரண்டி"), ("Cup", "कप", "கோப்பை"), ("Pan", "कड़ाही", "வாணலி"),
    ("Bowl", "कटोरी", "கிண்ணம்"), ("Fork", "काँटा", "முள்கரண்டி"), ("Kettle", "केतली", "கெட்டில்"), ("Knife", "चाकू", "கத்தி"),
    # names
    ("Ravi", "रवि", "ரவி"), ("Meera", "मीरा", "மீரா"), ("Asha", "आशा", "ஆஷா"), ("Kiran", "किरण", "கிரண்"),
    ("Dev", "देव", "தேவ்"), ("Lena", "लीना", "லீனா"), ("Omar", "उमर", "உமர்"),
    # antonyms
    ("hot", "गर्म", "சூடான"), ("cold", "ठंडा", "குளிர்ந்த"), ("big", "बड़ा", "பெரிய"), ("small", "छोटा", "சிறிய"),
    ("up", "ऊपर", "மேலே"), ("down", "नीचे", "கீழே"), ("day", "दिन", "பகல்"), ("night", "रात", "இரவு"),
    ("happy", "खुश", "மகிழ்ச்சியான"), ("sad", "उदास", "சோகமான"), ("fast", "तेज़", "வேகமான"), ("slow", "धीमा", "மெதுவான"),
    ("open", "खुला", "திறந்த"), ("closed", "बंद", "மூடிய"), ("light", "उजाला", "வெளிச்சம்"), ("dark", "अंधेरा", "இருட்டு"),
    ("early", "जल्दी", "சீக்கிரம்"), ("late", "देर से", "தாமதமாக"), ("rich", "अमीर", "பணக்காரர்"), ("poor", "गरीब", "ஏழை"),
    ("strong", "मज़बूत", "வலிமையான"), ("weak", "कमज़ोर", "பலவீனமான"), ("young", "जवान", "இளைய"), ("old", "बूढ़ा", "முதிய"),
    ("full", "भरा", "நிரம்பிய"), ("empty", "खाली", "காலியான"), ("brave", "बहादुर", "துணிச்சலான"), ("timid", "डरपोक", "பயந்த"),
    # synonyms
    ("joyful", "आनंदित", "ஆனந்தமான"), ("rapid", "त्वरित", "விரைவான"), ("quick", "फुर्तीला", "சுறுசுறுப்பான"),
    ("begin", "शुरू करना", "தொடங்கு"), ("start", "आरंभ करना", "ஆரம்பி"), ("tiny", "नन्हा", "சிறு"),
    ("buy", "खरीदना", "வாங்கு"), ("purchase", "ख़रीदारी करना", "கொள்முதல் செய்"), ("huge", "अत्यधिक बड़ा", "பிரம்மாண்டமான"),
    ("large", "विशाल", "பெரிய"), ("inquire", "पूछताछ करना", "விசாரி"), ("ask", "पूछना", "கேள்"),
    ("tired", "थका हुआ", "களைப்பான"), ("sleepy", "नींद वाला", "தூக்கக் கலக்கமான"), ("clever", "होशियार", "புத்திசாலி"),
    ("smart", "चतुर", "சாமர்த்தியமான"), ("gentle", "कोमल", "மென்மையான"), ("kind", "दयालु", "அன்பான"),
    ("silent", "खामोश", "மௌனமான"), ("quiet", "शांत", "அமைதியான"), ("answer", "उत्तर", "விடை"), ("reply", "जवाब", "பதில்"),
    ("shout", "चिल्लाना", "கத்து"), ("yell", "ज़ोर से बोलना", "கூச்சலிடு"), ("scared", "डरा हुआ", "அச்சமடைந்த"),
    ("afraid", "भयभीत", "பயமுள்ள"), ("pretty", "सुंदर", "அழகான"), ("lovely", "मनोहर", "அருமையான"),
    ("wise", "बुद्धिमान", "ஞானமுள்ள"), ("sage", "ज्ञानी", "ஞானி"), ("cheap", "सस्ता", "மலிவான"),
    ("inexpensive", "किफ़ायती", "விலை குறைவான"),
    # wrong synonyms
    ("Angry", "गुस्सैल", "கோபமான"), ("Slow", "धीमा", "மெதுவான"), ("Heavy", "भारी", "கனமான"), ("Bright", "चमकीला", "பிரகாசமான"),
    ("Tall", "ऊँचा", "உயரமான"), ("Sharp", "तेज़ धार वाला", "கூர்மையான"), ("Loud", "तेज़ आवाज़ वाला", "சத்தமான"),
    # shapes
    ("triangle", "त्रिभुज", "முக்கோணம்"), ("square", "वर्ग", "சதுரம்"), ("pentagon", "पंचभुज", "ஐங்கோணம்"),
    ("hexagon", "षट्भुज", "அறுகோணம்"), ("octagon", "अष्टभुज", "எண்கோணம்"),
    # category facts
    ("roses", "गुलाब", "ரோஜாக்கள்"), ("rose", "गुलाब", "ரோஜா"), ("flowers", "फूल", "பூக்கள்"),
    ("A flower", "एक फूल", "ஒரு பூ"), ("dogs", "कुत्ते", "நாய்கள்"), ("dog", "कुत्ता", "நாய்"),
    ("animals", "जानवर", "விலங்குகள்"), ("An animal", "एक जानवर", "ஒரு விலங்கு"), ("oaks", "बलूत", "ஓக் மரங்கள்"),
    ("oak", "बलूत का पेड़", "ஓக் மரம்"), ("trees", "पेड़", "மரங்கள்"), ("A tree", "एक पेड़", "ஒரு மரம்"),
    ("cars", "कारें", "கார்கள்"), ("car", "कार", "கார்"), ("vehicles", "वाहन", "வாகனங்கள்"),
    ("A vehicle", "एक वाहन", "ஒரு வாகனம்"), ("apples", "सेब", "ஆப்பிள்கள்"), ("apple", "सेब", "ஆப்பிள்"),
    ("fruits", "फल", "பழங்கள்"), ("A fruit", "एक फल", "ஒரு பழம்"), ("carrots", "गाजरें", "கேரட்டுகள்"),
    ("carrot", "गाजर", "கேரட்"), ("vegetables", "सब्ज़ियाँ", "காய்கறிகள்"), ("A vegetable", "एक सब्ज़ी", "ஒரு காய்கறி"),
    ("A stone", "एक पत्थर", "ஒரு கல்"), ("A cloud", "एक बादल", "ஒரு மேகம்"), ("A shoe", "एक जूता", "ஒரு காலணி"),
    ("A table", "एक मेज़", "ஒரு மேசை"),
    # reasoning words
    ("tallest", "सबसे लंबा", "மிக உயரமானவர்"), ("shortest", "सबसे छोटा", "மிகக் குள்ளமானவர்"),
    ("second tallest", "दूसरा सबसे लंबा", "இரண்டாவது உயரமானவர்"),
    ("second shortest", "दूसरा सबसे छोटा", "இரண்டாவது குள்ளமானவர்"),
]

WORDS = {
    "hi": {english: hindi for english, hindi, _ in WORD_TABLE},
    "ta": {english: tamil for english, _, tamil in WORD_TABLE},
}

# Sentence templates: key -> (English, Hindi, Tamil). Placeholders are the same in every language.
PHRASE_TABLE = [
    ("memory_list", "Remember this list: {items}. Which of these was NOT on the list?",
     "यह सूची याद रखें: {items}। इनमें से कौन सी सूची में नहीं थी?",
     "இந்தப் பட்டியலை நினைவில் கொள்ளுங்கள்: {items}. இவற்றில் பட்டியலில் இல்லாதது எது?"),
    ("hint_memory_check", "Check each word against the list.", "हर शब्द को सूची से मिलाएँ।",
     "ஒவ்வொரு சொல்லையும் பட்டியலுடன் ஒப்பிடுங்கள்."),
    ("memory_after", "Remember this order: {items}. What came directly after {item}?",
     "यह क्रम याद रखें: {items}। {item} के ठीक बाद कौन आया?",
     "இந்த வரிசையை நினைவில் கொள்ளுங்கள்: {items}. {item}-க்குப் பிறகு உடனே எது வந்தது?"),
    ("hint_memory_after", "Find the item, then look at the one after it.", "वस्तु खोजें, फिर उसके बाद वाली देखें।",
     "சொல்லைக் கண்டுபிடித்து அதற்கு அடுத்ததைப் பாருங்கள்."),
    ("memory_back", "Remember this order: {items}. Which item was two places before the last one?",
     "यह क्रम याद रखें: {items}। अंतिम से दो स्थान पहले कौन सी वस्तु थी?",
     "இந்த வரிசையை நினைவில் கொள்ளுங்கள்: {items}. கடைசிக்கு முந்தைய இரண்டாவது இடத்தில் இருந்தது எது?"),
    ("hint_memory_back", "Count back from the last item, not from the start.",
     "शुरू से नहीं, अंतिम वस्तु से पीछे गिनें।", "தொடக்கத்திலிருந்து அல்ல, கடைசிச் சொல்லிலிருந்து பின்னோக்கி எண்ணுங்கள்."),
    ("attention_odd", "Which one does not belong: {items}?", "कौन सा एक मेल नहीं खाता: {items}?",
     "எது பொருந்தவில்லை: {items}?"),
    ("hint_attention_odd", "Think about what the other two have in common.",
     "सोचें कि बाकी दो में क्या समानता है।", "மற்ற இரண்டிலும் உள்ள பொதுத்தன்மையை யோசியுங்கள்."),
    ("attention_a_not_b", "List {la}: {a}. List {lb}: {b}. Which word is in List {la} but NOT in List {lb}?",
     "सूची {la}: {a}। सूची {lb}: {b}। कौन सा शब्द सूची {la} में है पर सूची {lb} में नहीं?",
     "பட்டியல் {la}: {a}. பட்டியல் {lb}: {b}. பட்டியல் {la}-வில் உள்ளதும் பட்டியல் {lb}-யில் இல்லாததுமான சொல் எது?"),
    ("hint_attention_a", "Go through List {la} one word at a time.", "सूची {la} के हर शब्द को एक-एक करके देखें।",
     "பட்டியல் {la}-வின் சொற்களை ஒவ்வொன்றாகப் பாருங்கள்."),
    ("attention_both", "List {la}: {a}. List {lb}: {b}. Which word appears in BOTH lists?",
     "सूची {la}: {a}। सूची {lb}: {b}। कौन सा शब्द दोनों सूचियों में है?",
     "பட்டியல் {la}: {a}. பட்டியல் {lb}: {b}. இரண்டு பட்டியல்களிலும் உள்ள சொல் எது?"),
    ("hint_attention_both", "Only one word is on both lists.", "केवल एक शब्द दोनों सूचियों में है।",
     "இரண்டு பட்டியல்களிலும் ஒரே ஒரு சொல் மட்டுமே உள்ளது."),
    ("language_opposite", "Which word means the opposite of '{w}'? Choose from: {options}.",
     "'{w}' का विलोम कौन सा शब्द है? विकल्प: {options}",
     "'{w}'-க்கு எதிர்ச்சொல் எது? தேர்வுகள்: {options}"),
    ("hint_opposite", "Think of the word that describes the other side.",
     "दूसरी ओर का वर्णन करने वाला शब्द सोचें।", "மறுபக்கத்தை விவரிக்கும் சொல்லை யோசியுங்கள்."),
    ("language_synonym", "Which word means the same as '{w}'? Choose from: {options}.",
     "'{w}' के समान अर्थ वाला शब्द कौन सा है? विकल्प: {options}",
     "'{w}'-க்கு இணையான பொருள் உள்ள சொல் எது? தேர்வுகள்: {options}"),
    ("hint_synonym", "Pick the word with the same meaning, not the opposite.",
     "वह शब्द चुनें जिसका अर्थ समान हो, विपरीत नहीं।",
     "எதிர்ப்பொருள் அல்ல, அதே பொருள் உள்ள சொல்லைத் தேர்ந்தெடுங்கள்."),
    ("language_analogy", "'{a}' is to '{b}' as '{c}' is to what?",
     "'{a}' का '{b}' से जो संबंध है, वही '{c}' का किससे है?", "'{a}' : '{b}' போல '{c}' : எது?"),
    ("hint_analogy", "The first pair are opposites. Find the opposite of the third word.",
     "पहली जोड़ी विपरीत है। तीसरे शब्द का विपरीत खोजें।",
     "முதல் ஜோடி எதிர்ச்சொற்கள். மூன்றாவது சொல்லின் எதிர்ச்சொல்லைக் கண்டுபிடியுங்கள்."),
    ("sequence_next", "What comes next: {seq}, ...?", "अगला क्या आएगा: {seq}, ...?", "அடுத்து வருவது எது: {seq}, ...?"),
    ("hint_step", "The numbers go up by {step} each time.", "हर बार संख्याएँ {step} बढ़ती हैं।",
     "ஒவ்வொரு முறையும் எண்கள் {step} கூடுகின்றன."),
    ("hint_square", "Each number is a perfect square, in order.", "हर संख्या क्रम से एक पूर्ण वर्ग है।",
     "ஒவ்வொரு எண்ணும் வரிசையாக ஒரு முழு வர்கம்."),
    ("hint_cube", "Each number is a perfect cube, in order.", "हर संख्या क्रम से एक पूर्ण घन है।",
     "ஒவ்வொரு எண்ணும் வரிசையாக ஒரு முழு கனம்."),
    ("hint_ratio", "Each number is {ratio} times the one before.", "हर संख्या उससे पहले वाली से {ratio} गुना है।",
     "ஒவ்வொரு எண்ணும் அதற்கு முந்தையதை விட {ratio} மடங்கு."),
    ("hint_gap", "The gap between numbers grows by one each time.",
     "संख्याओं के बीच का अंतर हर बार एक बढ़ता है।", "எண்களுக்கு இடையிலான இடைவெளி ஒவ்வொரு முறையும் ஒன்று அதிகரிக்கிறது."),
    ("sequence_mixed", "Two number lists are mixed together: {seq}, ... What comes next?",
     "दो संख्या सूचियाँ मिली हुई हैं: {seq}, ... अगला क्या आएगा?",
     "இரண்டு எண் பட்டியல்கள் கலந்துள்ளன: {seq}, ... அடுத்து வருவது எது?"),
    ("hint_mixed", "Follow every other number to see one list at a time.",
     "एक बार में एक सूची देखने के लिए हर दूसरी संख्या देखें।",
     "ஒரு நேரத்தில் ஒரு பட்டியலைக் காண ஒவ்வொரு மாற்று எண்ணையும் பின்தொடருங்கள்."),
    ("category_fact", "{scene} says: all {thing} are {group}. The thing here is one {single}. What must it be?",
     "{scene} कहते हैं: सभी {thing} {group} हैं। यहाँ की चीज़ एक {single} है। वह क्या होनी चाहिए?",
     "{scene} கூறுகிறார்: எல்லா {thing}உம் {group}. இங்குள்ளது ஒரு {single}. அது என்னவாக இருக்க வேண்டும்?"),
    ("hint_category", "Use the first statement to decide.", "निर्णय के लिए पहला कथन इस्तेमाल करें।",
     "முடிவெடுக்க முதல் கூற்றைப் பயன்படுத்துங்கள்."),
    ("taller", "{a} is taller than {b}.", "{a}, {b} से लंबा है।", "{a}, {b}-ஐ விட உயரமானவர்."),
    ("who_is", "Who is the {word}?", "{word} कौन है?", "{word} யார்?"),
    ("hint_chain", "Follow the chain one step at a time.", "श्रृंखला को एक-एक कदम करके देखें।",
     "சங்கிலியை ஒரு படியாகப் பின்தொடருங்கள்."),
    ("hint_order", "Put the pairs in order, tallest first, before you answer.",
     "उत्तर देने से पहले जोड़ों को सबसे लंबे से क्रम में लगाएँ।",
     "பதிலளிக்கும் முன், உயரமானவரிலிருந்து தொடங்கி ஜோடிகளை வரிசைப்படுத்துங்கள்."),
    ("visual_row", "How many {sym} are in this row: {row}?", "इस पंक्ति में कितने {sym} हैं: {row}?",
     "இந்த வரிசையில் எத்தனை {sym} உள்ளன: {row}?"),
    ("hint_row", "Count each symbol from left to right.", "हर चिह्न को बाएँ से दाएँ गिनें।",
     "ஒவ்வொரு குறியையும் இடமிருந்து வலமாக எண்ணுங்கள்."),
    ("visual_two", "How many {s1} and {s2} together are in this row: {row}?",
     "इस पंक्ति में {s1} और {s2} मिलाकर कितने हैं: {row}?",
     "இந்த வரிசையில் {s1} மற்றும் {s2} சேர்த்து எத்தனை உள்ளன: {row}?"),
    ("hint_two", "Count both symbols, then add them together.", "दोनों चिह्न गिनें, फिर उन्हें जोड़ें।",
     "இரண்டு குறிகளையும் எண்ணி, பிறகு கூட்டுங்கள்."),
    ("sides_sum", "How many sides do a {a} and a {b} have together?",
     "एक {a} और एक {b} की कुल कितनी भुजाएँ होती हैं?", "ஒரு {a}க்கும் ஒரு {b}க்கும் சேர்த்து எத்தனை பக்கங்கள்?"),
    ("hint_sides", "Count the sides of each shape, then add them.", "हर आकृति की भुजाएँ गिनकर जोड़ें।",
     "ஒவ்வொரு வடிவத்தின் பக்கங்களையும் எண்ணிக் கூட்டுங்கள்."),
    ("grid_row", "Grid, row by row: {grid}. How many {t} are in row {r}?",
     "ग्रिड, पंक्ति दर पंक्ति: {grid}। पंक्ति {r} में कितने {t} हैं?",
     "கட்டம், வரிசை வரிசையாக: {grid}. வரிசை {r}-இல் எத்தனை {t} உள்ளன?"),
    ("grid_not", "Grid, row by row: {grid}. How many symbols are NOT {t}?",
     "ग्रिड, पंक्ति दर पंक्ति: {grid}। कितने चिह्न {t} नहीं हैं?",
     "கட்டம், வரிசை வரிசையாக: {grid}. {t} இல்லாத குறிகள் எத்தனை?"),
    ("hint_grid", "Go through the grid one row at a time.", "ग्रिड को एक-एक पंक्ति करके देखें।",
     "கட்டத்தை ஒவ்வொரு வரிசையாகப் பாருங்கள்."),
]


# ---------- v9 additions: new pattern families (no "what is first/second" recall questions) ----------

GROUPS = [("fruits", FRUITS), ("animals", ANIMALS), ("vehicles", VEHICLES),
          ("furniture", FURNITURE), ("colours", COLOURS), ("kitchen things", KITCHEN)]

WORD_TABLE += [
    ("furniture", "फर्नीचर", "மரச்சாமான்"), ("colours", "रंग", "நிறங்கள்"),
    ("kitchen things", "रसोई की चीज़ें", "சமையலறைப் பொருட்கள்"),
]
WORDS = {
    "hi": {english: hindi for english, hindi, _ in WORD_TABLE},
    "ta": {english: tamil for english, _, tamil in WORD_TABLE},
}

PHRASE_TABLE += [
    ("memory_count", "Remember these words: {items}. How many of them are {group}?",
     "इन शब्दों को याद रखें: {items}। इनमें से कितने {group} हैं?",
     "இந்தச் சொற்களை நினைவில் கொள்ளுங்கள்: {items}. இவற்றில் எத்தனை {group}?"),
    ("memory_most", "Remember these words: {items}. Which group appears most often in the list?",
     "इन शब्दों को याद रखें: {items}। सूची में कौन सा समूह सबसे ज़्यादा बार आया?",
     "இந்தச் சொற்களை நினைவில் கொள்ளுங்கள்: {items}. பட்டியலில் எந்தக் குழு அதிகம் வந்தது?"),
    ("memory_repeat", "Remember this list: {items}. Which word appears TWICE?",
     "यह सूची याद रखें: {items}। कौन सा शब्द दो बार आया?",
     "இந்தப் பட்டியலை நினைவில் கொள்ளுங்கள்: {items}. எந்தச் சொல் இரண்டு முறை வந்தது?"),
    ("memory_pair", "Remember these numbers: {nums}. Which two of them add up to {total}?",
     "ये संख्याएँ याद रखें: {nums}। इनमें से कौन सी दो जोड़ने पर {total} होती हैं?",
     "இந்த எண்களை நினைவில் கொள்ளுங்கள்: {nums}. இவற்றில் எவை இரண்டைக் கூட்டினால் {total} வரும்?"),
    ("hint_memory_count", "Count only the words from that group.", "केवल उसी समूह के शब्द गिनें।",
     "அந்தக் குழுவின் சொற்களை மட்டும் எண்ணுங்கள்."),
    ("hint_memory_most", "Count how many words belong to each group.", "हर समूह के शब्द गिनें।",
     "ஒவ்வொரு குழுவின் சொற்களையும் எண்ணுங்கள்."),
    ("hint_memory_repeat", "Look for a word you have already seen in the list.",
     "सूची में ऐसा शब्द खोजें जो पहले भी आ चुका हो।", "பட்டியலில் ஏற்கெனவே வந்த சொல்லைத் தேடுங்கள்."),
    ("hint_memory_pair", "Try each pair one at a time.", "हर जोड़ी को एक-एक करके जाँचें।",
     "ஒவ்வொரு ஜோடியையும் ஒன்றொன்றாகச் சரிபாருங்கள்."),
    ("hint_down", "The numbers go down by {step} each time.", "हर बार संख्याएँ {step} घटती हैं।",
     "ஒவ்வொரு முறையும் எண்கள் {step} குறைகின்றன."),
    ("hint_fib", "Add the last two numbers to get the next one.",
     "अगली संख्या पाने के लिए आखिरी दो संख्याएँ जोड़ें।", "அடுத்த எண்ணைப் பெற கடைசி இரண்டு எண்களைக் கூட்டுங்கள்."),
    ("hint_alt", "The numbers go up by {up}, then down by {down}, in turn.",
     "संख्याएँ बारी-बारी से {up} बढ़ती और {down} घटती हैं।", "எண்கள் மாறி மாறி {up} கூடி, {down} குறைகின்றன."),
    ("missing_number", "Find the missing number, shown as ?: {seq}",
     "गायब संख्या खोजें, जो ? से दिखाई गई है: {seq}",
     "விடுபட்ட எண்ணைக் கண்டுபிடியுங்கள், அது ? எனக் காட்டப்பட்டுள்ளது: {seq}"),
    ("hint_missing", "Find the gap between the numbers you can see.",
     "दिखने वाली संख्याओं के बीच का अंतर खोजें।", "தெரியும் எண்களுக்கு இடையிலான வித்தியாசத்தைக் கண்டுபிடியுங்கள்."),
    ("hint_dbl1", "Double the last number, then add one.", "पिछली संख्या को दोगुना करें, फिर एक जोड़ें।",
     "கடைசி எண்ணை இரட்டிப்பாக்கி ஒன்றைக் கூட்டுங்கள்."),
    ("between", "Who is taller than {low} but shorter than {high}?",
     "कौन {low} से लंबा है पर {high} से छोटा है?", "{low}-ஐ விட உயரமாகவும் {high}-ஐ விடக் குள்ளமாகவும் இருப்பவர் யார்?"),
]

LIST_LABELS = {"en": ("A", "B"), "hi": ("क", "ख"), "ta": ("அ", "ஆ")}

PHRASES = {
    "en": {key: en for key, en, _, _ in PHRASE_TABLE},
    "hi": {key: hi for key, _, hi, _ in PHRASE_TABLE},
    "ta": {key: ta for key, _, _, ta in PHRASE_TABLE},
}


class _Text:
    """Renders one language. Word lookups fall back to the English word."""

    def __init__(self, lang):
        self.lang = lang
        self.words = WORDS.get(lang, {})

    def w(self, word):
        """A word inside a sentence."""
        return self.words.get(word, word)

    def o(self, word):
        """A word as shown on an answer button (capitalised in English)."""
        if self.lang == "en":
            return word[:1].upper() + word[1:]
        return self.words.get(word, word)

    def list(self, words, option=False):
        return ", ".join(self.o(word) if option else self.w(word) for word in words)

    def p(self, key, **values):
        values.setdefault("la", LIST_LABELS[self.lang][0])
        values.setdefault("lb", LIST_LABELS[self.lang][1])
        return PHRASES[self.lang][key].format(**values)


def _shuffled(rng, items):
    items = list(items)
    rng.shuffle(items)
    return items


def _pack(T, text, options_en, answer_en, hint):
    return text, [T.o(option) for option in options_en], T.o(answer_en), hint


# ---------- generators: each returns (question_text, options, correct_answer, hint) ----------

def _memory(rng, d, T):
    if d == 1:
        label, group = rng.choice(GROUPS)
        k = rng.randint(1, 4)
        in_group = rng.sample(group, k)
        outside = [w for w in MEMORY_POOL if w not in group]
        items = _shuffled(rng, in_group + rng.sample(outside, 5 - k))
        return _pack(T, T.p("memory_count", items=T.list(items), group=T.w(label)),
                     _shuffled(rng, [str(k), str(k + 1), str(k - 1)]), str(k), T.p("hint_memory_count"))
    if d == 2:
        chosen = rng.sample(GROUPS, 3)
        counts = rng.sample([3, 2, 1], 3)
        items = []
        for (label, group), count in zip(chosen, counts):
            items += rng.sample(group, count)
        answer = chosen[counts.index(3)][0]
        return _pack(T, T.p("memory_most", items=T.list(_shuffled(rng, items))),
                     [label for label, _ in chosen], answer, T.p("hint_memory_most"))
    if rng.random() < 0.5:
        nums = rng.sample(range(1, 21), 6)
        pairs = [(a, b) for i, a in enumerate(nums) for b in nums[i + 1:]]
        a, b = rng.choice(pairs)
        total = a + b
        if sum(1 for p in pairs if sum(p) == total) == 1:
            others = [p for p in pairs if sum(p) != total]
            options = [f"{x} + {y}" for x, y in [(a, b)] + rng.sample(others, 2)]
            text = T.p("memory_pair", nums=", ".join(map(str, nums)), total=total)
            return _pack(T, text, _shuffled(rng, options), f"{a} + {b}", T.p("hint_memory_pair"))
    items = rng.sample(MEMORY_POOL, 7)
    repeated = rng.choice(items)
    shown = _shuffled(rng, items + [repeated])
    distractors = rng.sample([w for w in MEMORY_POOL if w not in items], 2)
    return _pack(T, T.p("memory_repeat", items=T.list(shown)), _shuffled(rng, [repeated] + distractors),
                 repeated, T.p("hint_memory_repeat"))


def _attention(rng, d, T):
    if d == 1:
        main, other = rng.sample(CATEGORIES, 2)
        a, b = rng.sample(main, 2)
        odd = rng.choice(other)
        options = _shuffled(rng, [a, b, odd])
        return _pack(T, T.p("attention_odd", items=T.list(options, option=True)), options, odd,
                     T.p("hint_attention_odd"))
    if d == 2:
        list_a = rng.sample(MEMORY_POOL, 4)
        shared = rng.sample(list_a, 3)
        only_b = rng.choice([w for w in MEMORY_POOL if w not in list_a])
        list_b = _shuffled(rng, shared + [only_b])
        answer = next(w for w in list_a if w not in shared)
        text = T.p("attention_a_not_b", a=T.list(list_a), b=T.list(list_b))
        return _pack(T, text, _shuffled(rng, [answer, shared[0], only_b]), answer, T.p("hint_attention_a"))
    pool = rng.sample(MEMORY_POOL, 7)
    shared = pool[0]
    list_a = _shuffled(rng, [shared, pool[1], pool[2], pool[3]])
    list_b = _shuffled(rng, [shared, pool[4], pool[5], pool[6]])
    text = T.p("attention_both", a=T.list(list_a), b=T.list(list_b))
    return _pack(T, text, _shuffled(rng, [shared, pool[1], pool[4]]), shared, T.p("hint_attention_both"))


def _language(rng, d, T):
    if d == 1:
        word, answer = rng.choice(ANTONYMS)
        pool = [b for a, b in ANTONYMS if a != word and b != answer]
        options = _shuffled(rng, [answer] + rng.sample(pool, 2))
        text = T.p("language_opposite", w=T.w(word), options=T.list(options, option=True))
        return _pack(T, text, options, answer, T.p("hint_opposite"))
    if d == 2:
        word, answer = rng.choice(SYNONYMS)
        options = _shuffled(rng, [answer] + rng.sample(SYNONYM_WRONG, 2))
        text = T.p("language_synonym", w=T.w(word), options=T.list(options, option=True))
        return _pack(T, text, options, answer, T.p("hint_synonym"))
    first = rng.choice(ANTONYMS)
    second = rng.choice([p for p in ANTONYMS if set(p).isdisjoint(first)])
    a, b = first
    c, answer = second
    text = T.p("language_analogy", a=T.w(a), b=T.w(b), c=T.w(c))
    return _pack(T, text, _shuffled(rng, [answer, c, b]), answer, T.p("hint_analogy"))


def _sequencing(rng, d, T):
    if d == 1:
        kind = rng.choice(["arith", "down", "fib", "alt"])
        if kind == "arith":
            step, start = rng.randint(3, 12), rng.randint(10, 60)
            shown = [start + i * step for i in range(4)]
            answer = start + 4 * step
            hint, distractors = T.p("hint_step", step=step), [answer + 1, answer - step]
        elif kind == "down":
            step, start = rng.randint(3, 9), rng.randint(70, 150)
            shown = [start - i * step for i in range(4)]
            answer = start - 4 * step
            hint, distractors = T.p("hint_down", step=step), [answer + 1, answer + step]
        elif kind == "fib":
            a = rng.randint(1, 9)
            b = rng.randint(a + 1, 15)
            seq = [a, b]
            while len(seq) < 5:
                seq.append(seq[-1] + seq[-2])
            shown, answer = seq[:4], seq[4]
            hint, distractors = T.p("hint_fib"), [answer + 1, answer - 1]
        else:
            v0, up = rng.randint(5, 30), rng.randint(3, 8)
            down = rng.randint(1, up - 1)
            shown = [v0, v0 + up, v0 + up - down, v0 + 2 * up - down, v0 + 2 * up - 2 * down]
            answer = v0 + 3 * up - 2 * down
            hint, distractors = T.p("hint_alt", up=up, down=down), [answer + 1, answer - down]
        text = T.p("sequence_next", seq=", ".join(map(str, shown)))
        return text, _shuffled(rng, [str(answer)] + [str(x) for x in distractors]), str(answer), hint
    if d == 2:
        kind = rng.choice(["square", "cube", "double", "triple", "triangular", "missing"])
        if kind == "missing":
            step, start = rng.randint(4, 11), rng.randint(3, 25)
            full = [start + i * step for i in range(5)]
            answer = full[2]
            seq = ", ".join("?" if i == 2 else str(x) for i, x in enumerate(full))
            return (T.p("missing_number", seq=seq), _shuffled(rng, [str(answer), str(answer + 1), str(answer - step)]),
                    str(answer), T.p("hint_missing"))
        if kind in ("square", "cube"):
            k = rng.randint(1, 15)
            power = 2 if kind == "square" else 3
            shown = [(k + i) ** power for i in range(3)]
            answer = (k + 3) ** power
            distractors = [answer - 1, answer + 1]
            hint = T.p("hint_square") if power == 2 else T.p("hint_cube")
        elif kind in ("double", "triple"):
            ratio = 2 if kind == "double" else 3
            s0 = rng.randint(1, 20)
            shown = [s0 * ratio ** i for i in range(3)]
            answer = s0 * ratio ** 3
            distractors = [s0 * (ratio + 2), s0 * (ratio ** 3 + ratio)]
            hint = T.p("hint_ratio", ratio=ratio)
        else:
            k = rng.randint(1, 15)
            tri = lambda n: n * (n + 1) // 2
            shown = [tri(k + i) for i in range(3)]
            answer = tri(k + 3)
            distractors = [answer - 1, answer + 2]
            hint = T.p("hint_gap")
        text = T.p("sequence_next", seq=", ".join(map(str, shown)))
        return text, _shuffled(rng, [str(answer)] + [str(x) for x in distractors]), str(answer), hint
    if rng.random() < 0.5:
        x = rng.randint(1, 6)
        seq = [x]
        for _ in range(4):
            seq.append(2 * seq[-1] + 1)
        answer = 2 * seq[-1] + 1
        text = T.p("sequence_next", seq=", ".join(map(str, seq)))
        return text, _shuffled(rng, [str(answer), str(answer - 1), str(answer + 2)]), str(answer), T.p("hint_dbl1")
    a0, sa = rng.randint(1, 9), rng.randint(2, 5)
    b0, sb = rng.randint(10, 30), rng.randint(3, 9)
    shown = [a0, b0, a0 + sa, b0 + sb, a0 + 2 * sa, b0 + 2 * sb]
    answer = a0 + 3 * sa
    distractors = [b0 + 3 * sb, answer + 1]
    text = T.p("sequence_mixed", seq=", ".join(map(str, shown)))
    return text, _shuffled(rng, [str(answer)] + [str(x) for x in distractors]), str(answer), T.p("hint_mixed")


def _reasoning(rng, d, T):
    if d == 1:
        thing, group, singular, answer = rng.choice(CATEGORY_FACTS)
        scene = rng.choice(NAMES)
        distractors = rng.sample(NOT_IN_GROUPS, 2)
        text = T.p("category_fact", scene=T.w(scene), thing=T.w(thing), group=T.w(group), single=T.w(singular))
        return _pack(T, text, _shuffled(rng, [answer] + distractors), answer, T.p("hint_category"))
    if d == 2:
        people = rng.sample(NAMES, 3)
        pairs = " ".join(T.p("taller", a=T.w(a), b=T.w(b)) for a, b in zip(people, people[1:]))
        ask_tallest = rng.random() < 0.5
        answer = people[0] if ask_tallest else people[-1]
        choices = [answer] + [p for p in people if p != answer]
        word = "tallest" if ask_tallest else "shortest"
        text = f"{pairs} {T.p('who_is', word=T.w(word))}"
        return _pack(T, text, _shuffled(rng, choices), answer, T.p("hint_chain"))
    perm = rng.sample(NAMES, 4)                     # perm[0] is the tallest, perm[3] the shortest
    pairs = [T.p("taller", a=T.w(perm[i]), b=T.w(perm[i + 1])) for i in range(3)]
    rng.shuffle(pairs)
    if rng.random() < 0.5:
        answer, high, low, distractors = perm[1], perm[0], perm[2], [perm[0], perm[3]]
    else:
        answer, high, low, distractors = perm[2], perm[1], perm[3], [perm[0], perm[1]]
    question = T.p("between", low=T.w(low), high=T.w(high))
    return _pack(T, f"{' '.join(pairs)} {question}", _shuffled(rng, [answer] + distractors), answer,
                 T.p("hint_order"))


def _visual(rng, d, T):
    if d == 1:
        row = [rng.choice(SYMBOLS) for _ in range(6)]
        if "★" not in row:
            row[rng.randrange(6)] = "★"
        count = row.count("★")
        options = _shuffled(rng, [str(count), str(count + 1), str(count - 1)])
        return T.p("visual_row", sym="★", row=" ".join(row)), options, str(count), T.p("hint_row")
    if d == 2:
        if rng.random() < 0.5:
            a, b = rng.sample(list(SIDES), 2)
            total = SIDES[a] + SIDES[b]
            options = _shuffled(rng, [str(total), str(total + 1), str(total - 1)])
            return T.p("sides_sum", a=T.o(a).lower() if T.lang == "en" else T.w(a), b=T.o(b).lower() if T.lang == "en" else T.w(b)), options, str(total), T.p("hint_sides")
        s1, s2 = rng.sample(SYMBOLS, 2)
        row = [rng.choice(SYMBOLS) for _ in range(8)]
        answer = row.count(s1) + row.count(s2)
        distractors = [str(answer + 1), str(answer - 1) if answer >= 1 else str(answer + 2)]
        text = T.p("visual_two", s1=s1, s2=s2, row=" ".join(row))
        return text, _shuffled(rng, [str(answer)] + distractors), str(answer), T.p("hint_two")
    rows, cols = 3, 4
    grid = [[rng.choice(SYMBOLS) for _ in range(cols)] for _ in range(rows)]
    target = rng.choice(SYMBOLS)
    grid_text = " / ".join(" ".join(row) for row in grid)
    if rng.random() < 0.5:
        r = rng.randrange(rows)
        answer = grid[r].count(target)
        text = T.p("grid_row", grid=grid_text, t=target, r=r + 1)
    else:
        answer = sum(1 for row in grid for symbol in row if symbol != target)
        text = T.p("grid_not", grid=grid_text, t=target)
    distractors = [str(answer + 1), str(answer - 1) if answer >= 1 else str(answer + 2)]
    return text, _shuffled(rng, [str(answer)] + distractors), str(answer), T.p("hint_grid")


GENERATORS = {
    "memory": _memory, "attention": _attention, "language": _language,
    "sequencing": _sequencing, "reasoning": _reasoning, "visual": _visual,
}


def _render(n, attempt, lang):
    """One language's version of level n for one attempt. The random choices do not depend
    on the language, so every language gets the same structure and the same answer position."""
    domain = level_domain(n)
    difficulty = level_difficulty(n)
    rng = random.Random(n * 7919 + attempt * 104729)
    text, options, answer, hint = GENERATORS[domain](rng, difficulty, _Text(lang))
    return {"question_text": text, "options": list(options), "correct_answer": answer, "hint": hint}


def _is_valid(content):
    options = [o.casefold() for o in content["options"]]
    return (len(options) == 3 and len(set(options)) == 3
            and content["correct_answer"].casefold() in options)


_CACHE = None


def all_levels():
    """All 500 levels. Each English question text is unique, and every language has three
    distinct options with the answer among them. A level that fails is regenerated with the
    next deterministic seed. Each level has a 'translations' entry for Hindi and Tamil."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    levels, seen = [], set()
    for n in range(1, TOTAL_LEVELS + 1):
        for attempt in range(300):
            versions = {lang: _render(n, attempt, lang) for lang in LANGUAGE_CODES}
            key = versions["en"]["question_text"].casefold()
            if key not in seen and all(_is_valid(v) for v in versions.values()):
                seen.add(key)
                break
        else:
            raise RuntimeError(f"could not build a unique question for level {n}")
        english = versions["en"]
        levels.append({
            "level_number": n,
            "domain": level_domain(n),
            "difficulty": level_difficulty(n),
            "required_skill": required_skill(n),
            "question_text": english["question_text"],
            "options": english["options"],
            "correct_answer": english["correct_answer"],
            "correct_index": english["options"].index(english["correct_answer"]),
            "hint": english["hint"],
            "translations": {lang: versions[lang] for lang in ("hi", "ta")},
        })
    _CACHE = levels
    return levels


def build_level(n):
    """Deterministic content for level n (1-500)."""
    if not 1 <= n <= TOTAL_LEVELS:
        raise ValueError(f"level must be between 1 and {TOTAL_LEVELS}")
    return all_levels()[n - 1]


def localized(level, lang):
    """The question fields for one language. Falls back to English."""
    if lang in ("hi", "ta") and lang in level.get("translations", {}):
        return level["translations"][lang]
    return {"question_text": level["question_text"], "options": level["options"],
            "correct_answer": level["correct_answer"], "hint": level["hint"]}
