from statemachine import FSM, State
from typing import List

def run_console() -> None:
    print("Hello, welcome to B2's restaurant finder!\n Before starting to collect your preference about restaurants, we wish to ask you to select the configurability options that best suits you.\n\n")
    print("1: if you wish the system to always reply in CAPSLOCK, digit 'allcaps'\n")
    print("2: if you wish the system to delay is answers by 3 seconds, digit 'delay'\n")
    print("3: if you wish the system to classify your utterance based on a baseline instead of using a machine learning model, digit'baseline'\n")
    print("4: if you wish the system to reply with an informal tone, digit 'informal'\n")
    print("You can choose multiple configurability at once, or also none of them\n")

    tokens: List[str] = input().lower().split()

    if "delay" in tokens:
        delay: bool = True
        print("delay mode on")
    else:
        delay = False

    if "baseline" in tokens:
        baseline: bool = True
        print("baseline mode on")
    else:
        baseline = False

    if "informal" in tokens:
        informal: bool = True
        print("informal mode on")
    else:
        informal = False

    if "allcaps" in tokens:
        allcaps: bool = True
        print("\nALLCAPS MODE ON")
    else:
        allcaps = False

    # create the fsm object based on the user input
    fsm: FSM = FSM(all_caps_config=allcaps, delay_config=delay, baseline_config=baseline, informal_config=informal)
    if allcaps:
        print(fsm.get_prompt().upper())
    else:
        print(fsm.get_prompt())

    try:
        while fsm.current_state != State.EXIT:
            user_input: str = input("> ")
            lowered_user_input = user_input.lower()
            reply = fsm.handle_input(lowered_user_input)
            if reply:
                print(reply)
    except KeyboardInterrupt:
        print("\nExiting. Bye!")

if __name__ == "__main__":
    run_console()
