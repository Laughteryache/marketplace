import { createPortal } from "react-dom";
import { useRef, useEffect } from "react";

import "./Modal.scss";

const Modal = ({ children, isOpened }) => {
  const dialog = useRef();

  useEffect(() => {
    if (isOpened) {
      dialog.current.showModal();
    } else {
      dialog.current.close();
    }
  }, [isOpened]);

  return createPortal(
    <dialog ref={dialog}>{children}</dialog>,
    document.getElementById("modal")
  );
};

export default Modal;
