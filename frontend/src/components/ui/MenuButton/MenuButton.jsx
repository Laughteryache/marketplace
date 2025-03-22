import Text from "@ui/Text";
import "./MenuButton.scss";

const MenuButton = ({
  logo: Logo,
  children,
  classname,
  handleClick,
  ...props
}) => {
  return (
    <div className="btn_menu" onClick={handleClick} {...props}>
      {Logo && <Logo className="btn_logo" />}
      {children && <Text className="btn_text">{children}</Text>}
    </div>
  );
};

export default MenuButton;
