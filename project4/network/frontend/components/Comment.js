import format from "date-fns/format";
import PropTypes from "prop-types";
import React from "react";
import { CSSTransition } from "react-transition-group";

import useGlobalContext from "../context/GlobalContext";
import useToggle from "../hooks/useToggle";
import getDate from "../utils/getDate";
import NewReply from "./NewReply";

const Comment = ({ comment, postID }) => {
  const [replyForm, setReplyForm] = useToggle();
  const { authenticated } = useGlobalContext();

  return (
    <li className="comment card">
      <div className="card-body">
        <div className="card-title comment-title">
          <p>
            <strong>{comment.username}</strong> wrote on{" "}
            {format(getDate(comment.publicationDate), "MMMM d, yyyy - HH:mm")}
          </p>

          {authenticated && (
            <button
              type="button"
              className="btn btn-outline-secondary btn-sm reply-btn"
              onClick={setReplyForm}
            >
              {replyForm ? "Cancel" : "Reply"}
            </button>
          )}
        </div>

        <p className="card-text" style={{ "whiteSpace": "pre-wrap" }}>
          {comment.text}
        </p>

        {/* Reply Form */}

        <CSSTransition
          in={replyForm}
          timeout={400}
          unmountOnExit
          classNames={"comment-form"}
        >
          <NewReply setReplyForm={setReplyForm} postID={postID} commentID={comment.id} />
        </CSSTransition>

        {/* Replies section */}
        <ul className="replies mt-3">
          {comment.replies.map((reply) => {
            return <Comment key={reply.id} comment={reply} postID={postID} />;
          })}
        </ul>
      </div>
    </li>
  );
};

Comment.propTypes = {
  comment: PropTypes.shape({
    id: PropTypes.number,
    text: PropTypes.string,
    username: PropTypes.string,
    publicationDate: PropTypes.string,
    replies: PropTypes.arrayOf(PropTypes.object),
  }),
  postsQueryKey: PropTypes.array,
  postID: PropTypes.number,
};

export default Comment;
