import { useState, useRef } from "react";
import PropTypes from "prop-types";
import useControlledTextarea from "../../hooks/useControlledTextarea";

import useUpdateProfile from "../../hooks/useUpdateProfile";

const UpdateProfile = ({ queryKey, setIsUpdating, profileData }) => {
  const [about, setAbout] = useState(profileData.about);
  const [sending, setSending] = useState(false);
  const [data, setData] = useState(null);

  const formEl = useRef(null);

  const { mutate } = useUpdateProfile(queryKey, setIsUpdating);

  const textArea = useControlledTextarea(about);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSending(true);
    const data = new FormData(formEl.current);

    mutate(data, {
      onSuccess: (data) => {
        setData(data);
        setSending(false);
        console.log(data.errors);
        if (!data.errors) {
          setIsUpdating(false);
        }
      },
      onError: () => {
        setSending(false);
      },
    });
  };

  return (
    <form ref={formEl} onSubmit={handleSubmit}>
      <div className="row align-items-center mb-3">
        <div className="col-sm-auto">
          <div className="input-group">
            <label htmlFor="form-photo" className="input-group-text">
              Profile Photo
            </label>
            <input
              type="file"
              id="form-photo"
              name="photo"
              className={`form-control ${
                data?.errors?.photo ? "is-invalid" : "is-valid"
              }`}
            />
            <div id="validationPhotoFeedback" className="invalid-feedback">
              {data?.errors?.photo}
            </div>
            <div className="valid-feedback"></div>
          </div>
        </div>
      </div>

      <div className="form-floating mb-3">
        <input
          type="text"
          name="username"
          id="form-username"
          maxLength={20}
          className={`form-control ${data?.errors?.username ? "is-invalid" : "is-valid"}`}
          defaultValue={profileData.username}
          required
          aria-describedby="validationUsernameFeedback"
        />
        <label htmlFor="form-username" className="form-label mb-0 col-sm-2">
          Username:
        </label>
        <div id="validationUsernameFeedback" className="invalid-feedback">
          {data?.errors?.username}
        </div>
        <div className="valid-feedback"></div>
      </div>

      <div className="form-floating mb-3">
        <textarea
          ref={textArea}
          id="profile-about"
          name="about"
          rows="1"
          className="form-control fixed-textarea"
          placeholder="Tell about yourself..."
          value={about}
          onChange={(e) => setAbout(e.target.value)}
          maxLength={200}
        ></textarea>
        <label htmlFor="profile-about">About me</label>
      </div>

      <div className="form-floating mb-3">
        <input
          type="email"
          id="email"
          name="email"
          placeholder="email@example.com"
          className={`form-control ${data?.errors?.email ? "is-invalid" : "is-valid"}`}
          defaultValue={profileData.email}
          required
          aria-describedby="validationEmailFeedback"
        />
        <div id="validationEmailFeedback" className="invalid-feedback">
          {data?.errors?.email}
        </div>
        <div className="valid-feedback"></div>

        <label htmlFor="email">E-mail</label>
      </div>

      <div className="d-flex  justify-content-center">
        <button type="submit" className="btn btn-primary">
          {!sending ? "Submit" : "Submitting..."}
        </button>
      </div>
    </form>
  );
};

UpdateProfile.propTypes = {
  queryKey: PropTypes.array,
  setIsUpdating: PropTypes.func,
  profileData: PropTypes.shape({
    username: PropTypes.string,
    about: PropTypes.string,
    email: PropTypes.string,
  }),
};

export default UpdateProfile;
