import Text from "@ui/Text";

const HeaderTop = () => {
  console.log("HeaderTop is rendering");

  return (
    <div className="header_top">
      <Text tag="h1" view="title" color="blue" weight="bold" className="title">
        MarketPlace
      </Text>
      <div className="log_menu"></div>
    </div>
  );
};

export default HeaderTop;
