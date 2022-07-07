import "./main.css";

import React from "react";
import ReactDOM from "react-dom/client";

import { QueryClient, QueryClientProvider } from "react-query";
import { ReactQueryDevtools } from "react-query/devtools";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import App from "./components/App";
import Following from "./components/Following";
import Home from "./components/Home";
import Profile from "./components/Profile/Profile";
import { DataProvider } from "./context/DataContext";

const queryClient = new QueryClient();

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />}>
            {/* Index route renders in the parent's outlet at the parent's URL */}
            <Route element={<DataProvider />}>
              <Route index element={<Home />} />
              <Route path=":urlPage" element={<Home />} />
              <Route path="/profile/:username/">
                <Route index element={<Profile />} />
                <Route path=":urlPage" element={<Profile />} />
              </Route>
              <Route path="/following">
                <Route index element={<Following />} />
                <Route path=":urlPage" element={<Following />} />
              </Route>
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
      <ReactQueryDevtools />
    </QueryClientProvider>
  </React.StrictMode>
);
