"""Define handlers for contact commands."""

from collections.abc import Iterable
from functools import partial

from rich.panel import Panel
from rich.table import Table

from assistant.contacts.address_book import AddressBook
from assistant.contacts.command_keys import ContactCommandKeys
from assistant.contacts.fields import Address, Birthday, Email, Phone
from assistant.contacts.keywords import get_keywords
from assistant.contacts.record import Record
from assistant.core.command import Command, MutationCommand
from assistant.core.exceptions import (
    AlreadyExistsError,
    ContactNotFoundError,
    PhoneExistsError,
    UsageError,
)
from assistant.core.input_error_decorator import input_error
from assistant.ui.views import (
    format_card,
    format_info,
    format_success,
    format_table,
)


def get_record(book: AddressBook, name: str) -> Record:
    """Return a contact or raise when it is missing."""
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError(name)
    return record


# Validates all fields first; modifies record only if everything is valid.
def add_contact_info(record: Record, args: list[str]) -> None:
    """Add validated details to a contact."""
    phone = args[0] if len(args) > 0 and args[0] != "-" else None
    email = args[1] if len(args) > 1 and args[1] != "-" else None
    birthday = args[2] if len(args) > 2 and args[2] != "-" else None
    plain_address = " ".join(args[3:]) if len(args) > 3 else None

    new_phone = Phone(phone) if phone else None
    new_email = Email(email) if email else None
    new_birthday = Birthday(birthday) if birthday else None
    new_address = Address(plain_address) if plain_address else None

    if new_phone and record.find_phone(new_phone.value):
        raise PhoneExistsError(new_phone.value, record.name.value)

    if new_phone:
        record.phones.append(new_phone)
    if new_email:
        record.email = new_email
    if new_birthday:
        record.birthday = new_birthday
    if new_address:
        record.address = new_address


@input_error
def add_contact(book: AddressBook, args: list[str]) -> Panel:
    """Add a contact or update an existing one."""
    name, *rest = args
    record = book.find(name)
    message = f"Контакт «{name}» оновлено."

    if record is None:
        record = Record(name)
        add_contact_info(record, rest)
        book.add_record(record)
        message = f"Контакт «{name}» додано."
    else:
        add_contact_info(record, rest)

    return format_success(message)


@input_error
def delete_contact(book: AddressBook, args: list[str]) -> Panel:
    """Delete a contact."""
    name, *_ = args
    book.delete(name)
    return format_success(f"Контакт {name} видалено.")


@input_error
def find_contact(book: AddressBook, args: list[str]) -> Table | Panel:
    """Find contacts matching a query."""
    query = " ".join(args).strip()
    if not query:
        raise UsageError(
            f"Використання: {ContactCommandKeys.FIND_CONTACT.value} <запит...>"
        )

    matches = book.search(query)
    if not matches:
        return format_info(f"Контактів за запитом «{query}» не знайдено.")
    return render_contacts_table(matches, "Результати пошуку")


def show_all_contacts(book: AddressBook, args: list[str]) -> Table | Panel:
    """Display all contacts."""
    if args:
        raise UsageError("Команда не приймає аргументів.")
    return render_contacts_table(book.values(), "Список усіх контактів")


def render_contacts_table(
    records: Iterable[Record], title: str
) -> Table | Panel:
    """Render contact records as a table."""
    headers = ["Імʼя", "Дата народження", "Телефон(и)", "Адреса", "Email"]
    rows = []
    for record in records:
        record_dict = record.to_dict()
        rows.append(
            [
                record_dict.get("name", "-") or "-",
                record_dict.get("birthday", "-") or "-",
                ", ".join(record_dict.get("phones", [])) or "-",
                record_dict.get("address", "-") or "-",
                record_dict.get("email", "-") or "-",
            ]
        )
    return format_table(title, headers, rows)


@input_error
def add_phone(book: AddressBook, args: list[str]) -> Panel:
    """Add a phone number to a contact."""
    name, phone, *_ = args
    record = get_record(book, name)
    record.add_phone(phone)
    return format_success(f"Номер телефону {phone} додано до контакту {name}")


