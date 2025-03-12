import cn from "classnames";

import Text from "@ui/Text";

import "./Button.scss";

const Button = ({
  className,
  children,
  loading = false,
  disabled = false,
  ...props
}) => {
  return (
    <button
      className={cn(className, "button", disabled && "button_disabled")}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <Text tag="span" view="button" color="grey" weight="normal">
          Загрузка...
        </Text>
      )}
      <Text tag="span" view="button" color="white" weight="normal">
        {children}
      </Text>
    </button>
  );
};

export default Button;
