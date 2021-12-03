import datetime
import json
import os
from kivy.graphics import Color
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineIconListItem, MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDToolbar
import tasks_manager
from constants import *
from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import NoTransition, ScreenManager


def get_main_container():
    return MDApp.get_running_app().get_main_container()


def get_screen_manager() -> ScreenManager:
    return get_main_container().get_screen_manager()


def get_tasks_manager():
    return MDApp.get_running_app().get_tasks_manager()


class TasksMenuDrawer(MDNavigationDrawer):
    task_text_field: MDTextField = ObjectProperty()
    done_checkbox: MDCheckbox = ObjectProperty()
    important_button: MDIconButton = ObjectProperty()
    deadline_label: MDLabel = ObjectProperty()
    priority_label: MDLabel = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task = None

    def load_task(self, task_id):
        self.task = get_tasks_manager().get_task(task_id)
        self.task_text_field.text = self.task.get_text()
        self.done_checkbox.active = self.task.is_done
        self.deadline_label.text = "Дедлайн " + self.task.deadline
        self.priority_label.text = "Приоритетность " + NUMBER_TO_PRIORITY[self.task.priority]
        self.compare_data()

    def compare_data(self):
        if self.task.deadline != "":
            if datetime.datetime.date(datetime.datetime.now()) > datetime.datetime.strptime(self.task.deadline,
                                                                                            "%Y-%m-%d").date():
                self.deadline_label.text_color = "#F2090D"
        if self.task.is_important:
            self.important_button.icon = 'cards-heart'
            self.important_button.text_color = "#FF0000"
        else:
            self.important_button.icon = 'cards-heart-outline'
            self.important_button.text_color = "#000000"

    def make_important(self):
        self.task.make_important()
        self.compare_data()

    def open(self):
        self.set_state("open")

    def mark_done(self):
        self.task.mark_done()

    def change_task_text(self):
        self.task.set_text(self.task_text_field.text)

    def on_save(self, instance, value, date_range):
        self.deadline_label.text = "Дедлайн " + str(value)
        self.task.deadline = str(value)

    def open_calendar(self):
        picker = MDDatePicker(min_date=datetime.date.today(),
                              max_date=datetime.date(datetime.date.today().year + 4, 1, 1))
        picker.bind(on_save=self.on_save)
        picker.open()

    def set_priority(self, priority):
        self.task.set_priority(priority)
        self.priority_label.text = "Приоритетность " + priority

    def open_priority_menu(self, instance):
        menu_items = [
            {
                "text": "Очень важная",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_priority("Очень важная")
            },
            {
                "text": "Важная",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_priority("Важная")
            },
            {
                "text": "Обычная",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_priority("Обычная")
            },
            {
                "text": "Низкая",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_priority("Низкая")
            },
            {
                "text": "Очень низкая",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_priority("Очень низкая")
            }
        ]

        menu = MDDropdownMenu(
            items=menu_items,
            width_mult=3,
        )

        menu.caller = instance
        menu.open()


