import json
import os
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.popup import Popup
from kivymd.uix.button import MDIconButton, MDRectangleFlatIconButton
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDToolbar

from constants import *
from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition


class TasksScreen(Screen):
    # Макс, Коля
    tasks: GridLayout = ObjectProperty()
    search_text_field = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.saved_tasks = []

    def delete_task(self, task):
        self.tasks.remove_widget(task)

    def add_task(self, task=None):
        new_id = len(self.tasks.children)
        if task:
            task.id = new_id
            self.tasks.add_widget(task)
            return

        self.tasks.add_widget(Task(id=new_id))

    def get_tasks(self):
        return [task for task in self.tasks.children]

    def import_tasks(self, tasks):
        for task in tasks:
            self.add_task(task)

    def search_task(self, *args):
        #Вадим
        search = self.search_text_field.text
        if search != '':
            if not self.saved_tasks:
                self.saved_tasks = self.get_tasks()
            self.delete_all_tasks()

            for task in self.saved_tasks:
                if search in task.get_task_text():
                    self.add_task(task)
        else:
            self.delete_all_tasks()
            self.import_tasks(self.saved_tasks)
            self.saved_tasks = []

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

    def __init__(self, id=0, task_text="", **kwargs):
        super().__init__(**kwargs)
        self.id = id

        self.task_input_field.text = task_text

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
        self.task_checkbox.active = self.is_done

    def get_text(self):
        return self.task_input_field.text


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


class ToolBar(BoxLayout):
    search_text_field: MDTextField = ObjectProperty()


class MenuButton(OneLineIconListItem):
    '''
    Класс кнопки, меняющей экран
    '''

    def __init__(self, screen_name=None, **kwargs):
        super().__init__(**kwargs)
        if screen_name:
            self.screen_name = screen_name

    # Эту функцию прописываем в kv-файле в on_press
    def change_screen(self):
        app: TodoApp = MDApp.get_running_app()
        main_container: MainContainer = app.get_main_container()
        manager: ScreenManager = main_container.get_screen_manager()
        manager.current = self.screen_name


class LowerMenuLayout(MDBoxLayout):
    # Макс
    '''
    Нижняя часть меню
    '''
    pass


class UpperMenuLayout(MDBoxLayout):
    ''' Тут верхняя часть меню '''
    important_button: MenuButton = ObjectProperty()
    home_button: MenuButton = ObjectProperty()
    my_day_button: MenuButton = ObjectProperty()


class ScrollViewTasksList(ScrollView):
    '''список задач'''

    def add_new_list(self):
        pass


class MainMenuLayout(MDBoxLayout):
    '''
    Всё меню
    '''
    upper: UpperMenuLayout = ObjectProperty()
    lower: LowerMenuLayout = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # print(self.parent)
        # print(self.children)


class MainContainer(BoxLayout):
    screen_manager: ScreenManager = ObjectProperty()
    main_menu: MainMenuLayout = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.SAVE_NAME = SAVE_NAME
        self.SAVE_FOLDER = SAVE_FOLDER
        self.SAVE_PATH = SAVE_PATH

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

        if (
                not os.path.exists(self.SAVE_FOLDER) or
                os.listdir(self.SAVE_FOLDER) == [".gitignore"] or
                self.SAVE_PATH not in os.listdir(self.SAVE_FOLDER)
        ):
            return

        with open(self.SAVE_PATH, "r") as f:
            save = json.load(f)

        save: dict = save[self.SAVE_NAME]

        for scr in save.keys():

            tasks: dict = save[scr]

            for id, task in tasks.items():
                new_task = Task(id=id, task_text=task["text"])
                if task["is_done"]:
                    new_task.mark_done()
                if task["is_important"]:
                    new_task.make_important()
                cur_scr: TasksScreen = self.screen_manager.get_screen(scr)
                cur_scr.add_task(new_task)

    def save_tasks(self):
        # Денис
        if not os.path.exists(self.SAVE_FOLDER):
            os.mkdir(self.SAVE_FOLDER)

        screens = self.screen_manager.screens

        data = {self.SAVE_NAME: {}}
        cur_save = data[self.SAVE_NAME]
        for scr in screens:
            if not scr is TasksScreen:
                continue
            scr: TasksScreen
            cur_scr = cur_save[scr.name] = {}

            for task in scr.get_tasks():
                task: Task
                cur_task = cur_scr[task.id] = {}
                cur_task["text"] = task.get_text()
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

    def on_start(self):
        self.main_container.load_tasks()

    def on_stop(self):
        self.main_container.save_tasks()

    def get_main_container(self):
        return self.main_container


def main():
    app = TodoApp()
    app.run()


if __name__ == '__main__':
    main()
