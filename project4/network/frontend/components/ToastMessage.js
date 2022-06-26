import React from "react";
import PropTypes from "prop-types";

const ToastMessage = ({ message }) => {
  const name = message.split(" ").slice(-1)[0];
  const startMsg = message.split(" ").slice(0, -1).join(" ");
  return (
    <aside
      aria-hidden="true"
      className="position-fixed top-0 start-50 translate-middle-x p-4"
      style={{ zIndex: 11 }}
    >
      <div
        id="followToast"
        className="toast text-white bg-primary"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <div className="toast-visible">
          <p className="toast-body">
            {startMsg} <strong>{name}</strong>{" "}
          </p>
          <button
            type="button"
            className="btn-close me-2 m-auto"
            data-bs-dismiss="toast"
            aria-label="Close"
          ></button>
        </div>
      </div>
    </aside>
  );
};

ToastMessage.propTypes = {
  message: PropTypes.string,
};

export default ToastMessage;