class TasksScreen(MDScreen):
    tasks: GridLayout = ObjectProperty()
    calling_button: OneLineIconListItem = ObjectProperty()
    info_drawer: TasksMenuDrawer = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.not_sorted = []

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
            if not task.is_done or self.name == "done_tasks":
                self.add_task(task)
                task.menu_btn.text_color = "#FFFFFF"
            if not task.is_done and self.name != "done_tasks" and task.deadline != "":
                if datetime.datetime.date(datetime.datetime.now()) > datetime.datetime.strptime(task.deadline,
                                                                                                "%Y-%m-%d").date():
                    task.menu_btn.text_color = "#F2090D"

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

    def sort_return(self):
        if self.not_sorted != []:
            self.delete_all_tasks()
            self.import_tasks(self.not_sorted)

    def sort_tasks_alphabet(self):
        # SORT ALFABET
        if self.not_sorted == []:
            self.not_sorted = self.get_tasks()
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
        if self.not_sorted == []:
            self.not_sorted = self.get_tasks()        # SORT ALFABET
        new_tasks_text = sorted([task.get_text() for task in self.get_tasks()])
        new_tasks = []
        for label in new_tasks_text:
            for task in self.get_tasks():
                if task.get_text() == label and task not in new_tasks:
                    new_tasks.append(task)

        self.delete_all_tasks()
        self.import_tasks(new_tasks)

    def sort_deadline(self):
        if self.not_sorted == []:
            self.not_sorted = self.get_tasks()
        dates = [task.get_deadline() for task in self.get_tasks()]
        task_dates = [date for date in dates if date != '']
        task_dates.sort()
        task_to_scr_last = []
        task_to_scr = []
        for date in task_dates:
            for task in self.get_tasks():
                if date == task.get_deadline() and task not in task_to_scr:
                    task_to_scr.append(task)
                elif task.get_deadline() == '' and task not in task_to_scr_last:
                    task_to_scr_last.append(task)
        self.delete_all_tasks()
        self.import_tasks((task_to_scr + task_to_scr_last)[::-1])

    def sort_task_important_up(self):
        if self.not_sorted == []:
            self.not_sorted = self.get_tasks()
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
        if self.not_sorted == []:
            self.not_sorted = self.get_tasks()
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
        self.deadline = ""
        self.priority = 3
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
        tasks_man: tasks_manager.TasksManager = get_tasks_manager()
        if not self.is_important:
            self.make_imp_btn.icon = 'cards-heart'
            self.make_imp_btn.text_color = "#FF0000"
            self.is_important = True
            tasks_man.add_task_to_screen(self.task_id, "important")
        else:
            self.make_imp_btn.icon = 'cards-heart-outline'
            self.make_imp_btn.text_color = "#FFFFFF"
            self.is_important = False
            self.belongs_to.remove("important")
            tasks_man.reload_all_screens()

    def mark_done(self):
        self.is_done = not self.is_done
        self.repaint()
        if self.is_done:
            get_tasks_manager().add_task_to_screen(self.task_id, "done_tasks")
        else:
            self.belongs_to.remove('done_tasks')
        get_screen_manager().current_screen.reload()
        self.task_checkbox.active = self.is_done

    def set_priority(self, priority):
        self.priority = PRIORITY_TO_NUMBER[priority]

    def open_additional_info(self):
        info: TasksMenuDrawer = get_current_screen().info_drawer
        info.load_task(self.task_id)
        info.open()

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

    def set_text(self, text):
        self.task_input_field.text = text

    def set_deadline(self, new_deadline):
        self.deadline = new_deadline

    def get_deadline(self):
        return self.deadline


