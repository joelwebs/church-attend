export interface Member {
  id: string;
  membership_number: string | null;
  first_name: string;
  last_name: string;
  other_names: string;
  full_name: string;
  phone_number: string;
  email: string;
  date_joined: string;
  is_active: boolean;
  is_deleted: boolean;
  deleted_at: string | null;
  deleted_by: number | null;
  created_by: number | null;
  updated_by: number | null;
  created_at: string;
  updated_at: string;
}

export interface MemberFormData {
  membership_number?: string;
  first_name: string;
  last_name: string;
  other_names?: string;
  phone_number?: string;
  email?: string;
  date_joined?: string;
  is_active?: boolean;
}

export interface PaginatedMembers {
  count: number;
  next: string | null;
  previous: string | null;
  results: Member[];
}
