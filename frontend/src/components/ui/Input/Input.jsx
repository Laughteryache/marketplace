import cn from "classnames";

import Text from "@ui/Text";
import "./Input.scss";

const Input = ({ label, type, placeholder, name, id, className, ...props }) => {
  return (
    <div className="input_field">
      <Text weight="medium" tag="label" htmlFor={label} view="label">
        {label}
      </Text>
      <input
        id={id}
        type={type}
        className={cn("input_form", className)}
        name={name}
        placeholder={placeholder}
      ></input>
    </div>
  );
};

export default Input;
