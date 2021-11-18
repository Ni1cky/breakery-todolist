from kivy.uix.screenmanager import ScreenManager
from main import Task, get_screen_manager


class TasksManager:
    def __init__(self):
        self.tasks = list()

    def add_task(self, task: Task):
        self.tasks.append(task)

    def add_task_to_screen(self, task_id, screen_name):
        self.tasks[task_id].belongs_to.add(screen_name)
        self.reload_screen()

    def delete_task(self, task_id):
        self.tasks.pop(task_id)
        self.reidentify()

    def reidentify(self):
        for task_id in range(len(self.tasks)):
            self.tasks[task_id].task_id = task_id
        self.reload_screen()

    def reload_screen(self, screen_name=None):
        screen_manager: ScreenManager = get_screen_manager()
        screen_to_reload_name = screen_manager.get_screen(screen_name) if screen_name else screen_manager.current
        # if no screen_name is passed - reload current
        screen_to_reload = screen_manager.get_screen(screen_to_reload_name)
        screen_to_reload.reload(tasks_to_load=self.get_tasks_for_screen(screen_to_reload_name))

    def get_tasks_for_screen(self, screen_name):
        screen_manager: ScreenManager = get_screen_manager()
        cur_screen_name = screen_manager.get_screen(screen_name) if screen_name else screen_manager.current
        tasks_to_load = [task.copy() for task in self.tasks if cur_screen_name in task.belongs_to]
        tasks_to_load.sort(key=lambda t: t.task_id)
        return tasks_to_load

    def reload_all_screens(self):
        screen_names = get_screen_manager().screen_names
        for screen_name in screen_names:
            self.reload_screen(screen_name)
