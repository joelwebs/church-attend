export interface StaffUser {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  role: "pastor" | "media_team";
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthContextType {
  user: StaffUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}