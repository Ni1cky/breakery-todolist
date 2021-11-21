import json
import os
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import OneLineIconListItem, OneLineAvatarIconListItem, MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
import tasks_manager
from constants import *
from kivymd.app import MDApp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, NoTransition

def get_screen_manager():
    return MDApp.get_running_app().get_main_container().get_screen_manager()


def get_tasks_manager():
    return MDApp.get_running_app().get_tasks_manager()


def get_current_screen():
    return get_screen_manager().current_screen


class TasksScreen(MDScreen):
    tasks: GridLayout = ObjectProperty()

    def get_tasktext_for_searching(self):
        return MDApp.get_running_app().get_main_container().toolbar.search_text_field.text

    def add_new_task(self):
        tasks_man: tasks_manager.TasksManager = get_tasks_manager()
        tasks_man.create_new_task()

    def add_task(self, task):
        self.tasks.add_widget(task)

    def get_tasks(self):
        return get_tasks_manager().get_tasks_for_screen(self.name)

    def import_tasks(self, tasks):
        for task in tasks:
            self.add_task(task)

    def search_task(self):
        self.delete_all_tasks()
        search = self.get_tasktext_for_searching()
        if search:
            for task in self.get_tasks():
                if search in task.get_text():
                    self.add_task(task)
        else:
            self.reload()

    def delete_all_tasks(self):
        self.tasks.clear_widgets()

    def sort_tasks_alphabet(self):
        # SORT ALFABET
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

    def sort_tasks_alphabet_reversed(self):
        # SORT ALFABET
        new_tasks_text = sorted([task.get_text() for task in self.get_tasks()])
        new_tasks = []
        for label in new_tasks_text:
            for task in self.get_tasks():
                if task.get_text() == label:
                    new_tasks.append(task)

        self.delete_all_tasks()
        self.import_tasks(new_tasks)

    def sort_task_important_up(self):
        tasks_important = []
        tasks_NOT_important = []
        for task in self.get_tasks():
            if task.is_important:
                tasks_important.append(task)
            elif not task.is_important:
                tasks_NOT_important.append(task)
        new_task = tasks_important + tasks_NOT_important
        self.delete_all_tasks()
        self.import_tasks(new_task[::-1])

    def sort_task_important_down(self):
        tasks_important = []
        tasks_NOT_important = []
        for task in self.get_tasks():
            if task.is_important:
                tasks_important.append(task)
            elif not task.is_important:
                tasks_NOT_important.append(task)
        new_task = tasks_NOT_important + tasks_important
        self.delete_all_tasks()
        self.import_tasks(new_task[::-1])


class Task(MDBoxLayout):
    task_checkbox: MDCheckbox = ObjectProperty()
    task_input_field: MDTextField = ObjectProperty()
    make_imp_btn: MDIconButton = ObjectProperty()
    '''
    Класс задачи
    '''

    def __init__(self, task_id=-1, task_text="", **kwargs):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.task_input_field.text = task_text

        self.belongs_to = {"tasks", }

        self.is_done = False
        self.is_important = False

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


class RightContentCls(OneLineAvatarIconListItem):
    left_icon = StringProperty()
    text = StringProperty()


class ToolBar(MDBoxLayout):
    search_text_field: MDTextField = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        theme_items = [
            {
                "text": "светлая",
                "viewclass": "OneLineListItem",
                # "on_release": self.do_sort_tasks_alphabet
            },
            {
                "text": "темная",
                "viewclass": "OneLineListItem",
                # "on_release": self.sort_tasks_alphabet_reversed
            },
            {
                "text": "бурая",
                "viewclass": "OneLineListItem",
                # "on_release": self.sort_task_important_up
            }
        ]

        menu_items = [
            {
                "text": "Сортировка по алфавиту",
                "left_icon": "sort-alphabetical-ascending",
                "viewclass": "RightContentCls",
                "on_release": self.do_sort_tasks_alphabet
            },
            {
                "text": "Обратная сортировка по алфавиту",
                "left_icon": "sort-alphabetical-descending",
                "viewclass": "RightContentCls",
                "on_release": self.sort_tasks_alphabet_reversed
            },
            {
                "text": "Сортировка по важности",
                "left_icon": "sort-alphabetical-descending",
                "viewclass": "RightContentCls",
                "on_release": self.sort_task_important_up
            },
            {
                "text": "Обратная сортировка по важности",
                "left_icon": "sort-alphabetical-descending",
                "viewclass": "RightContentCls",
                "on_release": self.sort_task_important_down
            }
        ]
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=7,
        )
        self.themes = MDDropdownMenu(
            items=theme_items,
            width_mult=3,
        )

    def open_theme_menu(self, instance):
        self.themes.caller = instance
        self.themes.open()

    def open_menu(self, instance):
        MDApp.get_running_app().get_main_container().open_menu()

    def open_sort_menu(self, instance):
        self.menu.caller = instance
        self.menu.open()

    def sort_task_important_up(self):
        get_screen_manager().current_screen.sort_task_important_up()

    def do_sort_tasks_alphabet(self):
        get_screen_manager().current_screen.sort_tasks_alphabet()

    def sort_tasks_alphabet_reversed(self):
        get_screen_manager().current_screen.sort_tasks_alphabet_reversed()

    def sort_task_important_down(self):
        get_screen_manager().current_screen.sort_task_important_down()

    def search_task(self):
        get_screen_manager().current_screen.search_task()


