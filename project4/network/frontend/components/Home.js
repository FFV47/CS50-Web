import React from "react";
import { useParams } from "react-router-dom";

import usePaginatedPosts from "../hooks/usePaginatedPosts";
import NewPost from "./NewPost";
import PageControl from "./PageControl";
import Post from "./Post";

const Home = () => {
  const params = useParams();
  const urlPage = params.urlPage ? parseInt(params.urlPage, 10) : 1;

  const postsQueryKey = ["posts", urlPage];

  const postsQuery = usePaginatedPosts(postsQueryKey);

  return (
    <>
      <h1 className="mt-3">All Posts</h1>

      <NewPost postsQueryKey={postsQueryKey} />

      <PageControl
        urlPage={urlPage}
        isPreviousData={postsQuery.isPreviousData}
        nextPage={postsQuery.data?.nextPage}
      />
      <section id="post-section">
        {!postsQuery.isLoading && !postsQuery.isError && postsQuery.isFetching && (
          <p>Refreshing...</p>
        )}

        {postsQuery.isLoading && <p>Loading...</p>}

        {!postsQuery.isLoading && postsQuery.isError && (
          <p>Error: {postsQuery.error.message}</p>
        )}

        {!postsQuery.isLoading && !postsQuery.isError && (
          <div>
            {postsQuery.data.posts.map((post) => (
              <Post key={post.id} post={post} postsQueryKey={postsQueryKey} />
            ))}
          </div>
        )}
        {/*  */}
      </section>
      {/* {!postsQuery.isLoading && !postsQuery.isError && (
        <PageControl
          urlPage={urlPage}
          isPreviousData={postsQuery.isPreviousData}
          nextPage={postsQuery.data?.nextPage}
        />
      )} */}
    </>
  );
};

export default Home;
