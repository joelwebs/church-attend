
import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Loader2 } from "lucide-react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "success" | "outline" | "ghost";
  size?: "small" | "medium" | "large";
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  children: ReactNode;
}

export default function Button({
  variant = "primary",
  size = "medium",
  loading = false,
  leftIcon,
  rightIcon,
  children,
  disabled,
  className = "",
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`app-button button-${variant} button-${size} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="button-spinner" size={18} />
      ) : (
        leftIcon
      )}

      <span>{loading ? "Please wait..." : children}</span>

      {!loading && rightIcon}
    </button>
  );
}
