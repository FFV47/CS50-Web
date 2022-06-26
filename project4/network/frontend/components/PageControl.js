import PropTypes from "prop-types";
import React from "react";
import { Link } from "react-router-dom";
import { GrCaretNext } from "react-icons/gr";
import useGlobalContext from "../context/GlobalContext";

const PageControl = ({ postsQuery }) => {
  const { urlPage } = useGlobalContext();

  const { isPreviousData, data } = postsQuery;
  const numPages = data?.numPages ? data.numPages : 1;

  const pages = [...Array(numPages).keys()].map((i) => i + 1);

  const isNextEnabled = !isPreviousData && data?.nextPage ? null : "disabled";
  const isPreviousDisabled =
    urlPage === 1 || (data?.previousPage && isPreviousData) ? "disabled" : null;

  return (
    <nav aria-label="page navigation" className="mt-3">
      <ul className="pagination justify-content-center">
        <li className={`page-item ${isPreviousDisabled}`}>
          {isPreviousDisabled === "disabled" ? (
            <span className="page-link" aria-label="Previous disabled">
              <GrCaretNext
                aria-hidden="true"
                className={`previous ${isPreviousDisabled}`}
              />
            </span>
          ) : (
            <Link to={`/${data?.previousPage}`} className="page-link">
              <GrCaretNext
                aria-hidden="true"
                className={`previous ${isPreviousDisabled}`}
              />
            </Link>
          )}
        </li>

        {pages.map((page) => {
          return (
            <li key={page} className={`page-item ${page === urlPage ? "active" : null}`}>
              <Link to={`/${page}`} className="page-link">
                {page}
              </Link>
            </li>
          );
        })}

        <li className={`page-item ${isNextEnabled}`}>
          {isNextEnabled === null ? (
            <span className="page-link" aria-label="Next disabled">
              <GrCaretNext aria-hidden="true" className={isNextEnabled} />
            </span>
          ) : (
            <Link to={`/${data?.nextPage}`} className="page-link" aria-label="Next">
              <GrCaretNext aria-hidden="true" className={isNextEnabled} />
            </Link>
          )}
        </li>
      </ul>
    </nav>
  );
};

PageControl.propTypes = {
  postsQuery: PropTypes.object,
};

export default PageControl;
