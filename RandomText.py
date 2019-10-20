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

def get_random_coffee_starter() -> str:
    return get_random_string([
        "En $ gustats nach am Kaffee!",
        "$ hätte Appettit auf ein koffeeinhaltiges Heißgetränk.",
        "Zahts wen Kaffee? $ frogat.",
        "Die Bohnen rufen! Frogts en $, dea hods a ghead!",
        "Covfefe! ☕",
        "Er wärmt von innen, er wärmt von außen, er sozialisiert alle Studenten da draußen. $ dad a Kaffee zahn!",
        "☕? $ frogt."
    ])

ends = {
    "host": 
        ["Wie wads mid TOP $?",
        "Treff ma uns in TOP $?",
        "Er gabat an aus in TOP $.",
        "Hört hört, der Veranstaltungsort beläuft sich auf TOP № $.",
        "Irgendwie ziagts mi zu $.",
        '''Heads ia des? I glaub es is Halloween. Do hea i a paar Geister rufen, "Kuuuuumds zu $!". Es a?''',
        "I glaub d'Kaffeemaschin' in TOP $ rennd scho.",
        "De Kaffeemaschin' aus TOP $ hea i bis do auffa, i glaub do gibts boid an.",
        "Trompeter bitte indn Partyraum. Kaffeetrinker bitte in TOP $."],
    "other":
        ["Gibts in dem Haus irgendwo Kaffeemaschinen?",
        "Zahts wen hosten?",
        "GET /coffeeLocation.html HTTP/1.1\nServer: Du?",
        "Wo soin ma?",
        "Hod wea an Kaffee fia de armen Studenten?"],
    "FH":
        ["Ob en Julian sei Chip nu wos draufhat?",
        "Hod da Julian zufällig sein Chip aufgladn?",
        "Wo is do da nächste Automat in da FH?",
        "Man lasset die FH-Plastikbecher klingen.",
        "A irish coffee in da FH wad a wos. Is do eig Rum drin?"
        ]
}
def get_random_coffee_end(type) -> str:
    return get_random_string(ends[type])


def get_random_string(l: [str]) -> str:
    return l[random.randint(0, len(l)-1)]