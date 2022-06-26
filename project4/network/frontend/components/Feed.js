import React from "react";

import useGlobalContext from "../context/GlobalContext";
import usePaginatedPosts from "../hooks/usePaginatedPosts";
import { ImSpinner5 } from "react-icons/im";

import PageControl from "./PageControl";
import Post from "./Post";

const Feed = () => {
  const { postsQueryKey } = useGlobalContext();

  const postsQuery = usePaginatedPosts(postsQueryKey);
  return (
    <>
      <PageControl postsQuery={postsQuery} />

      <section id="posts-section">
        {(!postsQuery.isLoading && !postsQuery.isError && postsQuery.isFetching) ||
        postsQuery.isLoading ? (
          <div className="center mb-3">
            <ImSpinner5 aria-hidden="true" className="loading-spinner" />
          </div>
        ) : (
          ""
        )}

        {!postsQuery.isLoading && postsQuery.isError && (
          <p className="alert alert-danger" role="alert">
            {postsQuery.error.message}
          </p>
        )}

        {!postsQuery.isLoading && !postsQuery.isError && (
          <ul className="list-unstyled">
            {postsQuery.data.posts.map((post) => (
              <Post key={post.id} post={post} />
            ))}
          </ul>
        )}
      </section>
    </>
  );
};

export default Feed;
