import PropTypes from "prop-types";
import { useState } from "react";
import { AiFillHeart } from "react-icons/ai";
import { Link } from "react-router-dom";

import { CSSTransition } from "react-transition-group";

import useFollow from "../../../hooks/useFollow";
import useLike from "../../../hooks/useLike";
import useToggle from "../../../hooks/useToggle";
import useToast from "../../../hooks/useToast";

import useDataContext from "../../../context/DataContext";
import Comment from "./Comment";
import EditPost from "./EditPost";
import NewComment from "./NewComment";

import { format, parseISO } from "date-fns";

const Post = ({ post }) => {
  const { username } = JSON.parse(document.getElementById("userInfo").textContent);
  const { queryKey, authenticated } = useDataContext();

  const [isEditingPost, setIsEditingPost] = useToggle();
  const [showText, setShowText] = useState(true);
  const [showComments, setShowComments] = useToggle();
  const [showCommentForm, setShowCommentForm] = useToggle();

  const likeMutation = useLike(queryKey);
  const followMutation = useFollow(queryKey);

  const showToast = useToast();

  const inProfilePage = /profile/.test(window.location.pathname);

  // Django template links
  const updateNavLinks = (e) => {
    const navBar = document.querySelector(".navbar-nav");
    const navLinks = [...navBar.children];

    navLinks.forEach((item) => {
      item.classList.remove("active");
      if (item.pathname === e.target.pathname) {
        item.classList.add("active");
      }
    });
  };

  return (
    <li>
      <article className="card round-card shadow mb-3">
        <div className="card-body">
          <div className="post-title mb-2">
            {/* Profile Link */}
            <Link
              to={`/profile/${post.username}`}
              onClick={updateNavLinks}
              className="card-title link-dark post-owner"
            >
              {post.username}
            </Link>

            {/* Follow Button */}
            {authenticated && !post.isOwner && !inProfilePage && (
              <button
                type="button"
                className={`btn btn-sm rounded-pill ${
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
            classNames="default-transition-group"
            onEnter={() => setShowText(false)}
            onExited={() => setShowText(true)}
          >
            <EditPost post={post} setIsEditingPost={setIsEditingPost} />
          </CSSTransition>

          {/* Dates */}
          <p className="text-muted mb-0">
            Posted on {format(parseISO(post.publicationDate), "MMMM d, yyyy - HH:mm")}
            {post.edited
              ? `, edited on ${format(
                parseISO(post.lastModified),
                "MMMM d, yyyy - HH:mm"
              )}`
              : ""}
          </p>

          {/* <p className="text-muted mb-0">
          Posted {formatRelative(parseISO(post.publicationDate), new Date())}
          {post.edited
            ? `, edited ${formatRelative(parseISO(post.lastModified), new Date())}`
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
            classNames="default-transition-group"
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
            classNames="default-transition-group"
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
