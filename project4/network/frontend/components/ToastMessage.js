import PropTypes from "prop-types";

const ToastMessage = ({ toastText }) => {
  const name = toastText.split(" ").slice(-1)[0];
  const startMsg = toastText.split(" ").slice(0, -1).join(" ");

  const position = /profile/.test(window.location.pathname)
    ? "position-relative mt-3"
    : "position-fixed";

  return (
    <div
      id="followToast"
      className={`toast bg-primary text-white ${position} top-1 start-50 translate-middle-x`}
      style={{ zIndex: 1 }}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div className="d-flex align-items-center">
        <div className="toast-body">
          {startMsg} <strong>{name}</strong>
        </div>
        <button
          type="button"
          className="btn-close btn-close-white me-3 m-auto"
          data-bs-dismiss="toast"
          aria-label="Close"
        ></button>
      </div>
    </div>
  );
};

ToastMessage.propTypes = {
  toastText: PropTypes.string,
};

export default ToastMessage;
