/* eslint-disable react/prop-types */
import React, { createContext, useContext, useState } from "react";
import { useParams } from "react-router-dom";
import ToastMessage from "../components/ToastMessage";
const GlobalContext = createContext();

export const GlobalProvider = ({ children }) => {
  const params = useParams();
  const urlPage = params.urlPage ? parseInt(params.urlPage, 10) : 1;

  const [toastText, setToastText] = useState("");

  const authenticated = JSON.parse(
    document.getElementById("userInfo").textContent
  ).logged_in;

  const postsQueryKey = ["posts", urlPage];

  return (
    <GlobalContext.Provider
      value={{ urlPage, postsQueryKey, authenticated, setToastText }}
    >
      <ToastMessage message={toastText} />
      {children}
    </GlobalContext.Provider>
  );
};

const useGlobalContext = () => useContext(GlobalContext);

export default useGlobalContext;
