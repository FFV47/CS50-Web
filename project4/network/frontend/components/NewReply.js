import PropTypes from "prop-types";
import React, { useEffect, useId, useRef, useState } from "react";

import useGlobalContext from "../context/GlobalContext";
import useNewComment from "../hooks/useNewComment";

const NewReply = ({ setReplyForm, postID, commentID }) => {
  const [text, setText] = useState("");
  const [replying, setReplying] = useState(false);
  const { postsQueryKey } = useGlobalContext();

  const formEl = useRef(null);
  const id = useId();

  const handleSubmit = (e) => {
    e.preventDefault();
    setReplying(true);

    if (text.trim().length > 0) {
      newCommentMutation.mutate(
        { text, postID, commentID },
        {
          onSuccess: () => {
            setReplying(false);
            setReplyForm(false);
          },
        }
      );
    }
  };

  useEffect(() => {
    formEl.current.focus();
  }, []);

  useEffect(() => {
    formEl.current.style.height = "inherit";
    formEl.current.style.height = `${formEl.current.scrollHeight}px`;
  });

  const newCommentMutation = useNewComment(postsQueryKey);

  return (
    <form className="form-floating" onSubmit={handleSubmit}>
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
      <button type="submit" className="btn btn-outline-primary btn-sm mt-3">
        {!replying ? "Reply" : "Replying..."}
      </button>
    </form>
  );
};

NewReply.propTypes = {
  setReplyForm: PropTypes.func,
  postID: PropTypes.number,
  commentID: PropTypes.number,
};

export default NewReply;
