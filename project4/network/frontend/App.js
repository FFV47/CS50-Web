import React from "react";
import { Route, Routes } from "react-router-dom";

import Following from "./components/Following";
import Home from "./components/Home";
import Profile from "./components/Profile";

const App = () => (
  <main>
    <Routes>
      <Route path="/" element={<Home />}>
        <Route path=":urlPage" element={<Home />} />
      </Route>
      <Route path="/profile" element={<Profile />} />
      <Route path="/following" element={<Following />} />
    </Routes>
  </main>
);

export default App;
