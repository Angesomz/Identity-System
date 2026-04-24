import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Adjust if backend is on different port/host

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a response interceptor to handle errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

export const enrollIdentity = async (data) => {
    return await api.post('/enroll', data);
};

export const identifyFace = async (data) => {
    return await api.post('/search/identify', data);
};

export const scanIDDocument = async (data) => {
    return await api.post('/ocr/scan-id', data);
};

export default api;
