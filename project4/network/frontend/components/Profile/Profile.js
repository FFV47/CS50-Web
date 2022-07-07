import { useState } from "react";
import { VscAccount } from "react-icons/vsc";
import { ImSpinner5 } from "react-icons/im";
import { CSSTransition } from "react-transition-group";

import useDataContext from "../../context/DataContext";
import UpdateProfile from "./UpdateProfile";

import useFollow from "../../hooks/useFollow";
import useProfile from "../../hooks/useProfile";
import useToggle from "../../hooks/useToggle";
import useToast from "../../hooks/useToast";

import Feed from "../Feed/Feed";

import { formatDistanceToNow, parseISO } from "date-fns";

const Profile = () => {
  const { loggedUser, authenticated, queryKey } = useDataContext();

  const { isLoading, isFetching, isError, data, error, isPreviousData } =
    useProfile(queryKey);

  const followMutation = useFollow(queryKey);

  const [isUpdating, setIsUpdating] = useToggle();
  const [showAbout, setShowAbout] = useState(true);

  const showToast = useToast();

  const capitalize = (string) => {
    return string.charAt(0).toUpperCase() + string.slice(1);
  };

  if (!authenticated) {
    window.location.replace("/login");
    return;
  }

  return (
    <>
      {(!isLoading && !isError && isFetching) || isLoading ? (
        <div className="center mb-3 mt-3">
          <ImSpinner5 aria-hidden="true" className="loading-spinner" />
        </div>
      ) : (
        ""
      )}

      {!isLoading && isError && (
        <p className="alert alert-danger" role="alert">
          {error.message}
        </p>
      )}

      {!isLoading && !isError && (
        <>
          <header className="profile-header">
            <h1>{`${capitalize(data.username)}'s profile`}</h1>
            {data.username !== loggedUser && (
              <button
                type="button"
                className={`btn btn-sm rounded-pill ${
                  data.isFollowing ? "btn-primary" : "btn-outline-primary"
                }`}
                onClick={() =>
                  followMutation.mutate(
                    {
                      username: data.username,
                    },
                    {
                      onSuccess: (data) => {
                        showToast("followToast", data.message);
                      },
                    }
                  )
                }
              >
                {data.isFollowing ? "Unfollow" : "Follow"}
              </button>
            )}
          </header>
          <div className="card round-card shadow mt-3">
            <div className="card-body">
              <header>
                <div className="d-flex align-items-center justify-content-between mb-3">
                  <div className="d-flex align-items-center">
                    {data.photo ? (
                      <img
                        src={data.photo}
                        alt="profile-photo"
                        className="img-fluid profile-photo"
                      />
                    ) : (
                      <VscAccount style={{ width: "3em", height: "3em" }} />
                    )}

                    <p className="card-title h4 fw-bold mb-0 ms-3">Info</p>

                    <div className="ms-5">
                      <p className="mb-0">
                        Joined: {formatDistanceToNow(parseISO(data.dateJoined))} ago
                      </p>
                      <p className="mb-0">
                        Last seen: {formatDistanceToNow(parseISO(data.lastLogin))} ago
                      </p>
                    </div>
                  </div>
                  <button className="btn btn-outline-primary" onClick={setIsUpdating}>
                    {!isUpdating ? "Update Profile" : "Cancel"}
                  </button>
                </div>
              </header>

              {showAbout && (
                <>
                  <p className="card-text">About me: {data.about}</p>
                  <p className="card-text">E-mail: {data.email}</p>
                </>
              )}

              <CSSTransition
                in={isUpdating}
                timeout={400}
                unmountOnExit
                classNames="default-transition-group"
                onEnter={() => setShowAbout(false)}
                onExited={() => setShowAbout(true)}
              >
                <UpdateProfile
                  queryKey={queryKey}
                  setIsUpdating={setIsUpdating}
                  profileData={{
                    username: data.username,
                    about: data.about,
                    email: data.email,
                  }}
                />
              </CSSTransition>
            </div>

            <ul className="list-group list-group-flush">
              <li className="list-group-item">Followers: {data.followersCount}</li>
              <li className="list-group-item">Following: {data.followingCount}</li>
            </ul>
          </div>
          {data?.postsData.posts.length ? (
            <Feed
              isLoading={isLoading}
              isFetching={isFetching}
              isError={isError}
              data={data.postsData}
              error={error}
              isPreviousData={isPreviousData}
              hasParentSpin={true}
            />
          ) : (
            <p className="h3 text-center mt-5">No posts to show</p>
          )}
        </>
      )}
    </>
  );
};

export default Profile;
