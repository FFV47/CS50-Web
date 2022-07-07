import { useEffect, useRef } from "react";

const useControlledTextarea = (text) => {
  const formEl = useRef(null);

  useEffect(() => {
    formEl.current.selectionStart = formEl.current.selectionEnd = text.length;
    formEl.current.focus();
  }, []);

  useEffect(() => {
    formEl.current.style.height = "inherit";
    formEl.current.style.height = `${formEl.current.scrollHeight}px`;
  });

  return formEl;
};

export default useControlledTextarea;
