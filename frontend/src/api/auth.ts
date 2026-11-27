import apiClient from "./client";
import type { LoginCredentials, StaffUser } from "../types/auth";

export const loginStaff = async (
  credentials: LoginCredentials
): Promise<StaffUser> => {
  const response = await apiClient.post("/auth/login/", credentials);
  return response.data;
};

export const getCurrentStaff = async (): Promise<StaffUser> => {
  const response = await apiClient.get("/auth/me/");
  return response.data;
};

export const logoutStaff = async (): Promise<void> => {
  await apiClient.post("/auth/logout/");
};