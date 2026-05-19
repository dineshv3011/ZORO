import json
import os
from datetime import datetime

class TaskManager:
    def __init__(self):
        self.tasks_file = "tasks.json"
        self.tasks = self._load_tasks()

    def _load_tasks(self):
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        return []

    def _save_tasks(self):
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, task_text):
        """Add a new task"""
        task = {
            "id": len(self.tasks) + 1,
            "task": task_text,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "done": False
        }
        self.tasks.append(task)
        self._save_tasks()
        return f"Task added: {task_text}"

    def get_pending_tasks(self):
        """Return all pending tasks"""
        return [t for t in self.tasks if not t['done']]

    def complete_task(self, task_id):
        """Mark a task as complete"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['done'] = True
                self._save_tasks()
                return f"Task completed: {task['task']}"
        return "Task not found."

    def get_today_summary(self):
        """Get a voice-friendly summary of today's tasks"""
        pending = self.get_pending_tasks()
        if not pending:
            return "You have no pending tasks. Great job!"
        summary = f"You have {len(pending)} pending task{'s' if len(pending) > 1 else ''}. "
        for i, task in enumerate(pending[:3], 1):
            summary += f"Task {i}: {task['task']}. "
        if len(pending) > 3:
            summary += f"And {len(pending) - 3} more."
        return summary

    def list_tasks(self):
        """List all pending tasks"""
        pending = self.get_pending_tasks()
        if not pending:
            return "No pending tasks!"
        return "\n".join([f"{t['id']}. {t['task']}" for t in pending])
