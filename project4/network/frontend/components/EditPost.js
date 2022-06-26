import PropTypes from "prop-types";
import React, { useEffect, useId, useRef, useState } from "react";
import useGlobalContext from "../context/GlobalContext";
import useEditPost from "../hooks/useEditPost";

const EditPost = ({ post, setIsEditingPost }) => {
  const [text, setText] = useState(post.text);
  const [updating, setUpdating] = useState(false);
  const { postsQueryKey } = useGlobalContext();

  const editPostMutation = useEditPost(postsQueryKey, setUpdating);

  const formEl = useRef(null);
  const id = useId();

  const handleEdit = (e) => {
    e.preventDefault();
    setUpdating(true);
    if (text.trim().length > 0) {
      editPostMutation.mutate(
        { postID: post.id, text: text },
        {
          onSuccess: () => {
            setUpdating(false);
            setIsEditingPost(false);
          },
        }
      );
    }
  };

  useEffect(() => {
    formEl.current.selectionStart = formEl.current.selectionEnd = text.length;
    formEl.current.focus();
  }, []);

  useEffect(() => {
    formEl.current.style.height = "inherit";
    formEl.current.style.height = `${formEl.current.scrollHeight}px`;
  });

  return (
    <form className="form-floating mt-2 mb-2" onSubmit={handleEdit}>
      <textarea
        ref={formEl}
        name="edit-text"
        id={id}
        cols="30"
        rows="1"
        className="form-control mt-4 post-textarea"
        placeholder="What's on your mind?"
        value={text}
        onChange={(e) => setText(e.target.value)}
      ></textarea>
      <label htmlFor={id}>Edit Post</label>
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
  setIsEditingPost: PropTypes.func,
};
export default EditPost;