class MenuButton(OneLineIconListItem):
    '''
    Класс кнопки, меняющей экран
    '''

    def __init__(self, screen_name=None, **kwargs):
        super().__init__(**kwargs)
        if screen_name:
            self.screen_name = screen_name

    def change_screen(self):
        if get_screen_manager().current == self.screen_name:
            return
        get_current_screen().delete_all_tasks()
        get_screen_manager().current = self.screen_name


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
    screens_list: MDList = ObjectProperty()
    '''
    Cписок задач
    '''

    new_list_field: MDTextField = ObjectProperty()

    def add_new_list(self):
        list_name = self.new_list_field.text
        screen_name = list_name
        screen_manager: ScreenManager = get_screen_manager()
        while screen_name in screen_manager.screen_names:
            if screen_name != "" and screen_name[-1].isdigit():
                screen_name = screen_name[:-1] + str(int(screen_name[-1]) + 1)
            else:
                screen_name += '1'
        screen_manager.add_widget(TasksScreen(name=screen_name))

        newList = MenuButton(screen_name=screen_name)
        newList.text = list_name
        newList.icn = "home"
        self.screens_list.add_widget(newList)


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
        self.screen_manager.current = "tasks"

    def open_menu(self, instance=None):
        self.main_menu.nav_bar.set_state("open")

    def open_settings(self, instance=None):
        self.screen_manager.current = "settings_menu"

    # def open_screen_properly(self):
    #     if isinstance(self.screen_manager.current_screen, TasksScreen):
    #         for item in self.toolbar.children[0].ids.right_actions.children[1:]:
    #             item.text_color = "#FFFFFF"
    #         try:
    #             self.screen_manager.current_screen.reload()
    #         except AttributeError:
    #             pass
    #     else:
    #         for item in self.toolbar.children[0].ids.right_actions.children[1:]:
    #             item.text_color = "#646464"

    def load_tasks(self):
        if (
                not os.path.exists(self.SAVE_FOLDER) or
                os.listdir(self.SAVE_FOLDER) == [".gitignore"] or
                f"{self.SAVE_NAME}.json" not in os.listdir(self.SAVE_FOLDER)
        ):
            return

        with open(self.SAVE_PATH, "r") as f:
            save = json.load(f)

        tasks_man: tasks_manager.TasksManager = get_tasks_manager()

        save: dict = save[self.SAVE_NAME]
        for task_id in save.keys():
            task_params = save[task_id]
            task = Task(task_id=int(task_id), task_text=task_params["text"])
            if task_params["is_important"]:
                task.make_important()
            if task_params["is_done"]:
                task.mark_done()
            task.update_parents(task_params["belongs_to"])
            tasks_man.add_new_task(task)
        tasks_man.reload_current_screen()

    def save_tasks(self):
        if not os.path.exists(self.SAVE_FOLDER):
            os.mkdir(self.SAVE_FOLDER)

        data = {self.SAVE_NAME: {}}
        cur_save = data[self.SAVE_NAME]
        for task in get_tasks_manager().tasks:
            cur_task = cur_save[task.task_id] = {}
            cur_task["text"] = task.get_text()
            cur_task["is_important"] = task.is_important
            cur_task["is_done"] = task.is_done
            cur_task["belongs_to"] = list(task.belongs_to)

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

    def on_start(self):
        self.main_container.load_tasks()

    def on_stop(self):
        self.main_container.save_tasks()

    def get_main_container(self):
        return self.main_container

    def get_tasks_manager(self):
        return self.tasks_manager


def main():
    app = TodoApp()
    app.run()


if __name__ == '__main__':
    main()
