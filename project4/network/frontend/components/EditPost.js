import React, { useState } from "react";
import PropTypes from "prop-types";
import useEditPost from "../hooks/useEditPost";

const EditPost = ({ post, postsQueryKey, setIsEditingPost }) => {
  const [postText, setPostText] = useState(post.text);
  const [updating, setUpdating] = useState(false);

  const editPostMutation = useEditPost(postsQueryKey, setUpdating);

  return (
    <form
      className="form-floating mt-2 mb-2"
      onSubmit={async (e) => {
        e.preventDefault();
        setUpdating(true);
        await editPostMutation.mutateAsync({ postID: post.id, text: postText });
        setIsEditingPost(false);
      }}
    >
      <textarea
        name="text"
        id="post-text"
        cols="30"
        rows="3"
        className="form-control mt-4"
        placeholder="What's on your mind?"
        value={postText}
        onChange={(e) => setPostText(e.target.value)}
      ></textarea>
      <label htmlFor="post-text">Edit Post</label>
      <button type="submit" className="btn btn-primary btn-sm mt-3">
        {!updating ? "Update Post" : "Updating..."}
      </button>
    </form>
  );
};
EditPost.propTypes = {
  post: PropTypes.shape({
    id: PropTypes.number,
    text: PropTypes.string,
  }),
  postsQueryKey: PropTypes.array,
  setIsEditingPost: PropTypes.func,
};
export default EditPost;
