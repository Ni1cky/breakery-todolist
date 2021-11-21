import json
import os
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
import tasks_manager
from constants import *
from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, NoTransition


def get_screen_manager():
    return MDApp.get_running_app().get_main_container().get_screen_manager()


def get_tasks_manager():
    return MDApp.get_running_app().get_tasks_manager()


class TasksScreen(MDScreen):
    tasks_layout: RecycleGridLayout = ObjectProperty()
    tasks_view: RecycleView = ObjectProperty()

    def get_tasktext_for_searching(self):
        return MDApp.get_running_app().get_main_container().toolbar.search_text_field.text

    def add_new_task(self):
        tasks_man: tasks_manager.TasksManager = get_tasks_manager()
        tasks_man.create_new_task()
        # self.add_task(tasks_man.get_task(len(tasks_man.tasks) - 1))

    def add_task(self, task):
        self.tasks_layout.add_widget(task)

    def delete_task(self, task_id):
        for task in self.tasks_layout.children:
            if task.task_id == task_id:
                self.tasks_layout.remove_widget(task)
                return

    def get_tasks(self):
        return [task for task in get_tasks_manager().get_tasks_for_screen(self.name)]

    def import_tasks(self, tasks):
        self.tasks_view.data = tasks
        # for task in [Task(**task_params) for task_params in tasks]:
        #     self.add_task(task)

    def search_task(self):
        pass
        self.delete_all_tasks()
        search = self.get_tasktext_for_searching()
        if search:
            for task in self.get_tasks():
                if search in task.get_text():
                    self.add_task(task)
        else:
            self.reload()

    def delete_all_tasks(self):
        self.tasks_view.data = []
        self.tasks_layout.clear_widgets()

    def sort_tasks(self):
        # SORT ALFABET
        pass
        new_tasks_text = sorted([task.get_text() for task in self.get_tasks()])
        new_tasks = []
        for label in new_tasks_text:
            for task in self.get_tasks():
                if task.get_text() == label:
                    new_tasks.append(task)

        self.delete_all_tasks()
        self.import_tasks(new_tasks[::-1])

    def reload(self):
        if get_screen_manager().current == self.name:
            self.delete_all_tasks()
            self.import_tasks(self.get_tasks())
            print(self.tasks_view.data)
            # self.tasks_view.refresh_from_data()
            print(self.tasks_layout.children)


class Task(MDBoxLayout, RecycleDataViewBehavior):
    task_checkbox: MDCheckbox = ObjectProperty()
    task_input_field: MDTextField = ObjectProperty()
    make_imp_btn: MDIconButton = ObjectProperty()
    '''
    Класс задачи
    '''

    def __init__(self, task_id=-1, task_text="", belongs_to=None, is_done=False, is_important=False, **kwargs):
        super().__init__(**kwargs)

        if belongs_to is None:
            belongs_to = {"tasks", }

        self.task_id = task_id
        self.task_input_field.text = task_text

        self.belongs_to = belongs_to

        self.is_done = False
        self.is_important = False
        if is_done:
            self.mark_done()
        if is_important:
            self.make_important()

    def get_params(self):
        return {"is_done": self.is_done, "is_important": self.is_important, "belongs_to": self.belongs_to, "task_text":self.task_input_field.text, "task_id": self.task_id}

    def update_parents(self, belongs_to):
        for parent in belongs_to:
            self.belongs_to.add(parent)

    def delete(self):
        get_tasks_manager().delete_task(self.task_id)

    def make_important(self):
        self.is_important = not self.is_important

    def mark_done(self):
        self.is_done = not self.is_done
        self.task_checkbox.active = self.is_done

    def get_text(self):
        return self.task_input_field.text

    def set_text(self, text):
        self.task_input_field.text = text

    def change_text(self):
        tasks_man = get_tasks_manager()
        tasks_man.tasks[self.task_id].set_text(self.get_text())


class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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


class ToolBar(MDBoxLayout):
    search_text_field: MDTextField = ObjectProperty()

    def open_menu(self):
        pass

    def open_settings(self):
        pass

    def sort_tasks(self):
        pass

    def search_task(self):
        pass


class MenuButton(OneLineIconListItem):
    '''
    Класс кнопки, меняющей экран
    '''

    def __init__(self, screen_name=None, **kwargs):
        super().__init__(**kwargs)
        if screen_name:
            self.screen_name = screen_name

    def change_screen(self):
        manager: ScreenManager = get_screen_manager()
        manager.current_screen.delete_all_tasks()
        manager.current = self.screen_name


