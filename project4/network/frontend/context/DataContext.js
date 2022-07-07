/* eslint-disable react/prop-types */
import { createContext, useContext, useState } from "react";
import { useParams, Outlet } from "react-router-dom";

import ToastMessage from "../components/ToastMessage";

const DataContext = createContext();

export const DataProvider = () => {
  const userInfo = JSON.parse(document.getElementById("userInfo").textContent);
  const authenticated = userInfo.auth;

  const path = window.location.pathname;

  const params = useParams();
  const urlPage = params.urlPage ? parseInt(params.urlPage, 10) : 1;
  const urlUsername = params.username;
  const loggedUser = userInfo.username;

  const [toastText, setToastText] = useState("");

  let queryKey;
  if (/profile/.test(path)) {
    queryKey = ["profile", urlUsername, urlPage];
  } else if (/following/.test(path)) {
    queryKey = ["following", urlPage];
  } else {
    queryKey = ["posts", urlPage];
  }

  return (
    <DataContext.Provider
      value={{ urlPage, queryKey, loggedUser, authenticated, setToastText }}
    >
      <ToastMessage toastText={toastText} />
      <Outlet />
    </DataContext.Provider>
  );
};

const useDataContext = () => useContext(DataContext);

export default useDataContext;