class ToolBar(MDBoxLayout):
    search_text_field: MDTextField = ObjectProperty()
    left_toolbar: MDToolbar = ObjectProperty()

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
            },
            {
                "text": "дедлайн",
                "left_icon": "sort-alphabetical-descending",
                "viewclass": "RightContentCls",
                "on_release": self.sort_deadline
            },
            {
                "text": "вернуть все",
                "left_icon": "sort-alphabetical-descending",
                "viewclass": "RightContentCls",
                "on_release": self.sort_return
            }
        ]
        self.sort_menu = MDDropdownMenu(
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
        self.sort_menu.caller = instance
        self.sort_menu.open()

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

    def sort_return(self):
        get_screen_manager().current_screen.sort_return()

    def sort_deadline(self):
        get_screen_manager().current_screen.sort_deadline()

class MenuButton(OneLineIconListItem):
    '''
    Класс кнопки, меняющей экран
    '''

    def __init__(self, screen_name=None, **kwargs):
        super().__init__(**kwargs)
        if screen_name:
            self.screen_name = screen_name

    def mark_active(self, prev):
        self.bg_color = list(map(lambda x: x - TASK_BUTTON_ACTIVE_COLOR_DELTA, TASK_BUTTON_DEFAULT_COLOR))
        container: MainContainer = get_main_container()
        container.toolbar.left_toolbar.title = self.text
        if prev:
            prev.bg_color = TASK_BUTTON_DEFAULT_COLOR

    def change_screen(self):
        screen_manager = get_screen_manager()

        if screen_manager.current == self.screen_name:
            screen_manager.current_screen.calling_button = self
            return

        self.mark_active(screen_manager.current_screen.calling_button)

        screen_manager.current_screen.delete_all_tasks()

        screen_manager.current = self.screen_name
        screen_manager.current_screen.calling_button = self

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
        self.new_list_field.text = ""


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
    start_button: MenuButton = ObjectProperty()


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

        self.screen_manager.transition = NoTransition()

    def open_menu(self, instance=None):
        self.main_menu.nav_bar.set_state("open")

    def get_screen_manager(self):
        return self.screen_manager

    def load_tasks(self):
        if (
                not os.path.exists(SAVE_FOLDER) or
                os.listdir(SAVE_FOLDER) == [".gitignore"] or
                f"{TASKS_SAVE_NAME}.json" not in os.listdir(SAVE_FOLDER)
        ):
            return

        with open(TASKS_SAVE_PATH, "r") as f:
            save = json.load(f)

        tasks_man = get_tasks_manager()

        save: dict = save[TASKS_SAVE_NAME]
        for task_id in save.keys():
            task_params = save[task_id]
            task = Task(task_id=int(task_id), task_text=task_params["text"])
            tasks_man.add_new_task(task)
            if task_params["is_important"]:
                task.make_important()
            if task_params["is_done"]:
                task.mark_done()
            task.update_parents(task_params["belongs_to"])
            task.priority = task_params["priority"]
            task.deadline = task_params["deadline"]
        tasks_man.reload_current_screen()

    def save_tasks(self):
        if not os.path.exists(SAVE_FOLDER):
            os.mkdir(SAVE_FOLDER)
            with open(f"{SAVE_FOLDER}/.gitignore", "w") as gitignore:
                gitignore.writelines(["*", "!.gitignore"])

        data = {TASKS_SAVE_NAME: {}}
        cur_save = data[TASKS_SAVE_NAME]
        for task in get_tasks_manager().tasks:
            cur_task = cur_save[task.task_id] = {}
            cur_task["text"] = task.get_text()
            cur_task["is_important"] = task.is_important
            cur_task["is_done"] = task.is_done
            cur_task["belongs_to"] = list(task.belongs_to)
            cur_task["deadline"] = task.deadline
            cur_task["priority"] = task.priority

        with open(TASKS_SAVE_PATH, 'w') as f:
            json.dump(data, f)

    def save_screens(self):
        if not os.path.exists(SAVE_FOLDER):
            os.mkdir(SAVE_FOLDER)
            with open(f"{SAVE_FOLDER}/.gitignore", "w") as gitignore:
                gitignore.writelines(["*", "!.gitignore"])

        data = {SCREENS_SAVE_NAME: {}}
        cur_save = data[SCREENS_SAVE_NAME]
        for menu_button in self.main_menu.lower.task_screens_scroll_view.screens_list.children:
            menu_button: MenuButton
            cur_screen = cur_save[menu_button.text] = {}
            cur_screen["screen_name"] = menu_button.screen_name

        with open(SCREENS_SAVE_PATH, 'w') as f:
            json.dump(data, f)

    def load_screens(self):
        if (
                not os.path.exists(SAVE_FOLDER) or
                os.listdir(SAVE_FOLDER) == [".gitignore"] or
                f"{SCREENS_SAVE_NAME}.json" not in os.listdir(SAVE_FOLDER)
        ):
            return

        with open(SCREENS_SAVE_PATH, "r") as f:
            save = json.load(f)
        save: dict = save[SCREENS_SAVE_NAME]

        tasks_man = get_tasks_manager()

        tasks_lists_list = self.main_menu.lower.task_screens_scroll_view.screens_list
        for menu_button_text in save.keys():
            tasks_lists_list.add_widget(
                MenuButton(text=menu_button_text, screen_name=save[menu_button_text]["screen_name"]))
            self.screen_manager.add_widget(TasksScreen(name=save[menu_button_text]["screen_name"]))

        tasks_man.reload_all_screens()


class TodoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks_manager = tasks_manager.TasksManager()

    def build(self):
        self.main_container = MainContainer()
        return self.main_container

    def on_start(self):
        self.main_container.load_tasks()
        self.main_container.load_screens()
        self.main_container.main_menu.upper.start_button.mark_active(None)

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
