
export type ServiceStatus =
  | "scheduled"
  | "open"
  | "closed"
  | "cancelled";

export interface ChurchService {
  id: string;
  name: string;
  date: string;
  start_time: string;
  end_time: string;
  venue: string;
  attendance_start: string;
  attendance_end: string;
  status: ServiceStatus;
  created_by: number | null;
  created_at: string;
  updated_at: string;
}

export interface ServiceFormData {
  name: string;
  date: string;
  start_time: string;
  end_time: string;
  venue: string;
  attendance_start: string;
  attendance_end: string;
}

export interface PaginatedServices {
  count: number;
  next: string | null;
  previous: string | null;
  results: ChurchService[];
}

export interface GeneratedQRCode {
  message: string;
  service_id: string;
  qr_token_id: string;
  qr_code: string;
  expires_at: string;
}
