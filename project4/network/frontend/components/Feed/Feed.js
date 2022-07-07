import PropTypes from "prop-types";

import { ImSpinner5 } from "react-icons/im";

import PageControl from "./PageControl";
import Post from "./Post/Post";

const Feed = ({
  isLoading,
  isFetching,
  isError,
  data,
  error,
  isPreviousData,
  hasParentSpin,
}) => {
  return (
    <>
      <PageControl isPreviousData={isPreviousData} data={data} />

      <section id="posts-section">
        {(!hasParentSpin && !isLoading && !isError && isFetching) || isLoading ? (
          <div className="center mb-3">
            <ImSpinner5 aria-hidden="true" className="loading-spinner" />
          </div>
        ) : (
          ""
        )}

        {!isLoading && isError && (
          <p className="alert alert-danger" role="alert">
            {error.message}
          </p>
        )}

        {!isLoading && !isError && (
          <ul className="list-unstyled">
            {data.posts.map((post) => (
              <Post key={post.id} post={post} />
            ))}
          </ul>
        )}
      </section>
    </>
  );
};

Feed.propTypes = {
  isLoading: PropTypes.bool,
  isFetching: PropTypes.bool,
  isError: PropTypes.bool,
  data: PropTypes.object,
  error: PropTypes.object,
  isPreviousData: PropTypes.bool,
  hasParentSpin: PropTypes.bool,
};

export default Feed;
