import datetime
from collections import UserDict

# Декоратор для обробки помилок введення.
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError) as e:
            return str(e)
    return inner

# Базовий клас для полів запису.
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Клас для імені контакту.
class Name(Field):
    pass

# Клас для номера телефону з валідацією.
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Номер телефону повинен містити 10 цифр.")
        super().__init__(value)

# Клас для дати народження з валідацією.
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Невірний формат дати. Використовуйте DD.MM.YYYY")

# Клас для запису контакту.
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None 

    def add_phone(self, phone_number):
        phone_obj = Phone(phone_number)
        self.phones.append(phone_obj)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
            return True
        return False

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if not phone_to_edit:
            raise ValueError("Номер телефону не знайдено.")
        
        new_phone_obj = Phone(new_phone)
        self.phones.remove(phone_to_edit)
        self.phones.append(new_phone_obj)
        return True

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

# Клас адресної книги.
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.date.today()
        for record in self.data.values():
            if record.birthday and record.birthday.value:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                
                delta_days = (birthday_this_year - today).days

                if 0 <= delta_days < 7:
                    if birthday_this_year.weekday() >= 5:
                        if birthday_this_year.weekday() == 5:
                            birthday_this_year += datetime.timedelta(days=2)
                        elif birthday_this_year.weekday() == 6:
                            birthday_this_year += datetime.timedelta(days=1)
                    
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": birthday_this_year.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays

    def __str__(self):
        if not self.data:
            return "Адресна книга порожня."
        return '\n'.join(str(record) for record in self.data.values())

# --- Функції-обробники команд ---

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.lower()
    return cmd, *args

@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise IndexError("Неповна команда. Введіть ім'я та хоча б один телефон.")
    name, *phones = args
    record = book.find(name)
    message = "Контакт оновлено."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт додано."
    
    for phone in phones:
        record.add_phone(phone)
    
    return message

@input_error
def change_contact(args, book):
    if len(args) != 3:
        raise IndexError("Неповна команда. Введіть ім'я, старий телефон та новий телефон.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Контакт оновлено."
    raise KeyError("Контакт не знайдено.")

@input_error
def show_phone(args, book):
    if len(args) != 1:
        raise IndexError("Неповна команда. Введіть ім'я.")
    name = args[0]
    record = book.find(name)
    if record:
        return str(record)
    raise KeyError("Контакт не знайдено.")

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise IndexError("Неповна команда. Введіть ім'я та дату народження (DD.MM.YYYY).")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Дату народження додано."
    raise KeyError("Контакт не знайдено.")

@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise IndexError("Неповна команда. Введіть ім'я.")
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Дата народження {record.name.value}: {record.birthday.value.strftime('%d.%m.%Y')}"
        else:
            return "У контакту не вказано дату народження."
    raise KeyError("Контакт не знайдено.")

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "Немає найближчих днів народження."
    
    output = "Дні народження на найближчий тиждень:\n"
    for item in upcoming:
        output += f"{item['name']}: {item['birthday']}\n"
    return output

# --- Головна функція ---
def main():
    book = AddressBook()
    print("Вітаю! Я ваш бот-помічник. Чим можу допомогти?")
    print("Список команд: add, change, phone, all, add-birthday, show-birthday, birthdays, hello, exit, close")
    while True:
        try:
            user_input = input("Введіть команду: ")
            command, *args = parse_input(user_input)
            
            if command in ["close", "exit"]:
                print("До побачення!")
                break
            elif command == "hello":
                print("Як я можу вам допомогти?")
            elif command == "add":
                print(add_contact(args, book))
            elif command == "change":
                print(change_contact(args, book))
            elif command == "phone":
                print(show_phone(args, book))
            elif command == "all":
                print(book)
            elif command == "add-birthday":
                print(add_birthday(args, book))
            elif command == "show-birthday":
                print(show_birthday(args, book))
            elif command == "birthdays":
                print(birthdays(args, book))
            else:
                print("Невірна команда.")
        except IndexError:
            # Обробка порожнього вводу.
            print("Будь ласка, введіть команду.")
        except Exception as e:
            # Обробка будь-якої іншої неочікуваної помилки.
            print(f"Сталася невідома помилка: {e}")

if __name__ == "__main__":
    main()