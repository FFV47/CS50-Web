import React, { useState } from "react";
import useNewPost from "../hooks/useNewPost";
import PropTypes from "prop-types";

const NewPost = ({ postsQueryKey }) => {
  const [text, setText] = useState("");
  const newPostMutation = useNewPost(postsQueryKey);

  return (
    <form
      className="card mx-3 mt-3"
      onSubmit={(e) => {
        e.preventDefault();
        newPostMutation.mutate({ text });
      }}
    >
      <div className="card-body">
        <form>
          <h3>
            <label htmlFor="newPost">New Post</label>
          </h3>
          <textarea
            name="newPost"
            id="newPost"
            className="form-control"
            cols="20"
            rows="5"
            value={text}
            onChange={(e) => setText(e.target.value)}
          ></textarea>
          <button className="btn btn-primary mt-2" type="submit">
            Post
          </button>
        </form>
      </div>
    </form>
  );
};

NewPost.propTypes = {
  postsQueryKey: PropTypes.string.isRequired,
};

export default NewPost;
