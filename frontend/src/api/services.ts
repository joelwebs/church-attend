
import apiClient from "./client";

import type {
  ChurchService,
  ServiceFormData,
  PaginatedServices,
  GeneratedQRCode,
} from "../types/service";

export async function getServices(
  search = "",
  page = 1
): Promise<PaginatedServices> {
  const response = await apiClient.get<PaginatedServices>("/services/", {
    params: {
      search: search || undefined,
      page,
    },
  });

  return response.data;
}

export async function getService(id: string): Promise<ChurchService> {
  const response = await apiClient.get<ChurchService>(
    `/services/${id}/`
  );

  return response.data;
}

export async function createService(
  data: ServiceFormData
): Promise<ChurchService> {
  const response = await apiClient.post<ChurchService>(
    "/services/",
    data
  );

  return response.data;
}

export async function updateService(
  id: string,
  data: Partial<ServiceFormData>
): Promise<ChurchService> {
  const response = await apiClient.patch<ChurchService>(
    `/services/${id}/`,
    data
  );

  return response.data;
}

export async function openService(id: string): Promise<void> {
  await apiClient.post(`/services/${id}/open/`);
}

export async function closeService(id: string): Promise<void> {
  await apiClient.post(`/services/${id}/close/`);
}

export async function cancelService(id: string): Promise<void> {
  await apiClient.post(`/services/${id}/cancel/`);
}

export async function generateServiceQR(
  id: string
): Promise<GeneratedQRCode> {
  const response = await apiClient.post<GeneratedQRCode>(
    `/services/${id}/generate_qr/`
  );

  return response.data;
}

export async function revokeServiceQR(id: string): Promise<void> {
  await apiClient.post(`/services/${id}/revoke_qr/`);
}
