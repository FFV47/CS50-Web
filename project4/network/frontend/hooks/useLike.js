import { useMutation, useQueryClient } from "react-query";
import axiosAPI from "../axiosAPI";

const useLike = (queryKey) => {
  const queryClient = useQueryClient();

  const likePost = async ({ postID }) => {
    const api = new axiosAPI();

    const response = await api.patch(`/api/like_post/${postID}`);
    if (response.data) {
      return response.data;
    }

    throw new Error(response.errorMessage);
  };

  const mutation = useMutation(likePost, {
    /**
     * "data" is the response data from the API. The second argument
     * is the object that the "mutate" function receives
     */
    onSuccess: (data, { postID }) => {
      queryClient.setQueryData(queryKey, (oldData) => {
        const newData = { ...oldData };
        const post = newData.posts.find((post) => post.id === postID);
        post.likes = data.likes;
        post.likedByUser = data.likedByUser;
        return newData;
      });
    },
  });

  return mutation;
};

export default useLike;
