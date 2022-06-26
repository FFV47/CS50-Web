import React from "react";
import { Outlet } from "react-router-dom";

const App = () => {
  return (
    <>
      <main className="container">
        <Outlet />
      </main>
    </>
  );
};

export default App;
