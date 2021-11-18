from kivy.uix.screenmanager import ScreenManager
from main import Task, get_screen_manager


class TasksManager:
    def __init__(self):
        self.tasks = list()

    def add_new_task(self, task: Task):
        task.task_id = len(self.tasks)
        self.tasks.append(task)

    def create_new_task(self):
        task = Task()
        task.task_id = len(self.tasks)
        task.update_parents([get_screen_manager().current])
        self.tasks.append(task)

    def add_task_to_screen(self, task_id, screen_name):
        self.tasks[task_id].belongs_to.add(screen_name)
        self.reload_current_screen()

    def delete_task(self, task_id):
        self.tasks.pop(task_id)
        self.get_current_screen().delete_task(task_id)
        self.reidentify()

    def reidentify(self):
        for new_task_id in range(len(self.tasks)):
            for task in self.get_current_screen().tasks.children:
                if task.task_id == self.tasks[new_task_id].task_id:
                    task.task_id = new_task_id
                    break
            self.tasks[new_task_id].task_id = new_task_id

    def reload_current_screen(self):
        cur_screen = self.get_current_screen()
        cur_screen.reload()

    def get_tasks_for_screen(self, screen_name=None):
        screen_manager: ScreenManager = get_screen_manager()
        screen_name = screen_name if screen_name else screen_manager.current
        tasks_to_load = [self.copy_task(task.task_id) for task in self.tasks if screen_name in task.belongs_to]
        tasks_to_load.sort(key=lambda t: t.task_id)
        return tasks_to_load

    def copy_task(self, task_id):
        parent_task: Task = self.tasks[task_id]
        copy = Task(task_id=task_id, task_text=parent_task.get_text())
        if parent_task.is_important:
            copy.make_important()
        if parent_task.is_done:
            copy.mark_done()
        return copy

    def reload_all_screens(self):
        screens = get_screen_manager().screens
        for screen in screens:
            screen.reload()

    def get_task(self, task_id):
        return self.copy_task(task_id)

    def get_current_screen(self):
        return get_screen_manager().current_screen
