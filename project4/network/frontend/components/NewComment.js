import PropTypes from "prop-types";
import React, { useEffect, useId, useRef, useState } from "react";

import useGlobalContext from "../context/GlobalContext";
import useNewComment from "../hooks/useNewComment";

const NewComment = ({ setShowCommentForm, setShowComments, postID }) => {
  const [text, setText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { postsQueryKey } = useGlobalContext();

  const formEl = useRef(null);
  const id = useId();

  useEffect(() => {
    formEl.current.focus();
  }, []);

  useEffect(() => {
    formEl.current.style.height = "inherit";
    formEl.current.style.height = `${formEl.current.scrollHeight}px`;
  });

  const newCommentMutation = useNewComment(postsQueryKey);

  return (
    <form
      className="form-floating"
      onSubmit={(e) => {
        e.preventDefault();
        setSubmitting(true);
        newCommentMutation.mutate(
          { text, postID },
          {
            onSuccess: () => {
              setSubmitting(false);
              setShowCommentForm(false);
              setShowComments(true);
            },
          }
        );
      }}
    >
      <textarea
        ref={formEl}
        name="comment-text"
        id={id}
        cols="30"
        rows="1"
        className="form-control mt-3 post-textarea"
        placeholder="Write a comment..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      ></textarea>
      <label htmlFor={id} className="form-label">
        Comment
      </label>
      <button type="submit" className="btn btn-primary btn-sm mt-3">
        {!submitting ? "Comment" : "Submitting..."}
      </button>
    </form>
  );
};

NewComment.propTypes = {
  setShowCommentForm: PropTypes.func,
  setShowComments: PropTypes.func,
  postID: PropTypes.number,
};

export default NewComment;
