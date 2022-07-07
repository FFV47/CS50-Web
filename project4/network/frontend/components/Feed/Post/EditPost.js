import PropTypes from "prop-types";
import { useId, useState } from "react";

import useControlledTextarea from "../../../hooks/useControlledTextarea";

import useDataContext from "../../../context/DataContext";
import useEditPost from "../../../hooks/useEditPost";

const EditPost = ({ post, setIsEditingPost }) => {
  const [text, setText] = useState(post.text);
  const [updating, setUpdating] = useState(false);
  const { queryKey } = useDataContext();

  const editPostMutation = useEditPost(queryKey, setUpdating);

  const formEl = useControlledTextarea(text);
  const id = useId();

  const handleEdit = (e) => {
    e.preventDefault();
    setUpdating(true);
    if (text.trim().length > 0) {
      editPostMutation.mutate(
        { postID: post.id, text: text },
        {
          onSuccess: () => {
            setUpdating(false);
            setIsEditingPost(false);
          },
        }
      );
    }
  };

  return (
    <form className="form-floating mt-2 mb-2" onSubmit={handleEdit}>
      <textarea
        ref={formEl}
        name="edit-text"
        id={id}
        rows="1"
        className="form-control mt-4 fixed-textarea"
        placeholder="What's on your mind?"
        value={text}
        onChange={(e) => setText(e.target.value)}
      ></textarea>
      <label htmlFor={id}>Edit Post</label>
      <button type="submit" className="btn btn-primary btn-sm mt-3">
        {!updating ? "Update Post" : "Updating..."}
      </button>
    </form>
  );
};
EditPost.propTypes = {
  post: PropTypes.shape({
    id: PropTypes.number,
    text: PropTypes.string,
  }),
  setIsEditingPost: PropTypes.func,
};
export default EditPost;
