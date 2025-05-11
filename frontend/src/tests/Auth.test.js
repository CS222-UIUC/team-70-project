// src/tests/auth.test.js
const axios = require("axios");
const MockAdapter = require("axios-mock-adapter");

describe("Auth API (Django Allauth)", () => {
  let mock;

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.restore();
  });

  it("should sign up a new user", async () => {
    mock.onPost("/auth/registration/").reply(201, {
      email: "test@example.com",
    });

    const res = await axios.post("/auth/registration/", {
      email: "test@example.com",
      password1: "SecurePass123!",
      password2: "SecurePass123!",
    });

    expect(res.status).toBe(201);
    expect(res.data.email).toBe("test@example.com");
  });

  it("should fail sign up if passwords do not match", async () => {
    mock.onPost("/auth/registration/").reply(400, {
      password2: ["The two password fields didn’t match."],
    });

    try {
      await axios.post("/auth/registration/", {
        email: "test@example.com",
        password1: "SecurePass123!",
        password2: "WrongPass123!",
      });
    } catch (err) {
      expect(err.response.status).toBe(400);
      expect(err.response.data.password2[0]).toMatch(
        /didn’t match/i
      );
    }
  });
  it("should fail sign up if email already exists", async () => {
    mock.onPost("/auth/registration/").reply(400, {
      email: ["A user is already registered with this email address."],
    });

    try {
      await axios.post("/auth/registration/", {
        email: "test@example.com",
        password1: "SecurePass123!",
        password2: "SecurePass123!",
      });
    } catch (err) {
      expect(err.response.status).toBe(400);
      expect(err.response.data.email[0]).toMatch(/already registered/i);
    }
  });

  it("should log in an existing user", async () => {
    mock.onPost("/auth/login/").reply(200, {
      email: "test@example.com",
    });

    const res = await axios.post("/auth/login/", {
      email: "test@example.com",
      password: "SecurePass123!",
    });

    expect(res.status).toBe(200);
    expect(res.data.email).toBe("test@example.com");
  });

  it("should fail login with wrong password", async () => {
    mock.onPost("/auth/login/").reply(400, {
      non_field_errors: ["Unable to log in with provided credentials."],
    });

    try {
      await axios.post("/auth/login/", {
        email: "test@example.com",
        password: "WrongPass123!",
      });
    } catch (err) {
      expect(err.response.status).toBe(400);
      expect(err.response.data.non_field_errors[0]).toMatch(
        /unable to log in/i
      );
    }
  });

  it("should log out the user", async () => {
    // stub the logout endpoint
    mock.onPost("/auth/logout/").reply(200);
    // stub the subsequent user-fetch to return empty
    mock.onGet("/auth/user/").reply(200, {});

    await axios.post("/auth/logout/");
    const res = await axios.get("/auth/user/");

    expect(res.status).toBe(200);
    expect(res.data).toEqual({});
  });
  it("should fetch 401 when getting user if not authenticated", async () => {
    mock.onGet("/auth/user/").reply(401, {
      detail: "Authentication credentials were not provided.",
    });

    try {
      await axios.get("/auth/user/");
    } catch (err) {
      expect(err.response.status).toBe(401);
      expect(err.response.data.detail).toMatch(/not provided/i);
    }
  });

  it("should persist session after login", async () => {
    // stub login
    mock.onPost("/auth/login/").reply(200, { email: "test@example.com" });
    // stub user-fetch
    mock.onGet("/auth/user/").reply(200, { email: "test@example.com" });

    await axios.post("/auth/login/", {
      email: "test@example.com",
      password: "SecurePass123!",
    });
    const res = await axios.get("/auth/user/");

    expect(res.data.email).toBe("test@example.com");
  });

  it("should include CSRF token on POST", async () => {
    // stub CSRF-get to send back a cookie header
    mock.onGet("/auth/csrf/").reply(200, {}, { "set-cookie": ["csrftoken=abc"] });

    const res = await axios.get("/auth/csrf/");
    expect(res.headers["set-cookie"]).toBeDefined();
    expect(res.headers["set-cookie"][0]).toMatch(/csrftoken=/);
  });

  it("should return user data if authenticated", async () => {
    mock.onGet("/auth/user/").reply(200, { email: "test@example.com" });

    const res = await axios.get("/auth/user/");
    expect(res.status).toBe(200);
    expect(res.data.email).toBe("test@example.com");
  });
});
