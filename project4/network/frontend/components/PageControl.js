import React, { useEffect, useState, useRef } from "react";
import PropTypes from "prop-types";

import { useNavigate } from "react-router-dom";

const PageControl = ({ urlPage, isPreviousData, nextPage }) => {
  const [page, setPage] = useState(urlPage);
  const navigate = useNavigate();

  // The only difference between useRef() and creating a {current:
  // ...} object yourself is that useRef will give you the same ref
  // object on every render.
  const pageButtonClicked = useRef(false);

  useEffect(() => {
    // Block navigate until the first click
    if (pageButtonClicked.current) {
      navigate(`/${page}`);
    }
  }, [page]);

  return (
    <div className="page-control">
      <p>Current Page: {page}</p>
      <button
        onClick={() => {
          setPage((old) => Math.max(old - 1, 1));
          pageButtonClicked.current = true;
        }}
        disabled={page === 1}
      >
        Previous Page
      </button>

      <button
        onClick={() => {
          if (!isPreviousData && nextPage) {
            setPage((old) => old + 1);
            pageButtonClicked.current = true;
          }
        }}
        // Disable the Next Page button until we know a next page is available
        disabled={isPreviousData || !nextPage}
      >
        Next Page
      </button>
    </div>
  );
};

PageControl.propTypes = {
  urlPage: PropTypes.number,
  isPreviousData: PropTypes.bool,
  nextPage: PropTypes.number,
};

export default PageControl;
