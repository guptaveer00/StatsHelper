"""Stats Helper: run with python app.py."""
import argparse
import textwrap

from study import StudyHelper, WEAK_DISTANCE, body_text, save_guide, source_label


def show_guide(guide):
    if not guide.matches:
        print("\nNo close matches. Try a more specific statistics question, or add a note.")
        return
    print(f"\nSTUDY GUIDE: {guide.query}")
    print("Read these sources, then use option 3 to practice recalling them.")
    print("These are excerpts, not an AI-written explanation. Check formulas in the PDF.")
    for index, (match, sentence) in enumerate(zip(guide.matches, guide.key_sentences), 1):
        print(f"\n{index}. {source_label(match)}")
        print(f"   Distance {match.distance:.3f} (lower is closer, not a confidence percentage)")
        if match.distance >= WEAK_DISTANCE:
            print("   Weak match: check relevance before studying this passage.")
        if sentence:
            print(textwrap.fill("Key sentence: " + sentence, width=88))
        else:
            print("No clean complete sentence available; read the source passage.")
        print(textwrap.fill("Passage: " + body_text(match.text), width=88))
    print("\nFor each source: explain how it answers your question and name one limitation.")
    print(f"{len(guide.cards)} recall card(s) ready. Option 5 saves the guide with source links.")


def add_note(helper):
    print("\nADD A NOTE (leave title blank to cancel)")
    title = input("Title: ").strip()
    if not title:
        return
    print("Paste your note. Finish with a single period (.) on its own line.")
    lines = []
    while True:
        line = input()
        if line.strip() == ".":
            break
        lines.append(line)
        if sum(len(s) + 1 for s in lines) > 30000:
            raise ValueError("Note is too long. Please try a shorter note.")
    ids = helper.add_note(title, "\n".join(lines))
    print(f"Saved in {len(ids)} searchable chunk(s). You can search it now.")


def practice(guide):
    if guide is None or not guide.cards:
        print("Make a guide with readable source sentences first (option 1).")
        return
    correct = 0
    for index, card in enumerate(guide.cards, 1):
        print(f"\nCard {index}/{len(guide.cards)} — {card.source}")
        print(textwrap.fill(card.prompt, width=88))
        input("Think of the missing word, then press Enter to reveal: ")
        print("Source word:", card.answer)
        response = input("Did you recall it? [y/N]: ").strip().lower()
        correct += response == "y"
    print(f"\nYou marked {correct}/{len(guide.cards)} recalled. Revisit the others in the PDF.")


def menu(helper):
    last_guide = None
    while True:
        print("\n--- STATS HELPER ---")
        print("1. Make a study guide\n2. Add a note\n3. Practice last guide")
        print("4. Library status\n5. Save last guide\n0. Quit")
        choice = input("Choose: ").strip()
        try:
            if choice == "0":
                print("Your textbook and notes are saved locally. See you next time!")
                return
            if choice == "1":
                query = input("What are you confused about? ")
                scope_input = input("Search [a]ll, [t]extbook, or [n]otes? [a]: ").strip().lower()
                if scope_input not in ("", "a", "t", "n"):
                    raise ValueError("Choose a, t, or n.")
                scope = {"": "all", "a": "all", "t": "textbook", "n": "notes"}[scope_input]
                last_guide = helper.make_guide(query, scope)
                show_guide(last_guide)
            elif choice == "2":
                add_note(helper)
            elif choice == "3":
                practice(last_guide)
            elif choice == "4":
                counts = helper.status()
                print(f"Textbook passages: {counts['textbook_passages']}")
                print(f"Your notes: {counts['notes']} ({counts['note_chunks']} chunks)")
            elif choice == "5":
                if last_guide is None:
                    print("Make a study guide first (option 1).")
                else:
                    print("Saved:", save_guide(last_guide))
            else:
                print("Choose one of the menu numbers.")
        except ValueError as error:
            print("Please try again:", error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", help="Make one guide without opening the menu")
    parser.add_argument("--scope", choices=["all", "textbook", "notes"], default="all")
    parser.add_argument("--save", action="store_true", help="Save the one-query guide")
    args = parser.parse_args()
    helper = StudyHelper()
    try:
        if args.query is not None:
            guide = helper.make_guide(args.query, args.scope)
            show_guide(guide)
            if args.save:
                print("Saved:", save_guide(guide))
        else:
            print("Stats Helper — free, local textbook search and recall practice")
            if helper.status()["textbook_passages"] == 0:
                print("Textbook not loaded. See README for the download/extract/load commands.")
                print("You can still add and search your own notes.")
            menu(helper)
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye. Previously saved notes remain on disk.")
    except ValueError as error:
        parser.exit(2, f"{error}\n")


if __name__ == "__main__":
    main()
