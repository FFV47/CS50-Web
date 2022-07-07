import { useQuery } from "react-query";
import axiosAPI from "../utils/axiosAPI";

const usePaginatedPosts = (queryKey, url) => {
  const api = new axiosAPI();

  const fetchPosts = async (page) => {
    const response = await api.get(`/api/${url}/${page}`);
    if (response && response.data) {
      return response.data;
    }

    throw new Error(response.errorMessage);
  };

  return useQuery(queryKey, () => fetchPosts(queryKey[1]), {
    keepPreviousData: true,
  });
};

export default usePaginatedPosts;
