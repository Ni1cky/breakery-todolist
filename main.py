import json
import os

from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDIconButton, MDRectangleFlatIconButton
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from constants import *
from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.stacklayout import StackLayout


class TasksScreen(Screen):
    # Макс, Коля
    tasks: GridLayout = ObjectProperty()

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


class Task(BoxLayout):
    task_checkbox: MDCheckbox = ObjectProperty()
    task_input_field: MDTextField = ObjectProperty()
    make_imp_btn: MDIconButton = ObjectProperty()
    # Вадим
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

    def get_text(self):
        return self.task_input_field.text


class MenuButton(MDRectangleFlatIconButton):
    # Макс
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

        self.screen_manager.transition = NoTransition()
        self.load_tasks_screens()

    def load_tasks_screens(self):
        self.screen_manager.add_widget(TasksScreen(name="important"))
        self.screen_manager.add_widget(TasksScreen(name="tasks"))
        self.screen_manager.add_widget(TasksScreen(name="my_day"))
        self.screen_manager.current = "tasks"

    def load_tasks(self):
        # Денис

        if not os.path.exists(self.SAVE_FOLDER) or os.listdir(self.SAVE_FOLDER) == []:
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
