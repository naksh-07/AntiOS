import React from "react";

export interface ButtonProps {
  label: string;
  onClick?: () => void;
  variant?: "primary" | "secondary";
}

export const Button: React.FC<ButtonProps> = ({ label, onClick, variant = "primary" }) => {
  const base = "px-4 py-2 rounded font-medium transition-colors";
  const styling = variant === "primary"
    ? "bg-brand-500 text-white hover:bg-brand-900"
    : "bg-gray-200 text-gray-800 hover:bg-gray-300";

  return (
    <button className={`${base} ${styling}`} onClick={onClick}>
      {label}
    </button>
  );
};
