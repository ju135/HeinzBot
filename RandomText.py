import random


def get_random_ask_answer() -> str:
    return get_random_string([
        "Wahrscheinlich scho..",
        "Knacki sogt er waß ned.",
        "Joooooooooo",
        "Na, sunst no wos.",
        "Na\ntülrich\nnicht",
        "Blede frog.",
        "Sog i da ned.",
        "Computer sagt nein.",
        "Sowieso.",
        "Jep.",
        "```ERROR - Signal: SIGBRT```",
        "null",
        "Nope.",
        "Hot da knicki a knack?",
        "Frog sptäter no amol.",
        "Hot da knicki ka knack?",
        "Wahrscheinlich ned..",
        "I hätt scho gsogt.",
        "Do redest mit da Glaskugel.",
        "Nur wenn da schneestial no vorm Teichhaus steht.",
        "Negativ, Kamerad!",
        "Positiv, Kamerad!",
        "De Frog is so oid wie en Krösche sei Stoff.",
        "Eh kloa.",
        "Fix!",
        "Jo frali, wos glaubstn du?!",
        "Und wegn so am Scheiß weckst mi vom Mittagsschlaferl auf?! Na, natürlich ned!",
        "Und wegn so am Scheiß weckst mi vom Mittagsschlaferl auf?! Fix du Sack!",
        "Wenn i meine Signale richtig filtere, ergibt de FFT davon a \"ja\".",
        "Wenn i meine Signale richtig filtere, ergibt de FFT davon a \"nein\".",
        "Jo zu 10000%",
        "Jo do bin i ma sicha.",
        "I bin spitzless. Jo!",
        "public boolean Heinz::ask(void) {\n    return false;\n}",
        "public boolean Heinz::ask(void) {\n    return true;\n}",
        "Error 404 - Answer not found Exception.",
        "JO!",
        "NA!",
        "Frog mi höflich noamol.",
        "Ich habe heute leider kein ja für dich.",
        "JoOoOoooOooOOoo!!!111!!11!!1!!!1",
        "Mei Play - Doh - Pyramide is rot, deswegen nein.",
        "Mei Play - Doh - Pyramide is blau, deswegen ja.",
        "Mei Spaghettiturm is da hechste, oiso jo."
    ])


def get_random_quote_text() -> str:
    return get_random_string([
        "Quote of the day - hobts an schenan tog. :)",
        "qotd, bg hb.",
        "as heutige zitat.",
        "As heutige Zitat ~ BG HB",
        "***QUOTE OF THE DAY*** ***QUOTE OF THE DAY*** ***QUOTE OF THE DAY*** BG WM",
        "Hob wieder a zitat für eich.",
        "Heitiges Zitat",
        "Quote",
        "Zitat des Tages.",
        "Zitat von Heinz.",
        "Hört, hört.",
        "Zitat eines weisen Menschen.",
        "Error! Exception in 'QuoteGenerator.asm': Sent quote may be meaningless."
    ])


def get_random_free_text() -> str:
    return get_random_string([
        "Ich habe heute leider kein Appointment für euch.",
        "Keine Vorlesung heute.",
        "gg wp",
        "schlofts eich aus, weil heit is frei.",
        "Für heit steht nix im Kalender.",
        "Heite hobts frei.",
        "Schenan FH-freien tog wünsch i eich."
    ])


def get_random_string(l: [str]) -> str:
    return l[random.randint(0, len(l)-1)]