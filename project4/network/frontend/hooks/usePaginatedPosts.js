import { useQuery } from "react-query";
import axiosAPI from "../axiosAPI";

const usePaginatedPosts = (queryKey) => {
  const api = new axiosAPI();

  const fetchPosts = async (page) => {
    const response = await api.get(`/api/all_posts/${page}`);
    if (response && response.data) {
      return response.data;
    }

    throw new Error(response.errorMessage);
  };

  return useQuery(queryKey, () => fetchPosts(queryKey[1]), { keepPreviousData: true });
};

export default usePaginatedPosts;
