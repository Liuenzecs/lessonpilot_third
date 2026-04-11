export interface AuthUser {
  id: string;
  email: string;
  name: string;
  email_verified: boolean;
  email_verified_at: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload extends LoginPayload {
  name: string;
}

export interface ForgotPasswordPayload {
  email: string;
}

export interface ResetPasswordPayload {
  token: string;
  password: string;
  confirm_password: string;
}

export interface VerifyEmailPayload {
  token: string;
}

export interface MessageResponse {
  message: string;
}
