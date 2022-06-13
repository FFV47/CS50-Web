import PropTypes from "prop-types";
import React, { useState } from "react";
import { AiFillHeart, AiOutlineHeart } from "react-icons/ai";

import { CSSTransition } from "react-transition-group";

import useLike from "../hooks/useLike";
import Comment from "./Comment";
import EditPost from "./EditPost";

const Post = ({ post, postsQueryKey }) => {
  const { username } = JSON.parse(document.getElementById("userInfo").textContent);

  const [isEditingPost, setIsEditingPost] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const likeMutation = useLike(postsQueryKey);

  return (
    <article className="card mb-3">
      <div className="card-body">
        <h5 className="card-title">{post.username}</h5>

        {/* Edit Post */}
        {username === post.username && (
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => setIsEditingPost((state) => !state)}
          >
            {isEditingPost ? "Cancel Edit" : "Edit"}
          </button>
        )}

        {!isEditingPost && <p className="mt-2">{post.text}</p>}

        <CSSTransition
          in={isEditingPost}
          timeout={1000}
          unmountOnExit
          classNames="edit-post"
        >
          <EditPost
            post={post}
            postsQueryKey={postsQueryKey}
            setIsEditingPost={setIsEditingPost}
          />
        </CSSTransition>

        <p className="text-muted">
          Posted on {post.publicationDate}
          {post.edited ? `, edited on ${post.lastModified}` : ""}
        </p>

        {/* Like Button */}
        <form
          className="like-form"
          onSubmit={(e) => {
            e.preventDefault();
            likeMutation.mutate({ postID: post.id });
          }}
        >
          <button className="like-btn" type="submit">
            {post.likedByUser ? <AiFillHeart /> : <AiOutlineHeart />}
          </button>
          <span>{post.likes}</span>
        </form>

        <button type="button" className="btn btn-outline-primary btn-sm">
          Comment
        </button>

        {/* Comment Section */}
        <br />
        <button
          type="button"
          className="btn show-comments-btn mt-3"
          onClick={() => setShowComments((state) => !state)}
        >
          {showComments ? "hide comments" : "show comments"}
        </button>

        {showComments && (
          <ul className="comment-section mt-3">
            {post.comments.map((comment) => {
              return <Comment key={comment.id} comment={comment} />;
            })}
          </ul>
        )}
      </div>
    </article>
  );
};

Post.propTypes = {
  post: PropTypes.shape({
    id: PropTypes.number,
    text: PropTypes.string,
    edited: PropTypes.bool,
    username: PropTypes.string,
    likes: PropTypes.number,
    likedByUser: PropTypes.bool,
    publicationDate: PropTypes.string,
    lastModified: PropTypes.string,
    comments: PropTypes.arrayOf(Comment.propTypes.comment),
  }),
  postsQueryKey: PropTypes.array,
};

export default Post;
