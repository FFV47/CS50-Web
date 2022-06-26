import PropTypes from "prop-types";
import React, { useState } from "react";
import { AiFillHeart } from "react-icons/ai";
import { Link } from "react-router-dom";

import { CSSTransition } from "react-transition-group";

import useBootstrapToast from "../hooks/useBootstrapToast";
import useFollow from "../hooks/useFollow";
import useLike from "../hooks/useLike";
import useToggle from "../hooks/useToggle";

import useGlobalContext from "../context/GlobalContext";
import Comment from "./Comment";
import EditPost from "./EditPost";
import NewComment from "./NewComment";

import format from "date-fns/format";
import getDate from "../utils/getDate";
// import { formatRelative, parseISO } from "date-fns";
// import { formatDistanceToNow } from "date-fns";

const Post = ({ post }) => {
  const { username } = JSON.parse(document.getElementById("userInfo").textContent);
  const { postsQueryKey, authenticated } = useGlobalContext();

  const [isEditingPost, setIsEditingPost] = useToggle();
  const [showText, setShowText] = useState(true);
  const [showComments, setShowComments] = useToggle();
  const [showCommentForm, setShowCommentForm] = useToggle();

  const likeMutation = useLike(postsQueryKey);
  const followMutation = useFollow(postsQueryKey);

  const showToast = useBootstrapToast();

  // const showToast = useToast();

  return (
    <li>
      <article className="card mb-3">
        <div className="card-body">
          <div className="post-title mb-2">
            <Link
              to={`/profile/${post.username}`}
              className="card-title link-dark post-owner"
            >
              {post.username}
            </Link>
            {authenticated && !post.isOwner && (
              <button
                type="button"
                className={`btn btn-sm ${
                  post.isFollowing ? "btn-primary" : "btn-outline-primary"
                }`}
                onClick={() =>
                  followMutation.mutate(
                    {
                      username: post.username,
                      postID: post.id,
                    },
                    {
                      onSuccess: (data) => {
                        showToast("followToast", data.message);
                      },
                    }
                  )
                }
              >
                {post.isFollowing ? "Unfollow" : "Follow"}
              </button>
            )}
          </div>

          {/* Edit Post */}
          {username === post.username && (
            <button
              type="button"
              className="btn btn-primary btn-sm edit-btn"
              onClick={setIsEditingPost}
            >
              {isEditingPost ? "Cancel Edit" : "Edit"}
            </button>
          )}

          {showText && (
            // renders "\n" and "\t" in HTML (same as textarea)
            <p className="mt-2" style={{ "whiteSpace": "pre-wrap" }}>
              {post.text}
            </p>
          )}

          <CSSTransition
            in={isEditingPost}
            timeout={400}
            unmountOnExit
            classNames="edit-post"
            onEnter={() => setShowText(false)}
            onExited={() => setShowText(true)}
          >
            <EditPost post={post} setIsEditingPost={setIsEditingPost} />
          </CSSTransition>

          {/* Dates */}
          <p className="text-muted mb-0">
            Posted on {format(getDate(post.publicationDate), "MMMM d, yyyy - HH:mm")}
            {post.edited
              ? `, edited on ${format(
                  getDate(post.lastModified),
                  "MMMM d, yyyy - HH:mm"
                )}`
              : ""}
          </p>

          {/* <p className="text-muted mb-0">
          Posted {formatRelative(getDate(post.publicationDate), new Date())}
          {post.edited
            ? `, edited ${formatRelative(getDate(post.lastModified), new Date())}`
            : ""}
        </p>
        <p className="text-muted mb-0">
          Posted {formatDistanceToNow(parseISO(post.publicationDate))} ago
          {post.edited
            ? `, edited ${formatDistanceToNow(parseISO(post.lastModified))} ago`
            : ""}
        </p> */}

          {/* Like Button */}
          <form
            className="like-form"
            onSubmit={(e) => {
              e.preventDefault();
              likeMutation.mutate(post.id);
            }}
          >
            <button className="like-btn" type="submit">
              <AiFillHeart className={post.likedByUser ? "liked" : null} />
            </button>
            <span>{post.likes}</span>
          </form>

          {/* New Comment */}
          {authenticated && (
            <button
              type="button"
              className="btn btn-outline-primary btn-sm"
              onClick={setShowCommentForm}
            >
              {showCommentForm ? "Cancel" : "Comment"}
            </button>
          )}

          <CSSTransition
            in={showCommentForm}
            timeout={400}
            unmountOnExit
            classNames={"comment-form"}
          >
            <NewComment
              setShowCommentForm={setShowCommentForm}
              setShowComments={setShowComments}
              postID={post.id}
            />
          </CSSTransition>

          {/* Comment Section */}
          {/* <br /> */}
          <hr className="mb-0" />
          <button
            type="button"
            className="btn show-comments-btn mt-1"
            onClick={setShowComments}
          >
            {showComments ? "hide comments" : "show comments"}
          </button>

          <CSSTransition
            in={showComments}
            timeout={400}
            unmountOnExit
            classNames="show-comments"
          >
            {post.comments.length > 0 ? (
              <ul className="comment-section mt-3">
                {post.comments.map((comment) => {
                  return <Comment key={comment.id} comment={comment} postID={post.id} />;
                })}
              </ul>
            ) : (
              <p className="text-muted">No comments yet</p>
            )}
          </CSSTransition>
        </div>
      </article>
    </li>
  );
};

Post.propTypes = {
  post: PropTypes.shape({
    id: PropTypes.number,
    text: PropTypes.string,
    edited: PropTypes.bool,
    username: PropTypes.string,
    isFollowing: PropTypes.bool,
    isOwner: PropTypes.bool,
    likes: PropTypes.number,
    likedByUser: PropTypes.bool,
    publicationDate: PropTypes.string,
    lastModified: PropTypes.string,
    comments: PropTypes.arrayOf(Comment.propTypes.comment),
  }),
};

export default Post;