class LowerMenuLayout(MDBoxLayout):
    '''
    Нижняя часть меню
    '''
    pass


class UpperMenuLayout(MDBoxLayout):
    '''
    Тут верхняя часть меню
    '''
    pass


class ScrollViewTasksList(ScrollView):
    '''
    Cписок задач
    '''

    def add_new_list(self):
        pass


class MainMenuLayout(MDNavigationDrawer):
    '''
    Всё меню
    '''
    upper: UpperMenuLayout = ObjectProperty()
    lower: LowerMenuLayout = ObjectProperty()
    nav_bar: MDNavigationDrawer = ObjectProperty()


class MainContainer(MDBoxLayout):
    screen_manager: ScreenManager = ObjectProperty()
    main_menu: MainMenuLayout = ObjectProperty()
    toolbar: ToolBar = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.SAVE_NAME = SAVE_NAME
        self.SAVE_FOLDER = SAVE_FOLDER
        self.SAVE_PATH = SAVE_PATH

        self.screen_manager.transition = NoTransition()
        self.load_tasks_screens()

    def load_tasks_screens(self):
        self.screen_manager.add_widget(TasksScreen(name="important"))
        self.screen_manager.add_widget(TasksScreen(name="tasks"))
        self.screen_manager.add_widget(TasksScreen(name="my_day"))
        self.screen_manager.add_widget(SettingsScreen(name="settings_menu"))
        self.screen_manager.current = "tasks"

    def open_menu(self, instance=None):
        self.main_menu.nav_bar.set_state("open")

    def sort_tasks(self, instance=None):
        if not isinstance(self.screen_manager.current_screen, TasksScreen):
            return
        cur_screen: TasksScreen = self.screen_manager.current_screen
        cur_screen.sort_tasks()

    def search_task(self, instance=None):
        if not isinstance(self.screen_manager.current_screen, TasksScreen):
            return
        cur_screen: TasksScreen = self.screen_manager.current_screen
        cur_screen.search_task()

    def open_settings(self, instance=None):
        self.screen_manager.current = "settings_menu"

    def open_screen_properly(self):
        if isinstance(self.screen_manager.current_screen, TasksScreen):
            for item in self.toolbar.children[0].ids.right_actions.children[1:]:
                item.text_color = "#FFFFFF"
            try:
                self.screen_manager.current_screen.reload()
            except AttributeError:
                pass
        else:
            for item in self.toolbar.children[0].ids.right_actions.children[1:]:
                item.text_color = "#646464"

    def load_tasks(self):
        if (
                not os.path.exists(self.SAVE_FOLDER) or
                os.listdir(self.SAVE_FOLDER) == [".gitignore"] or
                f"{self.SAVE_NAME}.json" not in os.listdir(self.SAVE_FOLDER)
        ):
            return

        with open(self.SAVE_PATH, "r") as f:
            save = json.load(f)

        save: dict = save[self.SAVE_NAME]

        for scr in save.keys():

            tasks: dict = save[scr]

            for id, task in tasks.items():
                new_task = Task(task_id=id, task_text=task["text"])
                if task["is_done"]:
                    new_task.mark_done()
                if task["is_important"]:
                    new_task.make_important()
                cur_scr: TasksScreen = self.screen_manager.get_screen(scr)
                cur_scr.add_task(new_task)

    def save_tasks(self):
        if not os.path.exists(self.SAVE_FOLDER):
            os.mkdir(self.SAVE_FOLDER)

        screens = self.screen_manager.screens

        data = {self.SAVE_NAME: {}}
        cur_save = data[self.SAVE_NAME]
        for scr in screens:
            if not isinstance(scr, TasksScreen):
                continue
            scr: TasksScreen
            cur_scr = cur_save[scr.name] = {}

            for task in scr.get_tasks():
                task: Task
                cur_task = cur_scr[task.task_id] = {}
                cur_task["text"] = task.get_text()
                cur_task["is_done"] = task.is_done
                cur_task["is_important"] = task.is_important

        with open(self.SAVE_PATH, 'w') as f:
            json.dump(data, f)

    def get_screen_manager(self):
        return self.screen_manager


class TodoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks_manager = tasks_manager.TasksManager()
        self.main_container = None

    def build(self):
        self.main_container = MainContainer()
        return self.main_container

    # def on_start(self):
    #     self.main_container.load_tasks()

    # def on_stop(self):
    #     self.main_container.save_tasks()

    def get_main_container(self):
        return self.main_container

    def get_tasks_manager(self):
        return self.tasks_manager


def main():
    app = TodoApp()
    app.run()


if __name__ == '__main__':
    main()
