import React, { useState, useEffect } from "react";
import api from "../services/api";

const TaskList = () => {
  const [tasks, setTasks] = useState([]);
  const [editingTask, setEditingTask] = useState(null);
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [showAddTaskForm, setShowAddTaskForm] = useState(false);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await api.get("/api/tasks/");
        setTasks(response.data);
      } catch (error) {
        console.error("Error fetching tasks:", error);
      }
    };
    fetchTasks();
  }, []);

  const handleDelete = async (taskId) => {
    try {
      await api.delete(`/api/tasks/${taskId}/`);
      setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };

  const handleEdit = (task) => {
    setEditingTask(task);
    setNewTitle(task.title);
    setNewDescription(task.description);
  };

  const handleUpdate = async () => {
    if (!editingTask) return;

    try {
      const response = await api.put(`/api/tasks/${editingTask.id}/`, {
        title: newTitle,
        description: newDescription,
      });

      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === editingTask.id ? response.data : task
        )
      );
      setEditingTask(null);
      setNewTitle("");
      setNewDescription("");
    } catch (error) {
      console.error("Error updating task:", error);
    }
  };

  const handleAddTask = async () => {
    if (!newTitle || !newDescription) {
      alert("Please enter both title and description");
      return;
    }

    try {
      const response = await api.post("/api/tasks/", {
        title: newTitle,
        description: newDescription,
      });

      setTasks((prevTasks) => [...prevTasks, response.data]);
      setNewTitle("");
      setNewDescription("");
      setShowAddTaskForm(false);
    } catch (error) {
      console.error("Error adding task:", error);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-semibold mb-4">Task List</h1>
      <button
        onClick={() => setShowAddTaskForm(true)}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 mb-4"
      >
        Add New Task
      </button>

      {showAddTaskForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-10">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h2 className="text-xl font-bold mb-4">Add New Task</h2>
            <input
              type="text"
              placeholder="Title"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1 w-full mb-2"
            />
            <textarea
              placeholder="Description"
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1 w-full mb-4"
            />
            <div className="flex justify-between">
              <button
                onClick={handleAddTask}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                Add Task
              </button>
              <button
                onClick={() => setShowAddTaskForm(false)}
                className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {tasks.map((task) => (
          <div
            key={task.id}
            className="bg-white p-4 shadow rounded-lg flex justify-between items-center"
          >
            {editingTask?.id === task.id ? (
              <div className="w-full">
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 w-full mb-2"
                />
                <textarea
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 w-full mb-2"
                />
                <div className="flex space-x-2">
                  <button
                    onClick={handleUpdate}
                    className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => setEditingTask(null)}
                    className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="w-full">
                <h2 className="text-xl font-bold">{task.title}</h2>
                <p className="text-gray-700">{task.description}</p>
                <div className="flex space-x-2 mt-2">
                  <button
                    onClick={() => handleEdit(task)}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(task.id)}
                    className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                  >
                    Delete
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default TaskList;
