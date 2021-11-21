from main import Task, get_screen_manager, get_current_screen


class TasksManager:
    def __init__(self):
        self.tasks = list()

    def add_new_task(self, task: Task):
        self.tasks.append(task)

    def create_new_task(self):
        task = Task()
        task.task_id = len(self.tasks)
        task.update_parents([get_screen_manager().current, ])
        self.tasks.append(task)
        self.reload_current_screen()

    def add_task_to_screen(self, task_id, screen_name):
        self.tasks[task_id].belongs_to.add(screen_name)
        self.reload_current_screen()

    def delete_task(self, task_id):
        self.tasks.pop(task_id)
        self.reidentify()

    def reidentify(self):
        for new_task_id in range(len(self.tasks)):
            self.tasks[new_task_id].task_id = new_task_id
        self.reload_current_screen()

    def reload_current_screen(self):
        cur_screen = get_current_screen()
        cur_screen.reload()

    def get_tasks_for_screen(self, screen_name=None):
        screen_manager = get_screen_manager()
        screen_name = screen_name if screen_name else screen_manager.current
        tasks_to_load = [task for task in self.tasks if screen_name in task.belongs_to]
        return tasks_to_load

    def reload_all_screens(self):
        screens = get_screen_manager().screens
        for screen in screens:
            screen.reload()

    def get_task(self, task_id):
        return self.tasks[task_id]
