from collections.abc import Iterable
from functools import partial
from typing import Any

from rich.panel import Panel
from rich.table import Table

from assistant.contacts.address_book import AddressBook
from assistant.contacts.record import Record
from assistant.core.command import Command, MutationCommand
from assistant.core.exceptions import (
    AlreadyExistsError,
    ContactNotFoundError,
    PhoneExistsError,
    UsageError,
)
from assistant.core.fields import Address, Birthday, Email, Phone
from assistant.core.input_error_decorator import input_error
from assistant.ui.views import (
    format_card,
    format_info,
    format_success,
    format_table,
)


def get_record(book: AddressBook, name: str) -> Record:
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError(name)
    return record


# Validates all fields first; modifies record only if everything is valid.
def add_contact_info(record: Record, args: list[str]) -> None:
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
    name, *rest = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        add_contact_info(record, rest)
        book.add_record(record)
        message = "Contact added."
    else:
        add_contact_info(record, rest)

    return format_success(message)


@input_error
def delete_contact(book: AddressBook, args: list[str]) -> Panel:
    name, *_ = args
    book.delete(name)
    return format_success(f"Contact {name} deleted.")


@input_error
def find_contact(book: AddressBook, args: list[str]) -> Table | Panel:
    query = " ".join(args).strip()
    if not query:
        raise UsageError("Використання: find-contact <запит...>")

    matches = book.search(query)
    if not matches:
        return format_info(f"Контактів за запитом «{query}» не знайдено.")
    return render_contacts_table(matches, "Результати пошуку")


def show_all_contacts(book: AddressBook, *_: Any) -> Table | Panel:
    return render_contacts_table(book.values(), "Список усіх контактів")


def render_contacts_table(
    records: Iterable[Record], title: str
) -> Table | Panel:
    headers = ["Імʼя", "Дата народження", "Телефон(и)", "Адреса", "Пошта"]
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
    name, phone, *_ = args
    record = get_record(book, name)
    record.add_phone(phone)
    return format_success(f"Номер телефону {phone} додано до контакту {name}")


@input_error
def show_phone(book: AddressBook, args: list[str]) -> Panel:
    name = args[0]
    record = get_record(book, name)
    return format_card(
        f"Контакт: {name}",
        {"Телефони": record.show_all_phones()},
    )


@input_error
def change_phone(book: AddressBook, args: list[str]) -> Panel:
    name, old_phone, new_phone, *_ = args
    record = get_record(book, name)
    record.edit_phone(old_phone, new_phone)
    return format_success("Phone updated.")


@input_error
def delete_phone(book: AddressBook, args: list[str]) -> Panel:
    name, phone, *_ = args
    record = get_record(book, name)
    record.delete_phone(phone)
    return format_success("Phone deleted.")


@input_error
def add_birthday(book: AddressBook, args: list[str]) -> Panel:
    name, date, *_ = args
    record = get_record(book, name)
    record.add_birthday(date)
    return format_success("Birthday added.")


@input_error
def show_birthday(book: AddressBook, args: list[str]) -> Panel | str:
    name, *_ = args
    record = get_record(book, name)
    if record.birthday is None:
        return format_info("Дата народження не вказана")
    return format_card("Дата народження", {name: str(record.birthday)})


@input_error
def change_birthday(book: AddressBook, args: list[str]) -> Panel:
    name = args[0]
    date = args[1]
    record = get_record(book,name)
    record.change_birthday(date)
    return format_success(f"Дату народження контакту {name} змінено")


@input_error
def delete_birthday(book: AddressBook, args: list[str]) -> Panel:
    name = args[0]
    record = get_record(book, name)
    record.delete_birthday()
    return format_success("Дату народження видалено")


def upcoming_birthdays(
    book: AddressBook, args: list[str] | None = None
) -> Table | Panel:
    title = "Список найближчих днів народжень"
    headers = ["Імʼя", "Дата народження"]
    rows = [
        [
            upcoming_bd.get("name", "-"),
            upcoming_bd.get("congratulation_date", "-"),
        ]
        for upcoming_bd in book.get_upcoming_birthdays()
    ]

    return format_table(title, headers, rows)


