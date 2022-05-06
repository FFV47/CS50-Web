import React from "react";
import NewPost from "./NewPost";

const Home = () => {
  const userLoggedIn = JSON.parse(document.getElementById("djangoUser").textContent);
  return (
    <>
      <NewPost />
    </>
  );
};

export default Home;
