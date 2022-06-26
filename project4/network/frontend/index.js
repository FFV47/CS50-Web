// Import all bootstrap plugins
import "./main.css";

import React from "react";
import ReactDOM from "react-dom/client";

import { QueryClient, QueryClientProvider } from "react-query";
import { ReactQueryDevtools } from "react-query/devtools";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import App from "./App";
import Following from "./components/Following";
import Home from "./components/Home";
import Profile from "./components/Profile";
import { GlobalProvider } from "./context/GlobalContext";

const queryClient = new QueryClient();

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <GlobalProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<App />}>
              {/* Index route renders in the parent's outlet at the parent's URL */}
              <Route index element={<Home />} />
              <Route path=":urlPage" element={<Home />} />
              <Route path="/profile">
                <Route index element={<Profile />} />
                <Route path=":username"></Route>
              </Route>
              <Route path="/following" element={<Following />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </GlobalProvider>
      <ReactQueryDevtools />
    </QueryClientProvider>
  </React.StrictMode>
);
