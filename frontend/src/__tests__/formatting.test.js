import {
  formatCurrency,
  formatIndianNumber,
  formatNumber,
} from "../utils/formatting";

describe("formatting utilities", () => {
  describe("formatCurrency", () => {
    it("should format a currency amount with Indian rupee symbol", () => {
      const result = formatCurrency(1000);
      expect(result).toMatch(/[\d,₹]/);
      expect(result).toContain("1,000");
    });

    it("should handle zero correctly", () => {
      const result = formatCurrency(0);
      expect(result).toMatch(/[\d,₹]/);
      expect(result).toContain("0");
    });

    it("should handle null gracefully", () => {
      const result = formatCurrency(null);
      expect(result).toEqual("₹0");
    });

    it("should handle undefined gracefully", () => {
      const result = formatCurrency(undefined);
      expect(result).toEqual("₹0");
    });

    it("should format large numbers with commas", () => {
      const result = formatCurrency(1000000);
      expect(result).toContain("10,00,000");
    });

    it("should not include decimal places by default", () => {
      const result = formatCurrency(1000.5);
      expect(result).not.toMatch(/\.\d/);
    });
  });

  describe("formatIndianNumber", () => {
    it("should format numbers with Indian style separators", () => {
      const result = formatIndianNumber(1000000);
      expect(result).toContain("10,00,000");
    });

    it("should handle zero correctly", () => {
      const result = formatIndianNumber(0);
      expect(result).toEqual("0");
    });

    it("should handle null gracefully", () => {
      const result = formatIndianNumber(null);
      expect(result).toEqual("0");
    });

    it("should handle undefined gracefully", () => {
      const result = formatIndianNumber(undefined);
      expect(result).toEqual("0");
    });

    it("should format smaller numbers without Indian separators", () => {
      const result = formatIndianNumber(999);
      expect(result).toEqual("999");
    });

    it("should format 1000 correctly", () => {
      const result = formatIndianNumber(1000);
      expect(result).toContain("1,000");
    });
  });

  describe("formatNumber", () => {
    it("should format a number with specified decimal places", () => {
      const result = formatNumber(3.14159, 2);
      expect(result).toEqual("3.14");
    });

    it("should default to 2 decimal places", () => {
      const result = formatNumber(123.456);
      expect(result).toContain("123.46");
    });

    it("should handle zero correctly", () => {
      const result = formatNumber(0, 2);
      expect(result).toEqual("0");
    });

    it("should handle null gracefully", () => {
      const result = formatNumber(null, 2);
      expect(result).toEqual("0");
    });

    it("should handle undefined gracefully", () => {
      const result = formatNumber(undefined, 2);
      expect(result).toEqual("0");
    });

    it("should handle 0 decimal places", () => {
      const result = formatNumber(123.456, 0);
      expect(result).toContain("123");
    });

    it("should apply Indian number formatting", () => {
      const result = formatNumber(1000000, 2);
      expect(result).toContain("10,00,000");
    });
  });
});
