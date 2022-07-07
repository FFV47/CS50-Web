import * as bootstrap from "bootstrap";
import useDataContext from "../context/DataContext";

const useToast = () => {
  const { setToastText } = useDataContext();

  const showToast = (toastID, message) => {
    document.querySelectorAll(".toast").forEach((toastEl) => {
      new bootstrap.Toast(toastEl);
    });

    const toastEl = document.getElementById(toastID);
    // Returns a Bootstrap toast instance
    const toast = bootstrap.Toast.getInstance(toastEl);
    setToastText(message);

    toast.show();
  };

  return showToast;
};

export default useToast;
