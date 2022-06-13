import { useMutation, useQueryClient } from "react-query";
import axiosAPI from "../axiosAPI";

const useNewPost = (queryKey) => {
  const queryClient = useQueryClient();

  const newPost = async ({ text }) => {
    const api = new axiosAPI();

    const response = await api.post("/api/new_post", { text });
    if (response.data) {
      return response.data;
    }

    throw new Error(response.errorMessage);
  };

  const mutation = useMutation(newPost, {
    onSuccess: (data) => {
      queryClient.setQueryData(queryKey, (oldData) => {
        const newData = { ...oldData };
        newData.posts.push(data);
        return newData;
      });
    },
  });

  return mutation;
};

export default useNewPost;
