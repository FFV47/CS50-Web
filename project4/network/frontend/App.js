import React from "react";
import { Routes, Route } from "react-router-dom";

import Home from "./components/Home";
import Profile from "./components/Profile";
import Following from "./components/Following";

const App = () => (
  <main>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/following" element={<Following />} />
    </Routes>
  </main>
);

export default App;
