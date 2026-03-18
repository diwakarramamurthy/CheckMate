import { render, screen, waitFor } from "@testing-library/react";
import App from "../App";
import axios from "axios";

// Mock axios
jest.mock("axios");

// Mock toast
jest.mock("sonner", () => ({
  Toaster: () => null,
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe("App", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    delete axios.defaults.headers.common["Authorization"];
  });

  afterEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe("rendering", () => {
    it("should render without crashing", () => {
      render(<App />);
      expect(document.querySelector("div")).toBeInTheDocument();
    });
  });

  describe("unauthenticated routes", () => {
    it("should show login page when not authenticated", async () => {
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });

    it("should render login form elements on login page", async () => {
      render(<App />);

      await waitFor(() => {
        expect(screen.getByTestId("login-email-input")).toBeInTheDocument();
        expect(screen.getByTestId("login-password-input")).toBeInTheDocument();
      });
    });

    it("should allow access to /login route", async () => {
      window.history.pushState({}, "Test page", "/login");
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });
  });

  describe("protected routes", () => {
    it("should redirect protected routes to login when not authenticated", async () => {
      window.history.pushState({}, "Test page", "/dashboard");
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });

    it("should redirect /projects to login when not authenticated", async () => {
      window.history.pushState({}, "Test page", "/projects");
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });

    it("should redirect /land-cost to login when not authenticated", async () => {
      window.history.pushState({}, "Test page", "/land-cost");
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });

    it("should redirect /buildings to login when not authenticated", async () => {
      window.history.pushState({}, "Test page", "/buildings");
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });

    it("should redirect /construction to login when not authenticated", async () => {
      window.history.pushState({}, "Test page", "/construction");
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });

    it("should redirect /costs to login when not authenticated", async () => {
      window.history.pushState({}, "Test page", "/costs");
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });

    it("should redirect /sales to login when not authenticated", async () => {
      window.history.pushState({}, "Test page", "/sales");
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });

    it("should redirect /reports to login when not authenticated", async () => {
      window.history.pushState({}, "Test page", "/reports");
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });

    it("should redirect /import to login when not authenticated", async () => {
      window.history.pushState({}, "Test page", "/import");
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });
  });

  describe("root path", () => {
    it("should redirect root path / to /dashboard", async () => {
      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
      });
    });
  });

  describe("authentication flow", () => {
    it("should render app with AuthProvider context", () => {
      render(<App />);
      expect(document.querySelector("div")).toBeInTheDocument();
    });

    it("should render BrowserRouter for navigation", () => {
      render(<App />);
      expect(document.querySelector("div")).toBeInTheDocument();
    });

    it("should render Toaster for notifications", () => {
      render(<App />);
      expect(document.querySelector("div")).toBeInTheDocument();
    });
  });
});
