import { format, parseISO } from "date-fns";
import PropTypes from "prop-types";
import { CSSTransition } from "react-transition-group";

import useDataContext from "../../../context/DataContext";
import useToggle from "../../../hooks/useToggle";
import NewReply from "./NewReply";

const Comment = ({ comment, postID }) => {
  const [replyForm, setReplyForm] = useToggle();
  const { authenticated } = useDataContext();

  return (
    <li className="comment card">
      <div className="card-body">
        <div className="card-title comment-title">
          <p>
            <strong>{comment.username}</strong> wrote on{" "}
            {format(parseISO(comment.publicationDate), "MMMM d, yyyy - HH:mm")}
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
          classNames="default-transition-group"
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
