import sys

# Training Limit = 5-4% des Vermögens
# Stop Limit setzen in der Regel 60%, soll aber aber zu viel sein
# Wenn der Kurs noch weiter fällt soll der bot nachkaufen…
# Er soll gleiche traidmenge nochmal für weniger Geld nachkaufen
# Max 3mal nachkaufen
#bitfinex nicht ideal, weil immer 0,2% fee --> insgesamt 0,4
# es ist schwerer die richtige Strategie auszuwählen
# HH und LL (Highes High and Lowest Low) und den RSI.
run = False

def starting_the_TradingBot():
    global run
    run = True
    main()


def stopping_the_TradingBot():
    global run
    run = False
    main()


def tradingBot_sate():
    if run == True:
        return "running"
    elif run == False:
        return "not running"


def get_results():
    kontostand = "KontoStand: " + str(0) + "€"
    GuV = "In Prozent Gewinne/Verluste: " + str(0) + "%"
    other = "And so on..."

    results = kontostand + "\n" + GuV + "\n" + other

    return results


def main():
    while run:
        print("...2")

    if run == False:
        print("Stopped vcv")
