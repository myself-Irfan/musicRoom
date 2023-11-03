import React from "react";
import ReactDOM from "react-dom/client";
import App from "./components/App";
import { BrowserRouter as Router } from "react-router-dom";

//create a root obj from document with app id
const root = ReactDOM.createRoot(document.getElementById("app"));
//render app component to root obj
root.render(
    <Router>
        <App />
    </Router>
);
