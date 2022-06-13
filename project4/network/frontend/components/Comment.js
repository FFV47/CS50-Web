import PropTypes from "prop-types";
import React from "react";

const Comment = ({ comment }) => {
  return (
    <li className="comment card">
      <div className="card-body">
        <p className="card-title">
          <strong>{comment.username}</strong> wrote on {comment.publicationDate}
        </p>
        <p className="card-text">{comment.text}</p>
        <ul className="replies">
          {comment.replies.map((reply) => {
            return <Comment key={reply.id} comment={reply} />;
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
};

export default Comment;
