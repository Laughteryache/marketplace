import { useActionState } from "react";

import Input from "@ui/Input";
import Text from "@ui/Text";
import Button from "@ui/Button";
import { registerUser } from "@src/api";
import "./AuthForm.scss";

const AuthForm = () => {
  const [state, submitAction] = useActionState(auth, {
    data: null,
    error: null,
  });

  async function auth(prevState, formData) {
    const email = formData.get("email");
    const password = formData.get("password");

    try {
      const response = await registerUser({ email, password });
      return { data: response, error: null };
    } catch (e) {
      return { ...prevState, error: e.message };
    }
  }

  return (
    <form action={submitAction} className="auth">
      <div style={{ display: "flex", flexDirection: "column", gap: "25px" }}>
        <Input
          label="Почта"
          type="email"
          placeholder="Почта"
          name="email"
          id="email"
        ></Input>
        <Input
          label="Пароль"
          type="password"
          placeholder="Пароль"
          name="password"
          id="password"
        ></Input>
      </div>
      <Button type="submit" size="medium">
        Войти
      </Button>
      {state.data && <p>{state.data.email} registered</p>}
      {state.error && <p>{state.error}</p>}
    </form>
  );
};

export default AuthForm;
