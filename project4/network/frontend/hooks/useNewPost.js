import { useMutation, useQueryClient } from "react-query";
import axiosAPI from "../utils/axiosAPI";

const useNewPost = (queryKey) => {
  const queryClient = useQueryClient();

  const newPost = async (text) => {
    const api = new axiosAPI();

    const response = await api.post("/api/new_post", { text });
    if (response.data) {
      return response.data;
    }

    throw new Error(response.errorMessage);
  };

  const mutation = useMutation(newPost, {
    // 🚀 fire and forget - will not wait
    // onSuccess: () => {
    //   queryClient.invalidateQueries(queryKey, { exact: true });
    // },
    // 🎉 will wait for query invalidation to finish
    onSuccess: () => {
      return queryClient.invalidateQueries(queryKey, { exact: true });
    },
  });

  return mutation;
};

export default useNewPost;
