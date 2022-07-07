import { useMutation, useQueryClient } from "react-query";
import axiosAPI from "../utils/axiosAPI";

const useFollow = (queryKey) => {
  const queryClient = useQueryClient();

  const followUser = async ({ username }) => {
    const api = new axiosAPI();

    const response = await api.post(`/api/follow/${username}`);
    if (response.data) {
      return response.data;
    }

    throw new Error(response.errorMessage);
  };

  const mutation = useMutation(followUser, {
    onSuccess: (data, { postID }) => {
      if (postID) {
        queryClient.setQueryData(queryKey, (oldData) => {
          const newData = { ...oldData };
          const post = newData.posts.find((post) => post.id === postID);
          post.isFollowing = data.isFollowing;
          return newData;
        });
      } else {
        queryClient.setQueryData(queryKey, (oldData) => {
          return { ...oldData, isFollowing: data.isFollowing };
        });
      }
    },
  });

  return mutation;
};

export default useFollow;
