import { parseISO } from "date-fns";

const getDate = (ISOstring) => {
  // remove timezone info
  return parseISO(ISOstring.slice(0, -1));
};

export default getDate;
