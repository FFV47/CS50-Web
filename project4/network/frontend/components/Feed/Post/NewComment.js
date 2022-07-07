import PropTypes from "prop-types";
import { useId, useState } from "react";

import useControlledTextarea from "../../../hooks/useControlledTextarea";

import useDataContext from "../../../context/DataContext";
import useNewComment from "../../../hooks/useNewComment";

const NewComment = ({ setShowCommentForm, setShowComments, postID }) => {
  const [text, setText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { queryKey } = useDataContext();

  const formEl = useControlledTextarea(text);
  const id = useId();

  const newCommentMutation = useNewComment(queryKey);

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
        rows="1"
        className="form-control mt-3 fixed-textarea"
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
