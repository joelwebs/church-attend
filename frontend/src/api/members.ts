import apiClient from "./client";
import type {
  Member,
  MemberFormData,
  PaginatedMembers,
} from "../types/member";

export async function getMembers(
  search = "",
  page = 1
): Promise<PaginatedMembers> {
  const response = await apiClient.get<PaginatedMembers>("/members/", {
    params: {
      search,
      page,
    },
  });

  return response.data;
}

export async function getArchivedMembers(
  search = "",
  page = 1
): Promise<PaginatedMembers> {
  const response = await apiClient.get<PaginatedMembers>(
    "/members/archived/",
    {
      params: {
        search,
        page,
      },
    }
  );

  return response.data;
}

export async function getMember(id: string): Promise<Member> {
  const response = await apiClient.get<Member>(`/members/${id}/`);
  return response.data;
}

export async function createMember(
  data: MemberFormData
): Promise<Member> {
  const response = await apiClient.post<Member>("/members/", data);
  return response.data;
}

export async function updateMember(
  id: string,
  data: Partial<MemberFormData>
): Promise<Member> {
  const response = await apiClient.patch<Member>(
    `/members/${id}/`,
    data
  );

  return response.data;
}

export async function deleteMember(id: string): Promise<void> {
  await apiClient.delete(`/members/${id}/`);
}

export async function restoreMember(id: string): Promise<void> {
  await apiClient.post(`/members/${id}/restore/`);
}

export async function activateMember(id: string): Promise<void> {
  await apiClient.post(`/members/${id}/activate/`);
}

export async function deactivateMember(id: string): Promise<void> {
  await apiClient.post(`/members/${id}/deactivate/`);
}
