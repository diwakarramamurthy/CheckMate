import { renderHook, act, waitFor } from "@testing-library/react";
import { AuthProvider, useAuth } from "../context/AuthContext";
import axios from "axios";

jest.mock("axios");

describe("AuthContext", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    delete axios.defaults.headers.common["Authorization"];
  });

  afterEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe("useAuth hook", () => {
    it("should return authentication state from context", () => {
      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      expect(result.current).toHaveProperty("user");
      expect(result.current).toHaveProperty("token");
      expect(result.current).toHaveProperty("loading");
      expect(result.current).toHaveProperty("login");
      expect(result.current).toHaveProperty("register");
      expect(result.current).toHaveProperty("logout");
    });

    it("should initialize with null user and no token", () => {
      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
    });

    it("should initialize loading state as true", () => {
      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      expect(result.current.loading).toBe(true);
    });
  });

  describe("AuthProvider", () => {
    it("should provide auth context to children", () => {
      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      expect(result.current).toBeDefined();
      expect(result.current).not.toBeNull();
    });

    it("should set loading to false when no token exists", async () => {
      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
    });
  });

  describe("login function", () => {
    it("should call the correct API endpoint with credentials", async () => {
      const mockResponse = {
        data: {
          access_token: "test_token",
          user: { id: 1, email: "test@example.com" },
        },
      };
      axios.post.mockResolvedValueOnce(mockResponse);

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      await act(async () => {
        await result.current.login("test@example.com", "password123");
      });

      expect(axios.post).toHaveBeenCalledWith(expect.stringContaining("auth/login"), {
        email: "test@example.com",
        password: "password123",
      });
    });

    it("should set user and token on successful login", async () => {
      const mockUser = { id: 1, email: "test@example.com", name: "Test User" };
      const mockResponse = {
        data: {
          access_token: "test_token_123",
          user: mockUser,
        },
      };
      axios.post.mockResolvedValueOnce(mockResponse);

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      await act(async () => {
        await result.current.login("test@example.com", "password123");
      });

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser);
        expect(result.current.token).toEqual("test_token_123");
      });
    });

    it("should store token in localStorage on successful login", async () => {
      const mockResponse = {
        data: {
          access_token: "test_token_123",
          user: { id: 1, email: "test@example.com" },
        },
      };
      axios.post.mockResolvedValueOnce(mockResponse);

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      await act(async () => {
        await result.current.login("test@example.com", "password123");
      });

      await waitFor(() => {
        expect(localStorage.getItem("rera_token")).toEqual("test_token_123");
      });
    });

    it("should set Authorization header on successful login", async () => {
      const mockResponse = {
        data: {
          access_token: "test_token_123",
          user: { id: 1, email: "test@example.com" },
        },
      };
      axios.post.mockResolvedValueOnce(mockResponse);

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      await act(async () => {
        await result.current.login("test@example.com", "password123");
      });

      await waitFor(() => {
        expect(axios.defaults.headers.common["Authorization"]).toEqual(
          "Bearer test_token_123"
        );
      });
    });

    it("should return user on successful login", async () => {
      const mockUser = { id: 1, email: "test@example.com", name: "Test User" };
      const mockResponse = {
        data: {
          access_token: "test_token_123",
          user: mockUser,
        },
      };
      axios.post.mockResolvedValueOnce(mockResponse);

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      let returnedUser;
      await act(async () => {
        returnedUser = await result.current.login("test@example.com", "password123");
      });

      expect(returnedUser).toEqual(mockUser);
    });
  });

  describe("logout function", () => {
    it("should clear user and token on logout", async () => {
      const mockResponse = {
        data: {
          access_token: "test_token",
          user: { id: 1, email: "test@example.com" },
        },
      };
      axios.post.mockResolvedValueOnce(mockResponse);

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      await act(async () => {
        await result.current.login("test@example.com", "password123");
      });

      await waitFor(() => {
        expect(result.current.user).not.toBeNull();
      });

      act(() => {
        result.current.logout();
      });

      await waitFor(() => {
        expect(result.current.user).toBeNull();
        expect(result.current.token).toBeNull();
      });
    });

    it("should remove token from localStorage on logout", async () => {
      const mockResponse = {
        data: {
          access_token: "test_token",
          user: { id: 1, email: "test@example.com" },
        },
      };
      axios.post.mockResolvedValueOnce(mockResponse);

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      await act(async () => {
        await result.current.login("test@example.com", "password123");
      });

      expect(localStorage.getItem("rera_token")).toBeTruthy();

      act(() => {
        result.current.logout();
      });

      expect(localStorage.getItem("rera_token")).toBeNull();
    });

    it("should remove Authorization header on logout", async () => {
      const mockResponse = {
        data: {
          access_token: "test_token",
          user: { id: 1, email: "test@example.com" },
        },
      };
      axios.post.mockResolvedValueOnce(mockResponse);

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      await act(async () => {
        await result.current.login("test@example.com", "password123");
      });

      act(() => {
        result.current.logout();
      });

      await waitFor(() => {
        expect(axios.defaults.headers.common["Authorization"]).toBeUndefined();
      });
    });
  });

  describe("register function", () => {
    it("should call the correct API endpoint with registration data", async () => {
      const mockResponse = {
        data: {
          access_token: "test_token",
          user: { id: 1, email: "test@example.com" },
        },
      };
      axios.post.mockResolvedValueOnce(mockResponse);

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      const registerData = {
        email: "test@example.com",
        password: "password123",
        name: "Test User",
        role: "developer",
      };

      await act(async () => {
        await result.current.register(registerData);
      });

      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining("auth/register"),
        registerData
      );
    });

    it("should set user and token on successful registration", async () => {
      const mockUser = { id: 1, email: "test@example.com", name: "Test User" };
      const mockResponse = {
        data: {
          access_token: "test_token_123",
          user: mockUser,
        },
      };
      axios.post.mockResolvedValueOnce(mockResponse);

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
      const { result } = renderHook(() => useAuth(), { wrapper });

      await act(async () => {
        await result.current.register({
          email: "test@example.com",
          password: "password123",
          name: "Test User",
          role: "developer",
        });
      });

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser);
        expect(result.current.token).toEqual("test_token_123");
      });
    });
  });
});
