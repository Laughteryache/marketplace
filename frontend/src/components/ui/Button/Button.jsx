import cn from "classnames";

import Text from "@ui/Text";

import "./Button.scss";

const Button = ({
  className,
  children,
  view = "normal",
  size = "medium",
  color = "blue",
  loading = false,
  disabled = false,
  ...props
}) => {
  return (
    <button
      className={cn(
        className,
        "button",
        disabled && "button_disabled",
        `button_size_${size}`,
        `button_color_${color}`
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <Text tag="span" view="button" color="grey" weight="normal">
          Загрузка...
        </Text>
      )}
      <Text
        tag="span"
        view="button"
        color={color === "blue" ? "white" : "blue"}
        weight="normal"
      >
        {children}
      </Text>
    </button>
  );
};

export default Button;
