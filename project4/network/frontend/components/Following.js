import useDataContext from "../context/DataContext";
import usePaginatedPosts from "../hooks/usePaginatedPosts";

import Feed from "./Feed/Feed";

const Following = () => {
  const { queryKey } = useDataContext();

  const { isLoading, isFetching, isError, data, error, isPreviousData } =
    usePaginatedPosts(queryKey, "following_posts");

  return (
    <>
      <h1 className="display-4 text-center mt-3">Following Posts</h1>
      {data?.posts.length ? (
        <Feed
          isLoading={isLoading}
          isFetching={isFetching}
          isError={isError}
          data={data}
          error={error}
          isPreviousData={isPreviousData}
          hasParentSpin={false}
        />
      ) : (
        <p className="h3 text-center mt-5">No posts to show</p>
      )}
    </>
  );
};

export default Following;
