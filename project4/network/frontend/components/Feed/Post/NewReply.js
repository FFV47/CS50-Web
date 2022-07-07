import PropTypes from "prop-types";
import { useId, useState } from "react";

import useControlledTextarea from "../../../hooks/useControlledTextarea";

import useDataContext from "../../../context/DataContext";
import useNewComment from "../../../hooks/useNewComment";

const NewReply = ({ setReplyForm, postID, commentID }) => {
  const { queryKey } = useDataContext();

  const [text, setText] = useState("");
  const [replying, setReplying] = useState(false);

  const newCommentMutation = useNewComment(queryKey);

  const formEl = useControlledTextarea(text);
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

  return (
    <form className="form-floating" onSubmit={handleSubmit}>
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