@input_error
def add_email(book: AddressBook, args: list[str]) -> Panel:
    name, email, *_ = args
    record = get_record(book, name)
    if record.email is not None:
        raise AlreadyExistsError(
            f"У контакту {name} вже є email {record.email.value}. "
            f"Щоб замінити, використайте change-email."
        )
    record.add_email(email)
    return format_success(f"Email {email} додано до контакту {name}")


@input_error
def change_email(book: AddressBook, args: list[str]) -> Panel:
    name, email, *_ = args
    record = get_record(book, name)
    record.edit_email(email)
    return format_success(f"Email контакту {name} змінено на {email}")


@input_error
def delete_email(book: AddressBook, args: list[str]) -> Panel:
    name, *_ = args
    record = get_record(book, name)
    record.delete_email()
    return format_success(f"Email контакту {name} видалено")


def parse_name_and_address(args: list[str]) -> tuple[str, str]:
    name, *rest = args
    if not rest:
        raise UsageError("Недостатньо аргументів.")
    return name, " ".join(rest)


@input_error
def add_address(book: AddressBook, args: list[str]) -> Panel:
    name, address = parse_name_and_address(args)
    record = get_record(book, name)
    if record.address is not None:
        raise AlreadyExistsError(
            f"У контакту {name} вже є адреса. "
            f"Щоб замінити, використайте change-address."
        )
    record.add_address(address)
    return format_success(f"Адресу контакту {name} додано: {address}")


@input_error
def change_address(book: AddressBook, args: list[str]) -> Panel:
    name, address = parse_name_and_address(args)
    record = get_record(book, name)
    record.edit_address(address)
    return format_success(f"Адресу контакту {name} змінено на: {address}")


@input_error
def delete_address(book: AddressBook, args: list[str]) -> Panel:
    name, *_ = args
    record = get_record(book, name)
    record.delete_address()
    return format_success(f"Адресу контакту {name} видалено")


# Complete logic for prompt showing suggestions


def complete_contact_name(book: AddressBook, args: list[str]) -> list[str]:
    if len(args) == 0:
        return sorted(book.data.keys())
    return []


def complete_name_and_phone(book: AddressBook, args: list[str]) -> list[str]:
    if len(args) == 0:
        return sorted(book.data.keys())

    if len(args) == 1:
        record = book.find(args[0])
        if record:
            return [phone.value for phone in record.phones]

    return []


