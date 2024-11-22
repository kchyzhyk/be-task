import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import TaskList from './components/TaskList';

const App = () => (
    <Router>
        <Routes>
            <Route path="/" element={<TaskList />} />
        </Routes>
    </Router>
);

export default App;
