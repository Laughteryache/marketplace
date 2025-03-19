import axios from "axios";
const BASE_URL = "http://127.0.0.1:8765";

export const registerUser = async (email, password) => {
  const REG_URL = `${BASE_URL}/v1/api/user/auth/sign-up`;
  try {
    const response = await axios.post(REG_URL, { email, password });
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail;
  }
};
