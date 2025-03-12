import cn from "classnames";

import "./Text.scss";

const Text = ({
  className,
  children,
  tag: Tag = "p",
  view = "button",
  weight = "normal",
  color = "black",
}) => {
  return (
    <Tag
      className={cn(
        view && `text_view_${view}`,
        weight && `text_weight_${weight}`,
        color && `text_color_${color}`,
        className
      )}
    >
      {children}
    </Tag>
  );
};

export default Text;
