from datetime import datetime, date, timedelta
from collections import UserDict
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)
        if not value:
            raise ValueError("Name cannot be empty")


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if not self.validate_phone(value):
            raise ValueError("Invalid phone number format")

    def validate_phone(self, phone):
        return len(phone) == 10 and phone.isdigit()


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        new_phone = Phone(phone)
        self.phones.append(new_phone)
        return new_phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(i) for i in self.phones)}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.upcoming_birthdays = []

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def string_to_date(self, date_string):
        return datetime.strptime(date_string, "%Y.%m.%d").date()

    def date_to_string(self, date):
        return date.strftime("%Y.%m.%d")

    def prepare_user_list(self, user_data):
        prepared_list = []
        for user in user_data:
            prepared_list.append({"name": user["name"], "birthday": self.string_to_date(user["birthday"])})
        return prepared_list

    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for user in self.data.values():
            birthday_this_year = user.birthday.value.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            birthday_this_year = self.adjust_for_weekend(birthday_this_year)
            if 0 <= (birthday_this_year - today).days <= days:
                congratulation_date_str = self.date_to_string(birthday_this_year)
                upcoming_birthdays.append({"name": user.name.value, "congratulation_date": congratulation_date_str})
        if not upcoming_birthdays:
            return "No upcoming birthdays next week."

        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter the argument for the command"
        except IndexError:
            return "Invalid index in sequence"
        except ValueError:
            return "ValueError"

    return inner


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    return cmd, args


@input_error
def add_contact(args, book: AddressBook):
    name = args[0]
    phone = args[1]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name = args[0]
    phone = args[1]
    if name in book.data:
        book.data[name].phones = [Phone(phone)]
        return "Contact updated."
    else:
        return "Contact not found."


@input_error
def get_phone(args, book: AddressBook):
    name = args[0]
    if name in book.data:
        return f"The phone number for {name} is {book.data[name].phones[0]}."
    else:
        return "Contact not found."


@input_error
def list_all_contacts(book: AddressBook):
    if not book:
        return "No contacts found."
    else:
        return "\n".join([str(record) for record in book.values()])


@input_error
def add_birthday(args, book: AddressBook):
    name = args[0]
    birthday = args[1]
    record = book.find(name)
    message = "Birthday updated."
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return message


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"The birthday of {name} is {record.birthday}."
    elif record and not record.birthday:
        return f"No birthday set for {name}."
    else:
        return f"Contact {name} not found."


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)  # Зберегти дані перед виходом
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(get_phone(args, book))

        elif command == "all":
            print(list_all_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(book.get_upcoming_birthdays())
        else:
            print("Invalid command.")

    save_data(book)


if __name__ == "__main__":
    main()
