import axios from "axios";
const baseUrl = "http://127.0.0.1:8765";

export const ping = async () => {
  const pingUrl = `${baseUrl}/v1/api/ping`;
  try {
    const response = await axios.get(pingUrl);
    console.log(response.data);
    return response.data;
  } catch (e) {
    throw error.response?.data?.detail;
  }
};

class Service {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }
}

class EntityService extends Service {
  constructor(baseUrl, entityType) {
    super(baseUrl);
    this.entityType = entityType;
  }

  async register(email, password) {
    const regUrl = `${this.baseUrl}/v1/api/${this.entityType}/auth/sign-up`;
    try {
      const response = await axios.post(regUrl, { email, password });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail;
    }
  }

  async login(email, password) {
    const loginUrl = `${this.baseUrl}/v1/api/${this.entityType}/auth/sign-in`;
    try {
      const response = await axios.post(loginUrl, { email, password });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail;
    }
  }
}

export class UserService extends EntityService {
  constructor(baseUrl) {
    super(baseUrl);
  }
}

export class BusinessService extends EntityService {
  constructor(baseUrl) {
    super(baseUrl);
  }
}

export const userService = new UserService(baseUrl);
