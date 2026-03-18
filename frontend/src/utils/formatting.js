import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";

// Format currency helper
export const formatCurrency = (amount) => {
  if (!amount && amount !== 0) return "₹0";
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
};

// Format number with Indian lakh/crore separators
export const formatIndianNumber = (num) => {
  if (!num && num !== 0) return "0";
  return new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: 0
  }).format(num);
};

// Format number helper
export const formatNumber = (num, decimals = 2) => {
  if (!num && num !== 0) return "0";
  return new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: decimals
  }).format(num);
};

// Currency Input Component with Indian formatting
export const CurrencyInput = ({ value, onChange, disabled, className, placeholder }) => {
  const [displayValue, setDisplayValue] = useState("");

  useEffect(() => {
    if (value || value === 0) {
      setDisplayValue(formatIndianNumber(value));
    } else {
      setDisplayValue("");
    }
  }, [value]);

  const handleChange = (e) => {
    const input = e.target.value;
    // Remove all non-digit characters
    const numericValue = input.replace(/[^0-9]/g, "");

    if (numericValue === "") {
      setDisplayValue("");
      onChange(0);
    } else {
      const num = parseInt(numericValue, 10);
      setDisplayValue(formatIndianNumber(num));
      onChange(num);
    }
  };

  const handleFocus = (e) => {
    // Select all text on focus for easy editing
    e.target.select();
  };

  return (
    <Input
      type="text"
      value={displayValue}
      onChange={handleChange}
      onFocus={handleFocus}
      disabled={disabled}
      className={className}
      placeholder={placeholder || "0"}
    />
  );
};
