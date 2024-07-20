from convert import convert, replace_file

if __name__ == "__main__":
    with open("ui.txt", "r") as f:
        ui = f.read()

    result = convert(ui, 1)

    with open("result.verse", "w") as f:
        f.write(result)

    # replace_file(
    # r"C:\Users\joojn\Documents\Fortnite Projects\HackerTycoon\Plugins\HackerTycoon\Content\Screens\BtcSellScreen.verse", 
    # result, 
    # "CloseBtn := button_loud", 
    # "Screen := btc_exchange_screen"
    # )

    exit()
    replace_file(
    r"C:\Users\joojn\Documents\Fortnite Projects\HackerTycoon\Plugins\HackerTycoon\Content\Screens\CheatMenu.verse", 
    result, 
    "LegitStackBox := stack_box", 
    "Screen :="
    )
