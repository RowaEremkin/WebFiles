dicti = {
    "site_name":{
        "en": "Files",
        "ru": "Файлы"
    },
    "login":{
        "en": "Login",
        "ru": "Вход"
    },
    "log_in":{
        "en": "Log in",
        "ru": "Войти"
    },
    "dont_have_account":{
        "en": "Dont have an account?",
        "ru": "Нет аккаунта?"
    },
    "registration":{
        "en": "Registration",
        "ru": "Регистрация"
    },
    "back":{
        "en": "Back",
        "ru": "Назад"
    },
    "download":{
        "en": "Download",
        "ru": "Загрузить"
    },
    "username":{
        "en": "Username",
        "ru": "Имя пользователя"
    },
    "password":{
        "en": "Password",
        "ru": "Пароль"
    },
    "passwordRepeat":{
        "en": "Password repeat",
        "ru": "Повтор пароля"
    },
    "register":{
        "en": "Register",
        "ru": "Зарегистрироваться"
    },
    "email":{
        "en": "Email",
        "ru": "Эпочта"
    },
    "login_as":{
        "en": "Login as",
        "ru": "Вы вошли как"
    },
    "you_have_been_logged_out":{
        "en": "You have been logged out",
        "ru": "Вы вышли из аккаунта"
    },
    "logout":{
        "en": "Logout",
        "ru": "Выйти"
    },
    "create_file":{
        "en": "Create file",
        "ru": "Создать файл"
    },
    "create_folder":{
        "en": "Create folder",
        "ru": "Создать папку"
    },
    "upload":{
        "en": "Upload",
        "ru": "Выгрузить"
    },
    "folder_name_can_not_be_empty":{
        "en": "Folder name can not be empty",
        "ru": "Имя папки не может быть пустым"
    },
    "failed_to_create_folder":{
        "en": "Failed to create folder",
        "ru": "Ошибка при создании папки"
    },
    "enter_folder_name":{
        "en": "Enter folder name:",
        "ru": "Введите имя папки:"
    },
    "enter_file_name":{
        "en": "Enter file name:",
        "ru": "Введите имя файла:"
    },
    "enter_file_content":{
        "en": "Enter file content:",
        "ru": "Введите содержимое файла:"
    },
    "file_name_can_not_be_empty":{
        "en": "File name can not be empty",
        "ru": "Имя файла не может быть пустым."
    },
    "failed_to_create_file":{
        "en": "Failed to create file",
        "ru": "Ошибка при создании файла"
    },
    "are_you_sure_you_want_to_delete_this_file":{
        "en": "Are you sure you want to delete this file?",
        "ru": "Вы уверены, что хотите удалить этот файл?"
    },
    "failed_to_delete_file":{
        "en": "Failed to delete file",
        "ru": "Ошибка при удалении файла"
    },
    "are_you_sure_you_want_to_delete_this_folder":{
        "en": "Are you sure you want to delete this folder?",
        "ru": "Вы уверены, что хотите удалить эту папку?"
    },
    "failed_to_delete_folder":{
        "en": "Failed to delete folder",
        "ru": "Ошибка при удалении папки"
    },
    "enter_new_folder_name":{
        "en": "Enter new folder name:",
        "ru": "Введите новое имя папки"
    },
    "failed_to_rename_folder":{
        "en": "Failed to rename folder",
        "ru": "Ошибка при переименовании папки"
    },
    "enter_new_file_name":{
        "en": "Enter new file name:",
        "ru": "Введите новое имя файла:"
    },
    "failed_to_rename_file":{
        "en": "Failed to rename file",
        "ru": "Ошибка при переименовании файла"
    },
    "search":{
        "en": "Search",
        "ru": "Поиск"
    },
    "search_placeholder":{
        "en": "Find...",
        "ru": "Поиск..."
    },


}
def get_translations(language):
    trans = {}
    for (key,val) in dicti.items():
        if val.__contains__(language):
            trans[key] = val[language]
        else:
            trans[key] = val["en"]
    return trans