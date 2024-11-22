import axios from 'axios';


localStorage.setItem('token', '37f4d8daf56e89a94fc5c292e40c69e9c49f4dc6');

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/',
    headers: {
        Authorization: `Token ${localStorage.getItem('token')}`,
    },
});

export default api;
