const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const app = express();

app.use(bodyParser.json());
app.use(cors());

// Sample tasks with descriptions and due dates
let tasks = [
  { id: 1, text: 'Sample task 1', description: 'This is a description for task 1', completed: false, dueDate: null },
  { id: 2, text: 'Sample task 2', description: 'This is a description for task 2', completed: false, dueDate: null },
];

// GET all tasks
app.get('/tasks', (req, res) => {
  res.json(tasks);
});

// POST a new task (with description and due date)
app.post('/tasks', (req, res) => {
  const { text, description, dueDate } = req.body;

  // Validate that text and description are provided
  if (!text || !description) {
    return res.status(400).json({ message: 'Task text and description are required' });
  }

  // Ensure dueDate is stored as a Date object (or null if not provided)
  const newTask = {
    id: Date.now(),
    text,
    description,
    completed: false,
    dueDate: dueDate ? new Date(dueDate) : null,
  };

  tasks.push(newTask);
  res.status(201).json(newTask);
});

// PATCH to toggle task completion
app.patch('/tasks/:id', (req, res) => {
  const { id } = req.params;
  const task = tasks.find(t => t.id === parseInt(id));

  if (!task) {
    return res.status(404).json({ message: 'Task not found' });
  }

  task.completed = !task.completed;
  res.json(task);
});

// PUT to update task details (description, due date)
app.put('/tasks/:id', (req, res) => {
  const { id } = req.params;
  const { description, dueDate } = req.body;

  const task = tasks.find(t => t.id === parseInt(id));

  if (!task) {
    return res.status(404).json({ message: 'Task not found' });
  }

  // Update task fields if provided
  if (description) {
    task.description = description;
  }

  if (dueDate) {
    task.dueDate = new Date(dueDate);
  }

  res.json(task);
});

// DELETE a task
app.delete('/tasks/:id', (req, res) => {
  const { id } = req.params;
  tasks = tasks.filter(t => t.id !== parseInt(id));

  res.status(204).send();
});

// Start the server
const PORT = process.env.PORT || 5001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});