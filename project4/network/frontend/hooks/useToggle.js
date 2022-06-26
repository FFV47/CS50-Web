import React from "react";

const useToggle = () => {
  const [state, setState] = React.useState(false);

  const toggle = React.useCallback(() => setState((state) => !state), []);

  return [state, toggle];
};

export default useToggle;