def build_contacts_commands(book: AddressBook) -> dict[str, Command]:
    return {
        "add-contact": MutationCommand(
            handler=partial(add_contact, book),
            usage=(
                "add-contact <ім'я> [телефон] [email] [ДД.ММ.РРРР] [адреса]"
            ),
            description=(
                "Додати контакт або оновити існуючий "
                "('-' для пропуску поля, напр.: add-contact Anna - a@m.com; "
                'імʼя з пробілом — у лапках: "Anna Petrenko")'
            ),
            category="Contacts",
            example="add-contact Anna 0501234567 anna@mail.com 15.03.1995 "
            "Київ",
        ),
        "delete-contact": MutationCommand(
            handler=partial(delete_contact, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="delete-contact <ім'я>",
            description="Видалити контакт із книги",
            category="Contacts",
            example="delete-contact Anna",
        ),
        "find-contact": Command(
            handler=partial(find_contact, book),
            usage="find-contact <запит...>",
            description=(
                "Знайти контакти за іменем, телефоном, email, "
                "адресою або датою народження"
            ),
            category="Contacts",
            example="find-contact Anna",
        ),
        "show-all-contacts": Command(
            handler=partial(show_all_contacts, book),
            usage="show-all-contacts",
            description="Показати всі збережені контакти",
            category="Contacts",
            example="show-all-contacts",
        ),
        "add-phone": MutationCommand(
            handler=partial(add_phone, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="add-phone <ім'я> <телефон>",
            description="Додати додатковий номер телефону до контакту",
            category="Contacts",
            example="add-phone Anna 0507654321",
        ),
        "show-phone": Command(
            handler=partial(show_phone, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="show-phone <ім'я>",
            description="Показати інформацію та телефони контакту",
            category="Contacts",
            example="show-phone Anna",
        ),
        "change-phone": MutationCommand(
            handler=partial(change_phone, book),
            arg_completer=lambda args: complete_name_and_phone(book, args),
            usage="change-phone <ім'я> <старий_телефон> <новий_телефон>",
            description="Змінити існуючий номер телефону контакту",
            category="Contacts",
            example="change-phone Anna 0501234567 0509998877",
        ),
        "delete-phone": MutationCommand(
            handler=partial(delete_phone, book),
            arg_completer=lambda args: complete_name_and_phone(book, args),
            usage="delete-phone <ім'я> <телефон>",
            description="Видалити номер телефону у контакту",
            category="Contacts",
            example="delete-phone Anna 0501234567",
        ),
        "add-birthday": MutationCommand(
            handler=partial(add_birthday, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="add-birthday <ім'я> <дн - ДД.ММ.РРРР>",
            description="Додати день народження до контакту",
            category="Contacts",
            example="add-birthday Anna 15.03.1995",
        ),
        "show-birthday": Command(
            handler=partial(show_birthday, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="show-birthday <ім'я>",
            description="Показати день народження контакту",
            category="Contacts",
            example="show-birthday Anna",
        ),
        "change-birthday": MutationCommand(
            handler=partial(change_birthday, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="change-birthday <ім'я> <дн - ДД.ММ.РРРР>",
            description="Змінити день народження контакту",
            category="Contacts",
            example="change-birthday Anna 20.04.1996",
        ),
        "delete-birthday": MutationCommand(
            handler=partial(delete_birthday, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="delete-birthday <ім'я>",
            description="Видалити день народження у контакту",
            category="Contacts",
            example="delete-birthday Anna",
        ),
        "upcoming-birthdays": Command(
            handler=partial(upcoming_birthdays, book),
            usage="upcoming-birthdays [дні=7]",
            description=(
                "Показати контакти з днями народження у найближчі дні"
            ),
            category="Contacts",
            example="upcoming-birthdays 14",
        ),
        "add-email": MutationCommand(
            handler=partial(add_email, book),
            usage="add-email <ім'я> <email>",
            arg_completer=lambda args: complete_contact_name(book, args),
            description="Додати email до контакту",
            category="Contacts",
            example="add-email Anna anna@mail.com",
        ),
        "change-email": MutationCommand(
            handler=partial(change_email, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="change-email <ім'я> <новий_email>",
            description="Змінити email контакту",
            category="Contacts",
            example="change-email Anna new@mail.com",
        ),
        "delete-email": MutationCommand(
            handler=partial(delete_email, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="delete-email <ім'я>",
            description="Видалити email у контакту",
            category="Contacts",
            example="delete-email Anna",
        ),
        "add-address": MutationCommand(
            handler=partial(add_address, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="add-address <ім'я> <адреса...>",
            description="Додати адресу до контакту",
            category="Contacts",
            example="add-address Anna Київ, вул. Хрещатик 1",
        ),
        "change-address": MutationCommand(
            handler=partial(change_address, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="change-address <ім'я> <нова_адреса...>",
            description="Змінити адресу контакту",
            category="Contacts",
            example="change-address Anna Львів, пл. Ринок 5",
        ),
        "delete-address": MutationCommand(
            handler=partial(delete_address, book),
            arg_completer=lambda args: complete_contact_name(book, args),
            usage="delete-address <ім'я>",
            description="Видалити адресу у контакту",
            category="Contacts",
            example="delete-address Anna",
        ),
    }
