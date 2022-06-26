import React from "react";

import NewPost from "./NewPost";
import Feed from "./Feed";
import useGlobalContext from "../context/GlobalContext";

const Home = () => {
  const { authenticated } = useGlobalContext();

  return (
    <>
      <h1 className="display-4 text-center mt-3">All Posts</h1>

      {authenticated && <NewPost />}
      <Feed />
    </>
  );
};

export default Home;
