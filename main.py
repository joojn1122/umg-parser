from convert import convert, replace_file

if __name__ == "__main__":
    with open("ui.txt", "r", encoding="utf-8") as f:
        ui = f.read()

    result = convert(ui, 2)

    with open("result.verse", "w", encoding="utf-8") as f:
        f.write(result)

    replace_file(
        r"C:\Users\joojn\Documents\Fortnite Projects\HackerTycoon\Plugins\HackerTycoon\Content\Screens\HackingScreen.verse",
        result,
        "# -- HACKING PEOPLE UI -- #",
        "# -- END HACKING PEOPLE UI -- #"
    )

    # replace_file(
    # r"C:\Users\joojn\Documents\Fortnite Projects\HackerTycoon\Plugins\HackerTycoon\Content\Screens\BtcSellScreen.verse", 
    # result, 
    # "# -- BTC SELL UI -- #", 
    # "# -- END BTC SELL UI -- #"
    # )

    # replace_file(
    # r"C:\Users\joojn\Documents\Fortnite Projects\HackerTycoon\Plugins\HackerTycoon\Content\Screens\CheatMenu.verse", 
    # result, 
    # "# -- CHEAT MENU UI -- #", 
    # "# -- END CHEAT MENU UI -- #"
    # )
