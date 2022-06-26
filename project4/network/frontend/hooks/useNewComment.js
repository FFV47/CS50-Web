import { useMutation, useQueryClient } from "react-query";
import axiosAPI from "../utils/axiosAPI";

const useNewComment = (queryKey) => {
  const queryClient = useQueryClient();

  const newPost = async ({ text, postID, commentID }) => {
    const api = new axiosAPI();

    const response = await api.post("/api/new_comment", { text, postID, commentID });
    if (response.data) {
      return response.data;
    }

    throw new Error(response.errorMessage);
  };

  const mutation = useMutation(newPost, {
    onSuccess: async (data, { postID }) => {
      queryClient.setQueryData(queryKey, (oldData) => {
        const newData = { ...oldData };
        const index = newData.posts.findIndex((post) => post.id === postID);
        newData.posts[index] = data;
        return newData;
      });
    },
  });

  return mutation;
};

export default useNewComment;
