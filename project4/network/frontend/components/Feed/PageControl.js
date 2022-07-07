import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { GrCaretNext } from "react-icons/gr";
import useDataContext from "../../context/DataContext";

const PageControl = ({ isPreviousData, data }) => {
  const { urlPage } = useDataContext();
  // Fix duplicate characters for optional url parameters -> "/1" and
  // "" matches the same path in react router
  const path = window.location.pathname.replace(/\/\d?$/, "");

  const numPages = data?.numPages ? data.numPages : 1;

  const pages = [...Array(numPages).keys()].map((i) => i + 1);

  const isNextDisabled = !isPreviousData || data?.nextPage ? "disabled" : null;
  const isPreviousDisabled =
    urlPage === 1 || (data?.previousPage && isPreviousData) ? "disabled" : null;

  return (
    <nav aria-label="page navigation" className="mt-5">
      <ul className="pagination justify-content-center">
        {/* Previous Button */}
        <li className={`page-item ${isPreviousDisabled}`}>
          {isPreviousDisabled === "disabled" ? (
            <span className="page-link" aria-label="Previous disabled">
              <GrCaretNext
                aria-hidden="true"
                className={`previous ${isPreviousDisabled}`}
              />
            </span>
          ) : (
            <Link to={`${path}/${data?.previousPage}`} className="page-link">
              <GrCaretNext
                aria-hidden="true"
                className={`previous ${isPreviousDisabled}`}
              />
            </Link>
          )}
        </li>

        {/* Pages */}
        {pages.map((page) => {
          return (
            <li key={page} className={`page-item ${page === urlPage ? "active" : null}`}>
              <Link to={`${path}/${page}`} className="page-link">
                {page}
              </Link>
            </li>
          );
        })}

        {/* Next Button */}
        <li className={`page-item ${isNextDisabled}`}>
          {isNextDisabled === "disabled" ? (
            <span className="page-link" aria-label="Next disabled">
              <GrCaretNext aria-hidden="true" className={isNextDisabled} />
            </span>
          ) : (
            <Link
              to={`${path}/${data?.nextPage}`}
              className="page-link"
              aria-label="Next"
            >
              <GrCaretNext aria-hidden="true" className={isNextDisabled} />
            </Link>
          )}
        </li>
      </ul>
    </nav>
  );
};

PageControl.propTypes = {
  baseUrl: PropTypes.string,
  isPreviousData: PropTypes.bool,
  data: PropTypes.object,
};

export default PageControl;
