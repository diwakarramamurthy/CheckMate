import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import LoginPage from "../pages/LoginPage";
import * as AuthContext from "../context/AuthContext";

// Mock the toast notifications
jest.mock("sonner", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Mock axios globally
jest.mock("axios");

describe("LoginPage", () => {
  const mockLogin = jest.fn();
  const mockRegister = jest.fn();
  const mockNavigate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    // Mock useAuth hook
    jest.spyOn(AuthContext, "useAuth").mockReturnValue({
      user: null,
      token: null,
      loading: false,
      login: mockLogin,
      register: mockRegister,
      logout: jest.fn(),
    });

    // Mock useNavigate
    jest.spyOn(require("react-router-dom"), "useNavigate").mockReturnValue(mockNavigate);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  const renderLoginPage = () => {
    return render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
  };

  describe("rendering", () => {
    it("should render without crashing", () => {
      renderLoginPage();
      expect(screen.getByText("Welcome back")).toBeInTheDocument();
    });

    it("should render email input field", () => {
      renderLoginPage();
      const emailInput = screen.getByTestId("login-email-input");
      expect(emailInput).toBeInTheDocument();
      expect(emailInput).toHaveAttribute("type", "email");
    });

    it("should render password input field", () => {
      renderLoginPage();
      const passwordInput = screen.getByTestId("login-password-input");
      expect(passwordInput).toBeInTheDocument();
      expect(passwordInput).toHaveAttribute("type", "password");
    });

    it("should render login button", () => {
      renderLoginPage();
      const submitButton = screen.getByTestId("login-submit-btn");
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toHaveTextContent("Sign In");
    });

    it("should render toggle authentication mode button", () => {
      renderLoginPage();
      const toggleButton = screen.getByTestId("toggle-auth-mode");
      expect(toggleButton).toBeInTheDocument();
      expect(toggleButton).toHaveTextContent("Don't have an account");
    });
  });

  describe("form submission - login mode", () => {
    it("should call login function when form is submitted", async () => {
      mockLogin.mockResolvedValueOnce({ id: 1, email: "test@example.com" });
      renderLoginPage();

      const emailInput = screen.getByTestId("login-email-input");
      const passwordInput = screen.getByTestId("login-password-input");
      const submitButton = screen.getByTestId("login-submit-btn");

      await userEvent.type(emailInput, "test@example.com");
      await userEvent.type(passwordInput, "password123");
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password123");
      });
    });

    it("should navigate to dashboard on successful login", async () => {
      mockLogin.mockResolvedValueOnce({ id: 1, email: "test@example.com" });
      renderLoginPage();

      const emailInput = screen.getByTestId("login-email-input");
      const passwordInput = screen.getByTestId("login-password-input");
      const submitButton = screen.getByTestId("login-submit-btn");

      await userEvent.type(emailInput, "test@example.com");
      await userEvent.type(passwordInput, "password123");
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
      });
    });

    it("should disable button while loading", async () => {
      mockLogin.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ id: 1, email: "test@example.com" }), 100)
          )
      );
      renderLoginPage();

      const emailInput = screen.getByTestId("login-email-input");
      const passwordInput = screen.getByTestId("login-password-input");
      const submitButton = screen.getByTestId("login-submit-btn");

      await userEvent.type(emailInput, "test@example.com");
      await userEvent.type(passwordInput, "password123");
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(submitButton).toBeDisabled();
      });
    });
  });

  describe("form submission - register mode", () => {
    it("should switch to registration mode when toggle button is clicked", async () => {
      renderLoginPage();
      const toggleButton = screen.getByTestId("toggle-auth-mode");

      await userEvent.click(toggleButton);

      await waitFor(() => {
        expect(screen.getByText("Create Account")).toBeInTheDocument();
      });
    });

    it("should show name and role inputs in registration mode", async () => {
      renderLoginPage();
      const toggleButton = screen.getByTestId("toggle-auth-mode");

      await userEvent.click(toggleButton);

      await waitFor(() => {
        expect(screen.getByTestId("register-name-input")).toBeInTheDocument();
        expect(screen.getByTestId("register-role-select")).toBeInTheDocument();
      });
    });

    it("should call register function on form submission in register mode", async () => {
      mockRegister.mockResolvedValueOnce({ id: 1, email: "test@example.com" });
      renderLoginPage();

      const toggleButton = screen.getByTestId("toggle-auth-mode");
      await userEvent.click(toggleButton);

      await waitFor(() => {
        expect(screen.getByTestId("register-name-input")).toBeInTheDocument();
      });

      const nameInput = screen.getByTestId("register-name-input");
      const emailInput = screen.getByTestId("login-email-input");
      const passwordInput = screen.getByTestId("login-password-input");
      const submitButton = screen.getByTestId("login-submit-btn");

      await userEvent.type(nameInput, "Test User");
      await userEvent.type(emailInput, "test@example.com");
      await userEvent.type(passwordInput, "password123");
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith(
          expect.objectContaining({
            email: "test@example.com",
            password: "password123",
            name: "Test User",
          })
        );
      });
    });
  });

  describe("error handling", () => {
    it("should show error message on failed login", async () => {
      const { toast } = require("sonner");
      mockLogin.mockRejectedValueOnce({
        response: { data: { detail: "Invalid credentials" } },
      });
      renderLoginPage();

      const emailInput = screen.getByTestId("login-email-input");
      const passwordInput = screen.getByTestId("login-password-input");
      const submitButton = screen.getByTestId("login-submit-btn");

      await userEvent.type(emailInput, "test@example.com");
      await userEvent.type(passwordInput, "wrongpassword");
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith("Invalid credentials");
      });
    });

    it("should show generic error message when error detail is missing", async () => {
      const { toast } = require("sonner");
      mockLogin.mockRejectedValueOnce({ response: { data: {} } });
      renderLoginPage();

      const emailInput = screen.getByTestId("login-email-input");
      const passwordInput = screen.getByTestId("login-password-input");
      const submitButton = screen.getByTestId("login-submit-btn");

      await userEvent.type(emailInput, "test@example.com");
      await userEvent.type(passwordInput, "password123");
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith("Authentication failed");
      });
    });

    it("should reset loading state after error", async () => {
      mockLogin.mockRejectedValueOnce({
        response: { data: { detail: "Invalid credentials" } },
      });
      renderLoginPage();

      const emailInput = screen.getByTestId("login-email-input");
      const passwordInput = screen.getByTestId("login-password-input");
      const submitButton = screen.getByTestId("login-submit-btn");

      await userEvent.type(emailInput, "test@example.com");
      await userEvent.type(passwordInput, "password123");
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(submitButton).not.toBeDisabled();
      });
    });
  });

  describe("user input", () => {
    it("should update email input value", async () => {
      renderLoginPage();
      const emailInput = screen.getByTestId("login-email-input");

      await userEvent.type(emailInput, "test@example.com");

      expect(emailInput).toHaveValue("test@example.com");
    });

    it("should update password input value", async () => {
      renderLoginPage();
      const passwordInput = screen.getByTestId("login-password-input");

      await userEvent.type(passwordInput, "password123");

      expect(passwordInput).toHaveValue("password123");
    });
  });

  describe("navigation on authenticated user", () => {
    it("should navigate to dashboard if user is already authenticated", () => {
      jest.spyOn(AuthContext, "useAuth").mockReturnValue({
        user: { id: 1, email: "test@example.com" },
        token: "test_token",
        loading: false,
        login: mockLogin,
        register: mockRegister,
        logout: jest.fn(),
      });

      renderLoginPage();

      expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
    });
  });
});