@input_error
def show_phone(book: AddressBook, args: list[str]) -> Panel:
    """Display a contact's phone numbers."""
    if len(args) != 1:
        raise UsageError(
            "Вкажіть одне ім'я контакту (у лапках, якщо з пробілом)."
        )
    name = args[0]
    record = get_record(book, name)
    return format_card(
        f"Контакт: {name}",
        {"Телефони": record.show_all_phones()},
    )


@input_error
def change_phone(book: AddressBook, args: list[str]) -> Panel:
    """Replace a contact's phone number."""
    name, old_phone, new_phone, *_ = args
    record = get_record(book, name)
    record.edit_phone(old_phone, new_phone)
    return format_success("Номер телефону оновлено.")


@input_error
def delete_phone(book: AddressBook, args: list[str]) -> Panel:
    """Delete a contact's phone number."""
    name, phone, *_ = args
    record = get_record(book, name)
    record.delete_phone(phone)
    return format_success("Номер телефону видалено.")


@input_error
def add_birthday(book: AddressBook, args: list[str]) -> Panel:
    """Set a contact's birthday."""
    name, date, *_ = args
    record = get_record(book, name)
    record.add_birthday(date)
    return format_success("День народження додано.")


@input_error
def show_birthday(book: AddressBook, args: list[str]) -> Panel | str:
    """Display a contact's birthday."""
    name, *_ = args
    record = get_record(book, name)
    if record.birthday is None:
        return format_info("Дата народження не вказана")
    return format_card("Дата народження", {name: str(record.birthday)})


@input_error
def change_birthday(book: AddressBook, args: list[str]) -> Panel:
    """Replace a contact's birthday."""
    name = args[0]
    date = args[1]
    record = get_record(book, name)
    record.change_birthday(date)
    return format_success(f"Дату народження контакту {name} змінено")


@input_error
def delete_birthday(book: AddressBook, args: list[str]) -> Panel:
    """Remove a contact's birthday."""
    name = args[0]
    record = get_record(book, name)
    record.delete_birthday()
    return format_success("Дату народження видалено")


@input_error
def upcoming_birthdays(
    book: AddressBook, args: list[str] | None = None
) -> Table | Panel:
    """Display birthdays coming up within the selected period."""
    days = 7
    integer_error_message = "Кількість днів має бути цілим числом."
    if args:
        if len(args) != 1:
            raise UsageError(integer_error_message)
        try:
            days = int(args[0])
        except ValueError:
            raise UsageError(integer_error_message)

    weekdays = (
        "Понеділок",
        "Вівторок",
        "Середа",
        "Четвер",
        "Пʼятниця",
        "Субота",
        "Неділя",
    )
    title = "Найближчі дні народження"
    headers = [
        "Імʼя",
        "ДН",
        "День тижня",
        "Через (днів)",
        "Виповнюється",
        "Дата привітання",
    ]
    rows = [
        [
            item.name,
            item.birthday.strftime(Birthday.DATE_FORMAT),
            weekdays[item.birthday.weekday()],
            str(item.days_left),
            str(item.age),
            item.congratulation_date.strftime(Birthday.DATE_FORMAT),
        ]
        for item in book.get_upcoming_birthdays(days)
    ]

    return format_table(title, headers, rows)


@input_error
def add_email(book: AddressBook, args: list[str]) -> Panel:
    """Add an email address to a contact."""
    name, email, *_ = args
    record = get_record(book, name)
    if record.email is not None:
        raise AlreadyExistsError(
            f"У контакту {name} вже є email {record.email.value}. "
            "Щоб замінити, використайте "
            f"{ContactCommandKeys.CHANGE_EMAIL.value}."
        )
    record.add_email(email)
    return format_success(f"Email {email} додано до контакту {name}")


@input_error
def change_email(book: AddressBook, args: list[str]) -> Panel:
    """Replace a contact's email address."""
    name, email, *_ = args
    record = get_record(book, name)
    record.edit_email(email)
    return format_success(f"Email контакту {name} змінено на {email}")


