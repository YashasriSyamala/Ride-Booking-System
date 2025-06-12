import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import 'primereact/resources/themes/nano/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <App />
);
