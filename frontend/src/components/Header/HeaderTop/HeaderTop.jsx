import { useState } from "react";

import Login from "@assets/login.svg?react";
import Heart from "@assets/heart.svg?react";
import Box from "@assets/box.svg?react";
import Text from "@ui/Text";
import MenuButton from "@ui/MenuButton";
import Modal from "@components/Modal";

import "./HeaderTop.scss";

const HeaderTop = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="header_top">
      <Text tag="h1" view="title" color="blue" weight="bold" className="title">
        MarketPlace
      </Text>
      <div className="header_menu">
        <MenuButton logo={Login} handleClick={() => setIsOpen(true)}>
          Войти
        </MenuButton>
        <MenuButton logo={Heart}>Избранное</MenuButton>
        <MenuButton logo={Box}>Заказы</MenuButton>
      </div>
    </div>
  );
};

export default HeaderTop;