@input_error
def delete_email(book: AddressBook, args: list[str]) -> Panel:
    """Remove a contact's email address."""
    name, *_ = args
    record = get_record(book, name)
    record.delete_email()
    return format_success(f"Email контакту {name} видалено")


def parse_name_and_address(args: list[str]) -> tuple[str, str]:
    """Parse a contact name and address from arguments."""
    name, *rest = args
    if not rest:
        raise UsageError("Недостатньо аргументів.")
    return name, " ".join(rest)


@input_error
def add_address(book: AddressBook, args: list[str]) -> Panel:
    """Add an address to a contact."""
    name, address = parse_name_and_address(args)
    record = get_record(book, name)
    if record.address is not None:
        raise AlreadyExistsError(
            f"У контакту {name} вже є адреса. "
            "Щоб замінити, використайте "
            f"{ContactCommandKeys.CHANGE_ADDRESS.value}."
        )
    record.add_address(address)
    return format_success(f"Адресу контакту {name} додано: {address}")


@input_error
def change_address(book: AddressBook, args: list[str]) -> Panel:
    """Replace a contact's address."""
    name, address = parse_name_and_address(args)
    record = get_record(book, name)
    record.edit_address(address)
    return format_success(f"Адресу контакту {name} змінено на: {address}")


@input_error
def delete_address(book: AddressBook, args: list[str]) -> Panel:
    """Remove a contact's address."""
    name, *_ = args
    record = get_record(book, name)
    record.delete_address()
    return format_success(f"Адресу контакту {name} видалено")


# Complete logic for prompt showing suggestions


def complete_contact_name(book: AddressBook, args: list[str]) -> list[str]:
    """Suggest contact names for command input."""
    if len(args) == 0:
        return sorted(book.data.keys())
    return []


def complete_name_and_phone(book: AddressBook, args: list[str]) -> list[str]:
    """Suggest contact names or their phone numbers."""
    if len(args) == 0:
        return sorted(book.data.keys())

    if len(args) == 1:
        record = book.find(args[0])
        if record:
            return [phone.value for phone in record.phones]

    return []


