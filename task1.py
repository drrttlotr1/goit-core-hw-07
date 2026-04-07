from collections import UserDict
from datetime import datetime, date, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if self._validate(value):
            super().__init__(value)
        else:
            raise ValueError("Phone number must contain exactly 10 digits.")

    def _validate(self, value):
        if str(value).isdigit() and len(str(value)) == 10:
            return True
        else:
            return False

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        self.value = value

    @staticmethod
    def date_to_string(date_obj):
        return date_obj.strftime("%Y.%m.%d")

    @staticmethod
    def find_next_weekday(start_date, weekday=0):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)
    
    @staticmethod
    def adjust_for_weekend(birthday):
        if birthday.weekday() >= 5:
            return Birthday.find_next_weekday(birthday, 0)
        return birthday

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def find_phone(self, target_phone):
        for i in self.phones:
         if i.value == target_phone:
          return i 

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError(f"Phone number '{phone}' not found.")

    def edit_phone(self, old_phone, new_phone):
        if self.find_phone(old_phone):
            self.add_phone(new_phone)
            self.remove_phone(old_phone)
        else:
            raise ValueError(f"Phone number '{old_phone}' not found.")
    
    def add_birthday(self, birthdate):
        self.birthday = Birthday(birthdate)
       
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name) 
        
    def delete(self, name: str):
        del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            birthday_this_year = birthday_date.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            congratulation_date = Birthday.adjust_for_weekend(birthday_this_year)
            days_until_birthday = (congratulation_date - today).days

            if 0 <= days_until_birthday <= days:
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date": Birthday.date_to_string(congratulation_date)
                })

        return upcoming_birthdays
    
    def __str__(self):
        if not self.data:
            return ("Address book is empty.")
        result = []
        for key, record in self.data.items():
            birthday = record.birthday.value if record.birthday else "N/A"
            result.append(f"{key}: {record}. Birthdate: {birthday}")
        return '\n'.join(result)

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Enter the argument for the command"
        except KeyError:
            return "Input error: Key not found."
        except AttributeError as e:
            return str(e)
    return inner

@input_error
def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []  
    cmd, args = parts[0], parts[1:]  
    return cmd.strip().lower(), args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
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
def add_birthday(args, book: AddressBook):
    name, birthdate = args
    record = book.find(name)
    record.add_birthday(birthdate)
    return f"Birthday for '{name}' added: {birthdate}."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record.birthday is None:
        return f"Contact '{name}' has no birthday set."
    else:
        return f"Birthday for '{name}': {record.birthday.value}."
    
@input_error
def birthdays(book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    result = []
    for item in upcoming:
        result.append(f"{item['name']}: {item['congratulation_date']}")
    return "\n".join(result)

@input_error
def get_contact(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        raise AttributeError(f'Contact with name {name} does not exists')
    if record:
        return f"'{name}' numbers: {', '.join(str(phone.value) for phone in record.phones)}"

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if not record:
        raise AttributeError(f"Contact '{name}' not found.")
    message = "Contact updated."
    record.edit_phone(old_phone, new_phone)
    return message

def main():
    book = AddressBook()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(get_contact(args, book))

        elif command == "all":
            print(AddressBook.__str__(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()