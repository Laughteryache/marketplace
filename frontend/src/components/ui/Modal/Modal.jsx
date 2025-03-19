import { createPortal } from "react-dom";

import "./Modal.scss";

const Modal = ({ isOpen, onClose, children }) => {

  if (!isOpen) return null;

  return createPortal(
    <div className="modal">
      <div className="modal_content">
        <button className="modal_button_close" onClick={onClose}>
          &times
        </button>

        {children}
      </div>
      <div className="modal_overlay" onClick={onClose}></div>
    </div>,
    document.body
  );
};

export default Modal;