def build_commands(book: AddressBook) -> dict[str, Command]:
    """Build the contact command definitions."""
    return {
        ContactCommandKeys.ADD_CONTACT: MutationCommand(
            handler=partial(add_contact, book),
            usage=(
                f"{ContactCommandKeys.ADD_CONTACT.value} <ім'я> [телефон] "
                "[email] [ДД.ММ.РРРР] [адреса]"
            ),
            description=(
                "Додати контакт або оновити існуючий "
                "('-' для пропуску поля, напр.: "
                f"{ContactCommandKeys.ADD_CONTACT.value} Anna - a@m.com; "
                'імʼя з пробілом — у лапках: "Anna Petrenko")'
            ),
            category="Contacts",
            example=(
                f"{ContactCommandKeys.ADD_CONTACT.value} Anna 0501234567 "
                "anna@mail.com 15.03.1995 Київ"
            ),
            keywords=get_keywords(ContactCommandKeys.ADD_CONTACT),
        ),
        ContactCommandKeys.DELETE_CONTACT: MutationCommand(
            handler=partial(delete_contact, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=f"{ContactCommandKeys.DELETE_CONTACT.value} <ім'я>",
            description="Видалити контакт із книги",
            category="Contacts",
            example=f"{ContactCommandKeys.DELETE_CONTACT.value} Anna",
            keywords=get_keywords(ContactCommandKeys.DELETE_CONTACT),
        ),
        ContactCommandKeys.FIND_CONTACT: Command(
            handler=partial(find_contact, book),
            usage=f"{ContactCommandKeys.FIND_CONTACT.value} <запит...>",
            description=(
                "Знайти контакти за іменем, телефоном, email, "
                "адресою або датою народження"
            ),
            category="Contacts",
            example=f"{ContactCommandKeys.FIND_CONTACT.value} Anna",
            keywords=get_keywords(ContactCommandKeys.FIND_CONTACT),
        ),
        ContactCommandKeys.SHOW_ALL_CONTACTS: Command(
            handler=partial(show_all_contacts, book),
            usage=ContactCommandKeys.SHOW_ALL_CONTACTS.value,
            description="Показати всі збережені контакти",
            category="Contacts",
            example=ContactCommandKeys.SHOW_ALL_CONTACTS.value,
            keywords=get_keywords(ContactCommandKeys.SHOW_ALL_CONTACTS),
        ),
        ContactCommandKeys.ADD_PHONE: MutationCommand(
            handler=partial(add_phone, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=f"{ContactCommandKeys.ADD_PHONE.value} <ім'я> <телефон>",
            description="Додати додатковий номер телефону до контакту",
            category="Contacts",
            example=f"{ContactCommandKeys.ADD_PHONE.value} Anna 0507654321",
            keywords=get_keywords(ContactCommandKeys.ADD_PHONE),
        ),
        ContactCommandKeys.SHOW_PHONE: Command(
            handler=partial(show_phone, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=f"{ContactCommandKeys.SHOW_PHONE.value} <ім'я>",
            description="Показати інформацію та телефони контакту",
            category="Contacts",
            example=f"{ContactCommandKeys.SHOW_PHONE.value} Anna",
            keywords=get_keywords(ContactCommandKeys.SHOW_PHONE),
        ),
        ContactCommandKeys.CHANGE_PHONE: MutationCommand(
            handler=partial(change_phone, book),
            arg_completer=lambda args: complete_name_and_phone(book, args),
            usage=(
                f"{ContactCommandKeys.CHANGE_PHONE.value} "
                "<ім'я> <старий_телефон> <новий_телефон>"
            ),
            description="Змінити існуючий номер телефону контакту",
            category="Contacts",
            example=(
                f"{ContactCommandKeys.CHANGE_PHONE.value} "
                "Anna 0501234567 0509998877"
            ),
            keywords=get_keywords(ContactCommandKeys.CHANGE_PHONE),
        ),
        ContactCommandKeys.DELETE_PHONE: MutationCommand(
            handler=partial(delete_phone, book),
            arg_completer=lambda args: complete_name_and_phone(book, args),
            usage=f"{ContactCommandKeys.DELETE_PHONE.value} <ім'я> <телефон>",
            description="Видалити номер телефону у контакту",
            category="Contacts",
            example=f"{ContactCommandKeys.DELETE_PHONE.value} Anna 0501234567",
            keywords=get_keywords(ContactCommandKeys.DELETE_PHONE),
        ),
        ContactCommandKeys.ADD_BIRTHDAY: MutationCommand(
            handler=partial(add_birthday, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=(
                f"{ContactCommandKeys.ADD_BIRTHDAY.value} "
                "<ім'я> <дн - ДД.ММ.РРРР>"
            ),
            description="Додати день народження до контакту",
            category="Contacts",
            example=(
                f"{ContactCommandKeys.ADD_BIRTHDAY.value} Anna 15.03.1995"
            ),
            keywords=get_keywords(ContactCommandKeys.ADD_BIRTHDAY),
        ),
        ContactCommandKeys.SHOW_BIRTHDAY: Command(
            handler=partial(show_birthday, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=f"{ContactCommandKeys.SHOW_BIRTHDAY.value} <ім'я>",
            description="Показати день народження контакту",
            category="Contacts",
            example=f"{ContactCommandKeys.SHOW_BIRTHDAY.value} Anna",
            keywords=get_keywords(ContactCommandKeys.SHOW_BIRTHDAY),
        ),
        ContactCommandKeys.CHANGE_BIRTHDAY: MutationCommand(
            handler=partial(change_birthday, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=(
                f"{ContactCommandKeys.CHANGE_BIRTHDAY.value} "
                "<ім'я> <дн - ДД.ММ.РРРР>"
            ),
            description="Змінити день народження контакту",
            category="Contacts",
            example=(
                f"{ContactCommandKeys.CHANGE_BIRTHDAY.value} Anna 20.04.1996"
            ),
            keywords=get_keywords(ContactCommandKeys.CHANGE_BIRTHDAY),
        ),
        ContactCommandKeys.DELETE_BIRTHDAY: MutationCommand(
            handler=partial(delete_birthday, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=f"{ContactCommandKeys.DELETE_BIRTHDAY.value} <ім'я>",
            description="Видалити день народження у контакту",
            category="Contacts",
            example=f"{ContactCommandKeys.DELETE_BIRTHDAY.value} Anna",
            keywords=get_keywords(ContactCommandKeys.DELETE_BIRTHDAY),
        ),
        ContactCommandKeys.UPCOMING_BIRTHDAYS: Command(
            handler=partial(upcoming_birthdays, book),
            usage=f"{ContactCommandKeys.UPCOMING_BIRTHDAYS.value} [дні=7]",
            description="Показати дні народження в межах заданого періоду",
            category="Contacts",
            example=f"{ContactCommandKeys.UPCOMING_BIRTHDAYS.value} 14",
            keywords=get_keywords(ContactCommandKeys.UPCOMING_BIRTHDAYS),
        ),
        ContactCommandKeys.ADD_EMAIL: MutationCommand(
            handler=partial(add_email, book),
            usage=f"{ContactCommandKeys.ADD_EMAIL.value} <ім'я> <email>",
            arg_completer=lambda args: complete_contact_name(book, args),
            description="Додати email до контакту",
            category="Contacts",
            example=f"{ContactCommandKeys.ADD_EMAIL.value} Anna anna@mail.com",
            keywords=get_keywords(ContactCommandKeys.ADD_EMAIL),
        ),
        ContactCommandKeys.CHANGE_EMAIL: MutationCommand(
            handler=partial(change_email, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=(
                f"{ContactCommandKeys.CHANGE_EMAIL.value} <ім'я> <новий_email>"
            ),
            description="Змінити email контакту",
            category="Contacts",
            example=(
                f"{ContactCommandKeys.CHANGE_EMAIL.value} Anna new@mail.com"
            ),
            keywords=get_keywords(ContactCommandKeys.CHANGE_EMAIL),
        ),
        ContactCommandKeys.DELETE_EMAIL: MutationCommand(
            handler=partial(delete_email, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=f"{ContactCommandKeys.DELETE_EMAIL.value} <ім'я>",
            description="Видалити email у контакту",
            category="Contacts",
            example=f"{ContactCommandKeys.DELETE_EMAIL.value} Anna",
            keywords=get_keywords(ContactCommandKeys.DELETE_EMAIL),
        ),
        ContactCommandKeys.ADD_ADDRESS: MutationCommand(
            handler=partial(add_address, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=f"{ContactCommandKeys.ADD_ADDRESS.value} <ім'я> <адреса...>",
            description="Додати адресу до контакту",
            category="Contacts",
            example=(
                f"{ContactCommandKeys.ADD_ADDRESS.value} "
                "Anna Київ, вул. Хрещатик 1"
            ),
            keywords=get_keywords(ContactCommandKeys.ADD_ADDRESS),
        ),
        ContactCommandKeys.CHANGE_ADDRESS: MutationCommand(
            handler=partial(change_address, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=(
                f"{ContactCommandKeys.CHANGE_ADDRESS.value} "
                "<ім'я> <нова_адреса...>"
            ),
            description="Змінити адресу контакту",
            category="Contacts",
            example=(
                f"{ContactCommandKeys.CHANGE_ADDRESS.value} "
                "Anna Львів, пл. Ринок 5"
            ),
            keywords=get_keywords(ContactCommandKeys.CHANGE_ADDRESS),
        ),
        ContactCommandKeys.DELETE_ADDRESS: MutationCommand(
            handler=partial(delete_address, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage=f"{ContactCommandKeys.DELETE_ADDRESS.value} <ім'я>",
            description="Видалити адресу у контакту",
            category="Contacts",
            example=f"{ContactCommandKeys.DELETE_ADDRESS.value} Anna",
            keywords=get_keywords(ContactCommandKeys.DELETE_ADDRESS),
        ),
    }
