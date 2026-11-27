from assistant.general.command_keys import GeneralCommandKeys

EXIT_KEYWORDS: tuple[str, ...] = (
    "вийти",
    "вихід",
    "закрий",
    "закрити",
    "завершити",
    "заверши",
    "бувай",
    "прощавай",
    "до побачення",
    "вийти з програми",
    "завершити роботу",
    "exit",
    "close",
    "quit",
    "bye",
    "goodbye",
    "good bye",
    "exit program",
    "quit application",
)

HELLO_KEYWORDS: tuple[str, ...] = (
    "привіт",
    "вітаю",
    "здрастуй",
    "добрий день",
    "добрий ранок",
    "добрий вечір",
    "hello",
    "hi",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
)

HELP_KEYWORDS: tuple[str, ...] = (
    "допомога",
    "допоможи",
    "команди",
    "інструкція",
    "підказка",
    "можливості",
    "потрібна допомога",
    "покажи команди",
    "всі команди",
    "доступні команди",
    "як користуватися",
    "що ти вмієш",
    "help",
    "commands",
    "instructions",
    "usage",
    "help me",
    "show commands",
    "available commands",
    "all commands",
    "need help",
)

CLOSE_KEYWORDS: tuple[str, ...] = (
    "закрий",
    "закрити",
    "заверши",
    "завершити",
    "закрий програму",
    "закрити програму",
    "закрий асистента",
    "закрити застосунок",
    "close",
    "shutdown",
    "finish",
    "close program",
    "close application",
    "close assistant",
)

GENERAL_KEYWORDS: dict[GeneralCommandKeys, tuple[str, ...]] = {
    GeneralCommandKeys.HELLO: HELLO_KEYWORDS,
    GeneralCommandKeys.HELP: HELP_KEYWORDS,
    GeneralCommandKeys.CLOSE: CLOSE_KEYWORDS,
    GeneralCommandKeys.EXIT: EXIT_KEYWORDS,
}


def get_keywords(command: GeneralCommandKeys) -> tuple[str, ...]:
    return GENERAL_KEYWORDS.get(command, ())
