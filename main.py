import json
import os
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDIconButton, MDRectangleFlatIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from constants import *
from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.stacklayout import StackLayout


class TasksScreen(Screen):
    # Макс, Коля
    tasks: GridLayout = ObjectProperty()

    def delete_task(self, task):
        self.tasks.remove_widget(task)

    def add_task(self, task=None):
        if task:
            self.tasks.add_widget(task)
            return
        self.tasks.add_widget(Task())

    def get_tasks(self):
        return [task for task in self.tasks.children]

    def import_tasks(self, tasks):
        for task in tasks:
            self.add_task(task)

    def search_task(self, instance):
        pass

    def delete_all_tasks(self):
        #Вадим
        for i in self.get_tasks():
            self.delete_task(i)

    def sort_task(self, instance):
        #Вадим
        # SORT ALFABET
        new_tasks_text = sorted([task.get_task_text() for task in self.get_tasks()])
        new_tasks = []
        for label in new_tasks_text:
            for task in self.get_tasks():
                if task.get_task_text() == label:
                    new_tasks.append(task)

        self.delete_all_tasks()
        self.import_tasks(new_tasks[::-1])

    def dots_task(self, instance):
        pass

    def open_menu(self, instance):
        pass

    def open_settings(self, instance):
        app: TodoApp = MDApp.get_running_app()
        main_container: MainContainer = app.get_main_container()
        manager: ScreenManager = main_container.get_screen_manager()
        manager.current = "settings_menu"


class Task(BoxLayout):
    task_checkbox: MDCheckbox = ObjectProperty()
    task_input_field: MDTextField = ObjectProperty()
    make_imp_btn: MDIconButton = ObjectProperty()
    '''
    Класс задачи
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'task_text' in kwargs:
            self.task_text = kwargs['task_text']
        if 'task_name' in kwargs:
            self.task_name = kwargs['task_name']
        self.is_done = False
        self.is_important = False

    def delete_task(self):
        app = MDApp.get_running_app()
        main_container = app.get_main_container()
        screen_manager = main_container.get_screen_manager()
        screen_manager.get_screen(screen_manager.current).delete_task(self)

    def make_important(self):
        self.is_important = not self.is_important

    def mark_done(self):
        self.is_done = not self.is_done

    def get_task_text(self):
        return self.task_input_field.text


class SettingsMenu(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        menu_items = [
            {
                "text": "темная",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="темная": self.menu_callback(x)
            },
            {
                "text": "светлая",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="светлая": self.menu_callback(x)
            },
            {
                "text": "бурая",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="бурая": self.menu_callback(x)
            }
        ]
        TodoApp.menu = MDDropdownMenu(
            caller=self.ids.button,
            items=menu_items,
            width_mult=3,
        )

    def menu_callback(self, text_item):
        # функция, которая вызывается при наатии
        # print(text_item)
        pass


class MenuButton(MDRectangleFlatIconButton):
    '''
    Класс кнопки, меняющей экран
    '''

    def __init__(self, screen_name=None, **kwargs):
        super().__init__(**kwargs)
        if screen_name:
            self.set_screen_name(screen_name)

    # Эту функцию прописываем в kv-файле в on_press
    def change_screen(self):
        app: TodoApp = MDApp.get_running_app()
        main_container: MainContainer = app.get_main_container()
        manager: ScreenManager = main_container.get_screen_manager()
        manager.current = self.screen_name

    def set_screen_name(self, screen_name):
        self.screen_name = screen_name


class LowerMenuLayout(StackLayout):
    # Макс
    '''
    Нижняя часть меню
    '''
    pass


class UpperMenuLayout(StackLayout):
    ''' Тут верхняя часть меню '''
    pass


class MainMenuLayout(BoxLayout):
    # Макс
    '''
    Всё меню
    '''
    pass


class MainContainer(BoxLayout):
    screen_manager: ScreenManager = ObjectProperty()
    important_button: MenuButton = ObjectProperty()
    home_button: MenuButton = ObjectProperty()
    my_day_button: MenuButton = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.SAVE_NAME = SAVE_NAME
        self.SAVE_FOLDER = SAVE_FOLDER
        self.SAVE_PATH = SAVE_PATH

        self.important_button.set_screen_name("important")
        self.tasks_button.set_screen_name("tasks")
        self.my_day_button.set_screen_name("my_day")
        # self.load_tasks()
        self.screen_manager.transition = NoTransition()
        self.load_tasks_screens()

    def load_tasks_screens(self):
        self.screen_manager.add_widget(TasksScreen(name="important"))
        self.screen_manager.add_widget(TasksScreen(name="tasks"))
        self.screen_manager.add_widget(TasksScreen(name="my_day"))
        self.screen_manager.add_widget(SettingsMenu(name="settings_menu"))
        self.screen_manager.current = "tasks"

    def load_tasks(self):
        # Денис
        with open(self.SAVE_PATH, "r") as f:
            save = json.load(f)
        cur_save: dict = save[self.SAVE_NAME]
        for i in cur_save.values():
            new_task = Task(task_name=i["name"])
            if i["is_done"]:
                new_task.mark_done()
            if i["is_important"]:
                new_task.make_important()
            self.tasks_screen.add_task(new_task)

    def save_tasks(self):
        # Денис
        if not os.path.exists(self.SAVE_FOLDER):
            os.mkdir(self.SAVE_FOLDER)

        tasks = self.tasks_screen.get_tasks()

        data = {self.SAVE_NAME: {}}
        cur_save = data[self.SAVE_NAME]
        for task in tasks:
            cur_task = cur_save[task.task_name] = {}
            cur_task["name"] = task.task_name
            cur_task["text"] = task.task_text
            cur_task["is_done"] = task.is_done
            cur_task["is_important"] = task.is_important

        with open(self.SAVE_PATH, 'w') as f:
            json.dump(data, f)

    def get_screen_manager(self):
        return self.screen_manager






class TodoApp(MDApp):
    def build(self):
        self.main_container = MainContainer()
        return self.main_container

    def get_main_container(self):
        return self.main_container


def main():
    app = TodoApp()
    app.run()


if __name__ == '__main__':
    main()
