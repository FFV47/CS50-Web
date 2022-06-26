import * as bootstrap from "bootstrap"; /* eslint-disable-line no-unused-vars */
import useGlobalContext from "../context/GlobalContext";

const useBootstrapToast = () => {
  const { setToastText } = useGlobalContext();

  const showToast = (toastID, message) => {
    document.querySelectorAll(".toast").forEach((toastEl) => {
      new bootstrap.Toast(toastEl);
    });

    const toastEl = document.getElementById(toastID);
    const toast = bootstrap.Toast.getInstance(toastEl); // Returns a Bootstrap toast instance
    setToastText(message);
    toast.show();
  };

  return showToast;
};

export default useBootstrapToast;
