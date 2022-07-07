import { useQuery } from "react-query";
import axiosAPI from "../utils/axiosAPI";

const useProfile = (queryKey) => {
  const api = new axiosAPI();

  const fetchProfile = async (username, page) => {
    const response = await api.get(`/api/profile/${username}/${page}`);
    if (response && response.data) {
      return response.data;
    }

    throw new Error(response.errorMessage);
  };

  return useQuery(queryKey, () => fetchProfile(queryKey[1], queryKey[2]), {
    keepPreviousData: true,
  });
};

export default useProfile;
