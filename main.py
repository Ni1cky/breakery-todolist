import json
import os
from kivy.graphics import Color, Line
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


def get_screen_manager() -> ScreenManager:
    return MDApp.get_running_app().get_main_container().get_screen_manager()


def get_tasks_manager():
    return MDApp.get_running_app().get_tasks_manager()


class TasksScreen(MDScreen):
    tasks: GridLayout = ObjectProperty()

    def get_tasktext_for_searching(self):
        return MDApp.get_running_app().get_main_container().toolbar.search_text_field.text

    def add_new_task(self):
        tasks_man = get_tasks_manager()
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
                if task.get_text() == label and task not in new_tasks:
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
                if task.get_text() == label and task not in new_tasks:
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


def get_current_screen() -> TasksScreen:
    return get_screen_manager().current_screen


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
        if isinstance(belongs_to, str):
            self.belongs_to.add(belongs_to)
        else:
            for parent in belongs_to:
                self.belongs_to.add(parent)

    def delete(self):
        get_tasks_manager().delete_task(self.task_id)

    def make_important(self):
        self.is_important = not self.is_important

    def mark_done(self):
        self.is_done = not self.is_done
        self.repaint()
        if self.is_done:
            get_tasks_manager().add_task_to_screen(self.task_id, "done_tasks")
        else:
            self.belongs_to.remove('done_tasks')
        get_screen_manager().current_screen.reload()
        self.task_checkbox.active = self.is_done

    def repaint(self):
        for child in self.canvas.children:
            if isinstance(child, Color):
                if child.rgba == [0.0, 0.31, 0.88, 0.7]:
                    child.rgba = [0.39, 0.39, 0.39, 1]
                    return
                if child.rgba == [0.39, 0.39, 0.39, 1]:
                    child.rgba = [0.0, 0.31, 0.88, 0.7]
                    return

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
        screen_manager = get_screen_manager()
        if screen_manager.current == self.screen_name:
            return
        screen_manager.current_screen.delete_all_tasks()
        screen_manager.current = self.screen_name
        get_tasks_manager().reload_current_screen()


class ScrollViewTasksList(ScrollView):
    '''
    Cписок задач
    '''
    screens_list: MDList = ObjectProperty()
    new_list_field: MDTextField = ObjectProperty()

    def add_new_list(self):
        list_name = self.new_list_field.text
        screen_name = list_name
        screen_manager = get_screen_manager()
        while screen_name in screen_manager.screen_names:
            if screen_name != "" and screen_name[-1].isdigit():
                screen_name = screen_name[:-1] + str(int(screen_name[-1]) + 1)
            else:
                screen_name += '1'
        screen_manager.add_widget(TasksScreen(name=screen_name))

        new_list = MenuButton(screen_name=screen_name)
        new_list.text = list_name
        self.screens_list.add_widget(new_list)


class LowerMenuLayout(MDBoxLayout):
    task_screens_scroll_view: ScrollViewTasksList = ObjectProperty()
    '''
    Нижняя часть меню
    '''
    pass


class UpperMenuLayout(MDBoxLayout):
    '''
    Тут верхняя часть меню
    '''
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
        self.SAVE_FOLDER = SAVE_FOLDER
        self.TASKS_SAVE_NAME = TASKS_SAVE_NAME
        self.TASKS_SAVE_PATH = TASKS_SAVE_PATH
        self.SCREENS_SAVE_PATH = SCREENS_SAVE_PATH
        self.SCREENS_SAVE_NAME = SCREENS_SAVE_NAME

        self.screen_manager.transition = NoTransition()

    def open_menu(self, instance=None):
        self.main_menu.nav_bar.set_state("open")

    def get_screen_manager(self):
        return self.screen_manager

    def load_tasks(self):
        if (
                not os.path.exists(self.SAVE_FOLDER) or
                os.listdir(self.SAVE_FOLDER) == [".gitignore"] or
                f"{self.TASKS_SAVE_NAME}.json" not in os.listdir(self.SAVE_FOLDER)
        ):
            return

        with open(self.TASKS_SAVE_PATH, "r") as f:
            save = json.load(f)

        tasks_man = get_tasks_manager()

        save: dict = save[self.TASKS_SAVE_NAME]
        for task_id in save.keys():
            task_params = save[task_id]
            task = Task(task_id=int(task_id), task_text=task_params["text"])
            tasks_man.add_new_task(task)
            if task_params["is_important"]:
                task.make_important()
            if task_params["is_done"]:
                task.mark_done()
            task.update_parents(task_params["belongs_to"])
        tasks_man.reload_current_screen()

    def save_tasks(self):
        if not os.path.exists(self.SAVE_FOLDER):
            os.mkdir(self.SAVE_FOLDER)
            with open(f"{self.SAVE_FOLDER}/.gitignore", "w") as gitignore:
                gitignore.writelines(["*", "!.gitignore"])

        data = {self.TASKS_SAVE_NAME: {}}
        cur_save = data[self.TASKS_SAVE_NAME]
        for task in get_tasks_manager().tasks:
            cur_task = cur_save[task.task_id] = {}
            cur_task["text"] = task.get_text()
            cur_task["is_important"] = task.is_important
            cur_task["is_done"] = task.is_done
            cur_task["belongs_to"] = list(task.belongs_to)

        with open(self.TASKS_SAVE_PATH, 'w') as f:
            json.dump(data, f)

    def save_screens(self):
        if not os.path.exists(self.SAVE_FOLDER):
            os.mkdir(self.SAVE_FOLDER)
            with open(f"{self.SAVE_FOLDER}/.gitignore", "w") as gitignore:
                gitignore.writelines(["*", "!.gitignore"])

        data = {self.SCREENS_SAVE_NAME: {}}
        cur_save = data[self.SCREENS_SAVE_NAME]
        for menu_button in self.main_menu.lower.task_screens_scroll_view.screens_list.children:
            menu_button: MenuButton
            cur_screen = cur_save[menu_button.text] = {}
            cur_screen["screen_name"] = menu_button.screen_name

        with open(self.SCREENS_SAVE_PATH, 'w') as f:
            json.dump(data, f)

    def load_screens(self):
        if (
                not os.path.exists(self.SAVE_FOLDER) or
                os.listdir(self.SAVE_FOLDER) == [".gitignore"] or
                f"{self.SCREENS_SAVE_NAME}.json" not in os.listdir(self.SAVE_FOLDER)
        ):
            return

        with open(self.SCREENS_SAVE_PATH, "r") as f:
            save = json.load(f)
        save: dict = save[self.SCREENS_SAVE_NAME]

        tasks_man = get_tasks_manager()

        tasks_lists_list = self.main_menu.lower.task_screens_scroll_view.screens_list
        for menu_button_text in save.keys():
            tasks_lists_list.add_widget(MenuButton(text=menu_button_text, screen_name=save[menu_button_text]["screen_name"]))
            self.screen_manager.add_widget(TasksScreen(name=save[menu_button_text]["screen_name"]))

        tasks_man.reload_all_screens()


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
        self.main_container.load_screens()

    def on_stop(self):
        self.main_container.save_tasks()
        self.main_container.save_screens()

    def get_main_container(self) -> MainContainer:
        return self.main_container

    def get_tasks_manager(self):
        return self.tasks_manager


def main():
    app = TodoApp()
    app.run()


if __name__ == '__main__':
    main()
