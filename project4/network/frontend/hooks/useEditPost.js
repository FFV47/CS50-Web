import { useMutation, useQueryClient } from "react-query";
import axiosAPI from "../utils/axiosAPI";

const useEditPost = (queryKey, setUpdating) => {
  const queryClient = useQueryClient();

  const editPost = async ({ postID, text }) => {
    const api = new axiosAPI();

    const response = await api.post("/api/edit_post", { postID, text });
    if (response.data) {
      return response.data;
    }

    throw new Error(response.errorMessage);
  };

  const mutation = useMutation(editPost, {
    onSuccess: (data) => {
      queryClient.setQueryData(queryKey, (oldData) => {
        const newData = { ...oldData };
        const post = newData.posts.find((post) => post.id === data.id);
        post.text = data.text;
        post.edited = data.edited;
        post.lastModified = data.lastModified;
        return newData;
      });

      setUpdating(false);
    },
  });

  return mutation;
};

export default useEditPost;
