from collections import UserDict
from datetime import *
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
		pass


class Phone(Field):
	def __init__(self, value):
            super().__init__(value)
            if 10 != len(value) or not isinstance(int(value), int):
                raise ValueError("Phone has incorrect format")
            

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
      

class Record:
    try:
        with open("recordslist.pkl", "rb") as file:
            list_of_objects = pickle.load(file)
    except FileNotFoundError:
        list_of_objects = list()

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        Record.list_of_objects.append(self.__dict__)
        with open("recordslist.pkl", "wb") as file:
            pickle.dump(Record.list_of_objects, file)

    def add_phone(self, phone):
            phone_object = Phone(phone)
            self.phones.append(phone_object.value)

    def remove_phone(self, phone):
         self.phones.remove(phone)
    
    def edit_phone(self, old_number, new_number):
          if old_number not in self.phones or len(new_number) != 10 or not isinstance(int(old_number), int) or not isinstance(int(new_number), int):
            raise ValueError("One of phones or both of them have incorrect format")
          else:
            self.phones[self.phones.index(old_number)] = new_number

    def find_phone(self, phone):
        if phone in self.phones:
            return Phone(phone)
        else:
             return None
        
    def add_birthday(self, birthday):
         self.birthday = Birthday(birthday)
         with open("recordslist.pkl", "wb") as file:
            pickle.dump(Record.list_of_objects, file)

    def __str__(self):
        if self.birthday is not None:
            return f"Contact name: {self.name.value}, phones: {'; '.join(p for p in self.phones)}, birthday: {datetime.strftime(self.birthday.value, "%d.%m.%Y")}"
        else:
             return f"Contact name: {self.name.value}, phones: {'; '.join(p for p in self.phones)}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def add_record(self, contact): 
        self.data.update({contact.name.value : contact.phones})     

    def find(self, name):
        if name in self.data:
            contact = Record(name)
            for el in self.data.get(name):
                 contact.add_phone(el)
            for i in Record.list_of_objects:
                 if i.get("name") == name and i.get('birthday') is not None:
                    contact.add_birthday(datetime.strftime(i.get("birthday"), "%d.%m.%Y"))  
                 else:
                    continue
            self.data.update({contact.name.value : contact.phones}) 
            return contact
        else:
            return None
        
    def delete(self, name):
          self.data.pop(name)

    def get_upcoming_birthdays(self):
        list_of_users = list()
        today = date.today()
        now = datetime.now()
        for user in Record.list_of_objects:
            try:
                birthday_this_year = user["birthday"].value.replace(year=today.year)
                if ((now + timedelta(days=6)) - birthday_this_year) < timedelta(days=0) or ((now + timedelta(days=6)) - birthday_this_year) > timedelta(days=7):
                     continue
                if birthday_this_year.weekday() == 5:
                    birthday_this_year += timedelta(days=2)
                elif birthday_this_year.weekday() == 6:
                     birthday_this_year += timedelta(days=1)
                list_of_users.append({'name': user['name'].value, 'birthday': datetime.strftime(birthday_this_year, "%d.%m.%Y")})
            except AttributeError:
                 continue
        return list_of_users

    def __str__(self):
        return f"Book of contacts: {self.data}"
    

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
    return wrapper

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

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
def all (book):
    contacts = []
    for i in book.items():
        contacts.append(''.join(str(i)))
    return '\n'.join(contacts)

@input_error
def change_nummer(book, name, old_nummer, new_nummer):
    if len(old_nummer) != 10 or len(new_nummer) != 10 or not isinstance(int(old_nummer), int) or not isinstance(int(new_nummer), int):
        raise ValueError("One of phones or both of them have incorrect format")
    else:
        for el in Record.list_of_objects:
            if el['name'].value == name and old_nummer in el["phones"]:
                el["phones"][el["phones"].index(old_nummer)] = new_nummer
                with open("recordslist.pkl", "wb") as file:
                    pickle.dump(Record.list_of_objects, file)
        for el in book:
            if el == name:
                for i in book[name]:
                    if i == old_nummer:
                        book[name][book[name].index(i)] = new_nummer
                return 'Contact changed'

@input_error
def phone(book, user):
    for el in book:
        if el == user:
            return book.get(el)

@input_error  
def add_birthday_to_user(args, book):
    name, birthday, *_ = args
    user = book.find(name)
    for el in Record.list_of_objects:
        if el["name"].value == name and el["birthday"] is not None:
            return "This contact already has birthday date"
        else:
            continue
    else:
        user.add_birthday(birthday)
        return "Birthday added."

@input_error
def show_birthday(args):
    name, *_ = args
    for el in Record.list_of_objects:
        if el["name"].value == name and el["birthday"] is not None:
            return datetime.strftime(el["birthday"].value, "%d.%m.%Y")
        else:
            continue
    else:
        return None

@input_error
def birthdays(book):
    return(book.get_upcoming_birthdays())

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
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "all":
            print(all(book))
        elif command == "change":
            print(change_nummer(book, *args))
        elif command == 'phone':
            print(phone(book, args[0]))
        elif command == "add-birthday":
            print(add_birthday_to_user(args, book))
        elif command == "show-birthday":
            print(show_birthday(args))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()