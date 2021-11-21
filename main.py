import json
import os
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import OneLineIconListItem, IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from constants import *
from kivymd.app import MDApp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.uix.stacklayout import MDStackLayout


def get_screen_manager():
    return MDApp.get_running_app().get_main_container().get_screen_manager()


class TasksScreen(MDScreen):
    tasks: GridLayout = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_tasks = []


    def open_sort_menu(self):
        # MDApp.get_running_app().get_main_container().toolbar
        pass

    def delete_task(self, task, delete_from_presaved=False):
        self.tasks.remove_widget(task)
        if delete_from_presaved:
            if task in self.all_tasks:
                self.all_tasks.remove(task)

    def get_tasktext_for_searching(self):
        return MDApp.get_running_app().get_main_container().toolbar.search_text_field.text

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

    def search_task(self):
        if not self.all_tasks:
            self.all_tasks = self.get_tasks()

        self.delete_all_tasks()

        search = self.get_tasktext_for_searching()
        if search != '':
            for task in self.all_tasks:
                if search in task.get_task_text():
                    self.add_task(task)
        else:
            self.import_tasks(self.all_tasks)
            self.all_tasks = []

    def delete_all_tasks(self):
        for i in self.get_tasks():
            self.delete_task(i)

    def sort_tasks_alphabet(self):
        # SORT ALFABET
        new_tasks_text = sorted([task.get_task_text() for task in self.get_tasks()])
        new_tasks = []
        for label in new_tasks_text:
            for task in self.get_tasks():
                if task.get_task_text() == label:
                    new_tasks.append(task)

        self.delete_all_tasks()
        self.import_tasks(new_tasks[::-1])

    def sort_tasks_alphabet_reversed(self):
        # SORT ALFABET
        new_tasks_text = sorted([task.get_task_text() for task in self.get_tasks()])
        new_tasks = []
        for label in new_tasks_text:
            for task in self.get_tasks():
                if task.get_task_text() == label:
                    new_tasks.append(task)

        self.delete_all_tasks()
        self.import_tasks(new_tasks)

    def sort_task_important_up(self):
        tasks_important = []
        tasks_NOT_important = []
        for task in self.get_tasks():
            if task.get_is_important():
                tasks_important.append(task)
            elif not task.get_is_important():
                tasks_NOT_important.append(task)
        new_task = tasks_important + tasks_NOT_important
        self.delete_all_tasks()
        self.import_tasks(new_task[::-1])

    def sort_task_important_down(self):
        tasks_important = []
        tasks_NOT_important = []
        for task in self.get_tasks():
            if task.get_is_important():
                tasks_important.append(task)
            elif not task.get_is_important():
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

    def __init__(self, id=0, task_text="", **kwargs):
        super().__init__(**kwargs)
        self.id = id

        self.task_input_field.text = task_text

        self.is_done = False
        self.is_important = False

    def delete_task(self):
        screen_manager: ScreenManager = get_screen_manager()
        screen_manager.current_screen.delete_task(self, delete_from_presaved=True)

    def make_important(self):
        self.is_important = not self.is_important

    def mark_done(self):
        self.is_done = not self.is_done
        self.task_checkbox.active = self.is_done

    def get_text(self):
        return self.task_input_field.text

    def get_task_text(self):
        return self.task_input_field.text

    def get_is_important(self):
        return self.is_important


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
                # "on_release": pass
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

    def open_menu(self):
        pass

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
        self.children[0].children[0].add_widget(newList)


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
        self.screen_manager.add_widget(TasksScreen(name="test"))
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
                new_task = Task(id=id, task_text=task["text"])
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
        #self.main_container.load_tasks()
        pass

    def on_stop(self):
        self.main_container.save_tasks()

    def get_main_container(self):
        return self.main_container


def main():
    app = TodoApp()
    app.run()


if __name__ == '__main__':
    main()
