<<<<<<< HEAD
import "./App.css";

function App() {
  return <div></div>;
}
=======
import Header from "@components/Header";
import Modal from "@components/Modal";
import { ping } from "@src/api";
import { useEffect, useState } from "react";

const App = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchPing = async () => {
      try {
        const response = await ping();
        setData(response.uptime);
      } catch (e) {
        console.error(error);
      }
    };
    fetchPing();
  }, []);

  return (
    <>
      <Header></Header>
      <Modal />
      <h1>{data ? data : "Загрузка..."}</h1>
    </>
  );
};
>>>>>>> frontend-dev

export default App;
